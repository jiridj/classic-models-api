"""
OAuth 2.0 Authorization Code + PKCE endpoints.

Endpoints
---------
GET  /oauth/authorize/       — render the login form
POST /oauth/authorize/       — validate credentials, issue auth code, redirect
POST /oauth/token/           — exchange auth code for tokens; refresh_token grant
POST /oauth/token/revoke/    — RFC 7009 token revocation
"""

import base64
import hashlib

from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .jwt_tokens import mint_refresh_for_user
from .models import AuthorizationCode, OAuthClient


# ---------------------------------------------------------------------------
# Inline schema helpers (used by @extend_schema only — not executed at runtime)
# ---------------------------------------------------------------------------

_TokenResponse = inline_serializer(
    name="OAuthTokenResponse",
    fields={
        "access_token": serializers.CharField(help_text="JWT access token (Bearer)"),
        "token_type": serializers.CharField(help_text='Always "Bearer"'),
        "expires_in": serializers.IntegerField(help_text="Lifetime of the access token in seconds"),
        "refresh_token": serializers.CharField(help_text="JWT refresh token"),
        "scope": serializers.CharField(help_text='Space-separated scopes granted (empty string when no scopes requested)'),
    },
)

_OAuthErrorResponse = inline_serializer(
    name="OAuthErrorResponse",
    fields={
        "error": serializers.CharField(
            help_text=(
                "RFC 6749 error code. One of: invalid_client, invalid_grant, "
                "unsupported_grant_type, invalid_request"
            )
        ),
    },
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_error(error: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": error}, status=status)


def _verify_pkce(code_verifier: str, code_challenge: str) -> bool:
    """Return True when SHA-256(code_verifier) (base64url, no padding) == code_challenge."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return computed == code_challenge


def _token_response(refresh) -> JsonResponse:
    expires_in = int(jwt_settings.ACCESS_TOKEN_LIFETIME.total_seconds())
    return JsonResponse({
        "access_token": str(refresh.access_token),
        "token_type": "Bearer",
        "expires_in": expires_in,
        "refresh_token": str(refresh),
        "scope": "",
    })


# ---------------------------------------------------------------------------
# Authorization endpoint  GET + POST /oauth/authorize/
# ---------------------------------------------------------------------------

@extend_schema(
    methods=["GET"],
    operation_id="oauth_authorize_get",
    summary="OAuth 2.0 Authorization — Show Login Form",
    tags=["OAuth 2.0"],
    description=(
        "Authorization endpoint per RFC 6749 §4.1.1 and RFC 7636 (PKCE).\n\n"
        "Validates the OAuth parameters and renders the login form for the "
        "resource owner (user) to authenticate. Errors that cannot safely redirect "
        "(unknown `client_id`, unregistered `redirect_uri`) return HTTP 400 directly "
        "per RFC 6749 §4.1.2.1."
    ),
    parameters=[
        OpenApiParameter(name="response_type", location=OpenApiParameter.QUERY, required=True,
                         description='Must be `"code"`.', type=str),
        OpenApiParameter(name="client_id", location=OpenApiParameter.QUERY, required=True,
                         description="The registered OAuth client identifier (UUID).", type=str),
        OpenApiParameter(name="redirect_uri", location=OpenApiParameter.QUERY, required=True,
                         description="Must exactly match one of the URIs registered for this client.", type=str),
        OpenApiParameter(name="code_challenge", location=OpenApiParameter.QUERY, required=True,
                         description="BASE64URL(SHA-256(code_verifier)) — PKCE challenge (RFC 7636).", type=str),
        OpenApiParameter(name="code_challenge_method", location=OpenApiParameter.QUERY, required=True,
                         description='Must be `"S256"`. Plain is not supported.', type=str),
        OpenApiParameter(name="state", location=OpenApiParameter.QUERY, required=False,
                         description="Opaque value the client uses to maintain state between request and callback.", type=str),
        OpenApiParameter(name="scope", location=OpenApiParameter.QUERY, required=False,
                         description="Space-separated list of requested scopes (optional; currently unused).", type=str),
    ],
    responses={
        200: OpenApiResponse(description="Login form HTML rendered successfully"),
        400: OpenApiResponse(description="Invalid `client_id` or `redirect_uri` — cannot redirect"),
    },
    auth=[],
)
@extend_schema(
    methods=["POST"],
    operation_id="oauth_authorize_post",
    summary="OAuth 2.0 Authorization — Submit Credentials",
    tags=["OAuth 2.0"],
    description=(
        "Processes the submitted login form credentials. On success issues a "
        "short-lived authorization code and redirects to "
        "`redirect_uri?code=<code>&state=<state>`. On invalid credentials "
        "re-renders the form with an error message.\n\n"
        "Errors that cannot safely redirect (unknown `client_id`, unregistered "
        "`redirect_uri`) return HTTP 400 directly per RFC 6749 §4.1.2.1."
    ),
    request=inline_serializer(
        name="OAuthAuthorizeRequest",
        fields={
            "response_type": serializers.CharField(help_text='Must be `"code"`.'),
            "client_id": serializers.UUIDField(help_text="Registered OAuth client identifier."),
            "redirect_uri": serializers.CharField(help_text="Must exactly match a registered redirect URI."),
            "code_challenge": serializers.CharField(help_text="BASE64URL(SHA-256(code_verifier)) — PKCE challenge."),
            "code_challenge_method": serializers.CharField(help_text='Must be `"S256"`.'),
            "state": serializers.CharField(required=False, help_text="Opaque state value echoed back in the redirect."),
            "scope": serializers.CharField(required=False, help_text="Space-separated scopes (optional; currently unused)."),
            "username": serializers.CharField(help_text="Resource owner username."),
            "password": serializers.CharField(help_text="Resource owner password."),
        },
    ),
    responses={
        302: OpenApiResponse(description="Redirect to `redirect_uri` with `code` and `state` on success, or `error` on failure"),
        200: OpenApiResponse(description="Invalid credentials — login form re-rendered with error message"),
        400: OpenApiResponse(description="Invalid `client_id` or `redirect_uri` — cannot redirect"),
    },
    auth=[],
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def authorize_view(request):
    """
    GET  — validate OAuth parameters and render the login form.
    POST — validate credentials, create an AuthorizationCode, redirect to client.
    """
    if request.method == "GET":
        return _authorize_get(request)
    return _authorize_post(request)


def _get_client_and_validate_redirect(params):
    """
    Return (client, error_str) after validating client_id and redirect_uri.
    Errors here must NOT redirect — return a plain 400 per RFC 6749 §4.1.2.1.
    """
    client_id = params.get("client_id", "").strip()
    redirect_uri = params.get("redirect_uri", "").strip()

    if not client_id or not redirect_uri:
        return None, "missing client_id or redirect_uri"

    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        return None, "unknown client_id"

    if not client.is_redirect_uri_allowed(redirect_uri):
        return None, "redirect_uri not registered for this client"

    return client, None


def _authorize_get(request):
    params = request.GET
    client, err = _get_client_and_validate_redirect(params)
    if err:
        return HttpResponseBadRequest(f"Invalid OAuth request: {err}")

    if params.get("response_type") != "code":
        from urllib.parse import urlencode
        qs = urlencode({"error": "unsupported_response_type", "state": params.get("state", "")})
        return _redirect(f"{params['redirect_uri']}?{qs}")

    if params.get("code_challenge_method", "S256") != "S256":
        from urllib.parse import urlencode
        qs = urlencode({"error": "invalid_request", "state": params.get("state", "")})
        return _redirect(f"{params['redirect_uri']}?{qs}")

    if not params.get("code_challenge"):
        from urllib.parse import urlencode
        qs = urlencode({"error": "invalid_request", "state": params.get("state", "")})
        return _redirect(f"{params['redirect_uri']}?{qs}")

    context = {
        "client_name": client.name,
        # Pass all OAuth params through the form as hidden fields.
        "oauth_params": {
            "response_type": params.get("response_type", "code"),
            "client_id": str(client.client_id),
            "redirect_uri": params.get("redirect_uri", ""),
            "scope": params.get("scope", ""),
            "state": params.get("state", ""),
            "code_challenge": params.get("code_challenge", ""),
            "code_challenge_method": params.get("code_challenge_method", "S256"),
        },
    }
    return render(request, "authentication/oauth_authorize.html", context)


def _authorize_post(request):
    params = request.POST
    client, err = _get_client_and_validate_redirect(params)
    if err:
        return HttpResponseBadRequest(f"Invalid OAuth request: {err}")

    code_challenge = params.get("code_challenge", "").strip()
    code_challenge_method = params.get("code_challenge_method", "S256").strip()
    redirect_uri = params.get("redirect_uri", "").strip()
    state = params.get("state", "")

    username = params.get("username", "").strip()
    password = params.get("password", "")

    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        context = {
            "client_name": client.name,
            "error": "Invalid username or password.",
            "oauth_params": {
                "response_type": params.get("response_type", "code"),
                "client_id": str(client.client_id),
                "redirect_uri": redirect_uri,
                "scope": params.get("scope", ""),
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
            },
        }
        return render(request, "authentication/oauth_authorize.html", context, status=200)

    code = AuthorizationCode.objects.create(
        code=AuthorizationCode.generate_code(),
        client=client,
        user=user,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    from urllib.parse import urlencode
    qs = urlencode({"code": code.code, "state": state})
    return _redirect(f"{redirect_uri}?{qs}")


def _redirect(url: str):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect(url)


# ---------------------------------------------------------------------------
# Token endpoint  POST /oauth/token/
# ---------------------------------------------------------------------------

@extend_schema(
    operation_id="oauth_token",
    summary="OAuth 2.0 Token Endpoint",
    tags=["OAuth 2.0"],
    description=(
        "Token endpoint per RFC 6749 §4.1.3 and §6. Accepts "
        "`application/x-www-form-urlencoded` bodies only (not JSON).\n\n"
        "**grant_type=authorization_code** — Exchange a short-lived authorization "
        "code (obtained from the authorization endpoint) for an access token and "
        "refresh token. Requires the PKCE `code_verifier` matching the "
        "`code_challenge` supplied during authorization.\n\n"
        "**grant_type=refresh_token** — Exchange a refresh token for a new access "
        "token. When token rotation is enabled (default) the old refresh token is "
        "blacklisted and a new one is returned.\n\n"
        "Client credentials are authenticated via `client_id` and `client_secret` "
        "form fields (`client_secret_post` method)."
    ),
    request=inline_serializer(
        name="OAuthTokenRequest",
        fields={
            "grant_type": serializers.ChoiceField(
                choices=["authorization_code", "refresh_token"],
                help_text="The OAuth 2.0 grant type.",
            ),
            "code": serializers.CharField(
                required=False,
                help_text="Authorization code received from the authorization endpoint. Required for `authorization_code` grant.",
            ),
            "code_verifier": serializers.CharField(
                required=False,
                help_text="PKCE code verifier (RFC 7636). Required for `authorization_code` grant.",
            ),
            "redirect_uri": serializers.CharField(
                required=False,
                help_text="Must match the `redirect_uri` used during authorization. Required for `authorization_code` grant.",
            ),
            "refresh_token": serializers.CharField(
                required=False,
                help_text="Refresh token to exchange. Required for `refresh_token` grant.",
            ),
            "client_id": serializers.UUIDField(help_text="Registered OAuth client identifier."),
            "client_secret": serializers.CharField(help_text="OAuth client secret."),
        },
    ),
    responses={
        200: OpenApiResponse(response=_TokenResponse, description="Token issued successfully"),
        400: OpenApiResponse(response=_OAuthErrorResponse, description="`invalid_grant` or `unsupported_grant_type`"),
        401: OpenApiResponse(response=_OAuthErrorResponse, description="`invalid_client` — bad or missing client credentials"),
    },
    auth=[],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def token_view(request):
    if request.method != "POST":
        return _json_error("method_not_allowed", status=405)

    grant_type = request.POST.get("grant_type", "")

    if grant_type == "authorization_code":
        return _grant_authorization_code(request)
    elif grant_type == "refresh_token":
        return _grant_refresh_token(request)
    else:
        return _json_error("unsupported_grant_type")


def _authenticate_client(request):
    """Return (client, error_response) from POST body client_id/client_secret."""
    client_id = request.POST.get("client_id", "").strip()
    client_secret = request.POST.get("client_secret", "")

    if not client_id or not client_secret:
        return None, _json_error("invalid_client", status=401)

    try:
        client = OAuthClient.objects.get(client_id=client_id, is_active=True)
    except OAuthClient.DoesNotExist:
        return None, _json_error("invalid_client", status=401)

    if not client.verify_secret(client_secret):
        return None, _json_error("invalid_client", status=401)

    return client, None


def _grant_authorization_code(request):
    client, err = _authenticate_client(request)
    if err:
        return err

    code_str = request.POST.get("code", "").strip()
    code_verifier = request.POST.get("code_verifier", "").strip()
    redirect_uri = request.POST.get("redirect_uri", "").strip()

    try:
        auth_code = AuthorizationCode.objects.select_related("user").get(
            code=code_str, client=client
        )
    except AuthorizationCode.DoesNotExist:
        return _json_error("invalid_grant")

    if not auth_code.is_valid():
        return _json_error("invalid_grant")

    if auth_code.redirect_uri != redirect_uri:
        return _json_error("invalid_grant")

    if not _verify_pkce(code_verifier, auth_code.code_challenge):
        return _json_error("invalid_grant")

    # Mark used before minting to prevent races.
    AuthorizationCode.objects.filter(pk=auth_code.pk).update(used=True)

    refresh = mint_refresh_for_user(auth_code.user)
    return _token_response(refresh)


def _grant_refresh_token(request):
    client, err = _authenticate_client(request)
    if err:
        return err

    raw_refresh = request.POST.get("refresh_token", "").strip()
    if not raw_refresh:
        return _json_error("invalid_grant")

    try:
        refresh = RefreshToken(raw_refresh)
    except TokenError:
        return _json_error("invalid_grant")

    # If rotation is enabled, SimpleJWT blacklists the old token when we call
    # refresh.blacklist() — but the standard rotate path is through the serializer.
    # We replicate it here: blacklist the incoming token, mint a new pair.
    try:
        if jwt_settings.ROTATE_REFRESH_TOKENS:
            if jwt_settings.BLACKLIST_AFTER_ROTATION:
                refresh.blacklist()
            # Mint a fresh pair for the same user.
            from django.contrib.auth.models import User
            user_id = refresh.payload.get(jwt_settings.USER_ID_CLAIM)
            user = User.objects.get(pk=user_id)
            new_refresh = mint_refresh_for_user(user)
            return _token_response(new_refresh)
        else:
            # No rotation — return a new access token derived from the same refresh.
            return JsonResponse({
                "access_token": str(refresh.access_token),
                "token_type": "Bearer",
                "expires_in": int(jwt_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
                "scope": "",
            })
    except Exception:
        return _json_error("invalid_grant")


# ---------------------------------------------------------------------------
# Revocation endpoint  POST /oauth/token/revoke/  (RFC 7009)
# ---------------------------------------------------------------------------

@extend_schema(
    operation_id="oauth_revoke",
    summary="OAuth 2.0 Token Revocation",
    tags=["OAuth 2.0"],
    description=(
        "Token revocation endpoint per RFC 7009. Accepts "
        "`application/x-www-form-urlencoded` bodies only.\n\n"
        "Blacklists the supplied refresh token so it can no longer be used to "
        "obtain new access tokens. Per RFC 7009 §2.2 the server always returns "
        "HTTP 200 — even if the token is already invalid or expired — to avoid "
        "leaking token validity information.\n\n"
        "Client credentials are required and authenticated via `client_secret_post`."
    ),
    request=inline_serializer(
        name="OAuthRevokeRequest",
        fields={
            "token": serializers.CharField(help_text="The refresh token to revoke."),
            "client_id": serializers.UUIDField(help_text="Registered OAuth client identifier."),
            "client_secret": serializers.CharField(help_text="OAuth client secret."),
        },
    ),
    responses={
        200: OpenApiResponse(description="Token revoked (or was already invalid). No response body."),
        401: OpenApiResponse(response=_OAuthErrorResponse, description="`invalid_client` — bad or missing client credentials"),
    },
    auth=[],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def revoke_view(request):
    if request.method != "POST":
        return _json_error("method_not_allowed", status=405)

    # Validate client — still return 200 on any token error per RFC 7009 §2.2.
    client, err = _authenticate_client(request)
    if err:
        return err

    raw_token = request.POST.get("token", "").strip()
    if raw_token:
        try:
            token = RefreshToken(raw_token)
            token.blacklist()
        except TokenError:
            pass  # Already invalid — RFC 7009 says return 200 anyway.

    return HttpResponse(status=200)
