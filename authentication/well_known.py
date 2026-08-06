from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .jwt_keys import jwk_from_public_key_pem


def _absolute_url(request, path: str) -> str:
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}{path}"


@extend_schema(
    operation_id="jwks",
    summary="JSON Web Key Set (JWKS)",
    tags=["Authentication"],
    description=(
        "Returns the public key set used to verify JWT signatures (RFC 7517). "
        "Consumers can use this endpoint to validate `Authorization: Bearer` tokens "
        "without contacting the API on every request.\n\n"
        "Response is cached for 15 minutes (`Cache-Control: public, max-age=900`).\n\n"
        "Returns an empty key set when the API is configured with HS256 (symmetric) signing."
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="JWKSResponse",
                fields={"keys": serializers.ListField(child=serializers.DictField())},
            ),
            description="JWKS document",
        )
    },
    auth=[],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def jwks_view(request):
    public_pem = getattr(settings, "JWT_PUBLIC_KEY_PEM", None)
    if not public_pem:
        resp = Response({"keys": []})
        resp["Cache-Control"] = "public, max-age=900"
        return resp

    kid = getattr(settings, "JWT_KEY_ID", None) or None
    jwk = jwk_from_public_key_pem(public_pem, kid=kid).as_dict()

    resp = Response({"keys": [jwk]})
    resp["Cache-Control"] = "public, max-age=900"  # 15 minutes
    return resp


@extend_schema(
    operation_id="openid_configuration",
    summary="OpenID Connect Discovery Document",
    tags=["Authentication"],
    description=(
        "OpenID Connect discovery document (RFC 8414 / OpenID Connect Discovery 1.0). "
        "Returns the server's OAuth 2.0 endpoint URLs and supported capabilities. "
        "OAuth clients can use this endpoint for automatic configuration.\n\n"
        "Response is cached for 15 minutes (`Cache-Control: public, max-age=900`)."
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="OIDCConfigurationResponse",
                fields={
                    "issuer": serializers.CharField(allow_null=True),
                    "jwks_uri": serializers.CharField(),
                    "authorization_endpoint": serializers.CharField(),
                    "token_endpoint": serializers.CharField(),
                    "revocation_endpoint": serializers.CharField(),
                    "response_types_supported": serializers.ListField(child=serializers.CharField()),
                    "grant_types_supported": serializers.ListField(child=serializers.CharField()),
                    "code_challenge_methods_supported": serializers.ListField(child=serializers.CharField()),
                    "token_endpoint_auth_methods_supported": serializers.ListField(child=serializers.CharField()),
                },
            ),
            description="OIDC discovery document",
        )
    },
    auth=[],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def openid_configuration_view(request):
    issuer = getattr(settings, "JWT_ISSUER", None)

    payload = {
        "issuer": issuer,
        "jwks_uri": _absolute_url(request, "/classic-models/api/auth/.well-known/jwks.json"),
        "authorization_endpoint": _absolute_url(request, "/classic-models/api/oauth/authorize/"),
        "token_endpoint": _absolute_url(request, "/classic-models/api/oauth/token/"),
        "revocation_endpoint": _absolute_url(request, "/classic-models/api/oauth/token/revoke/"),
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
    }
    resp = Response(payload)
    resp["Cache-Control"] = "public, max-age=900"
    return resp
