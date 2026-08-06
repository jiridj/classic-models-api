from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .jwt_keys import jwk_from_public_key_pem


def _absolute_url(request, path: str) -> str:
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}{path}"


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

