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
    jwks_path = "/classic-models/api/auth/.well-known/jwks.json"

    payload = {
        "issuer": issuer,
        "jwks_uri": _absolute_url(request, jwks_path),
    }
    resp = Response(payload)
    resp["Cache-Control"] = "public, max-age=900"
    return resp

