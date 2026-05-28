from __future__ import annotations

from typing import Any, Optional

import jwt
from django.conf import settings
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token

from .jwt_keys import jwk_from_public_key_pem

class TokenBackendWithHeaders:
    """
    Minimal token backend variant that allows injecting JOSE headers (e.g. kid).

    SimpleJWT does not support arbitrary headers in v5.3.0, so we encode directly
    via PyJWT with the same settings SimpleJWT uses (aud/iss/signing key/algorithm).
    """

    @staticmethod
    def encode(payload: dict[str, Any], *, headers: Optional[dict[str, Any]] = None) -> str:
        jwt_payload = payload.copy()

        # Keep SimpleJWT's behavior of optionally including aud/iss in the payload.
        if api_settings.AUDIENCE is not None:
            jwt_payload["aud"] = api_settings.AUDIENCE
        if api_settings.ISSUER is not None:
            jwt_payload["iss"] = api_settings.ISSUER

        token = jwt.encode(
            jwt_payload,
            api_settings.SIGNING_KEY,
            algorithm=api_settings.ALGORITHM,
            headers=headers or None,
        )
        if isinstance(token, bytes):  # pragma: no cover (PyJWT legacy)
            return token.decode("utf-8")
        return token


class HeadersTokenMixin:
    headers: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.headers = {}

    def __str__(self) -> str:
        return TokenBackendWithHeaders.encode(self.payload, headers=self.headers)


def get_jwt_kid() -> Optional[str]:
    # Set in settings from env; fallback is computed server-side for JWKS, but for
    # token header we still want a stable value when possible.
    explicit = getattr(settings, "JWT_KEY_ID", None)
    if explicit:
        return explicit

    public_pem = getattr(settings, "JWT_PUBLIC_KEY_PEM", None)
    if public_pem:
        return jwk_from_public_key_pem(public_pem).kid

    return None


class CustomAccessToken(HeadersTokenMixin, AccessToken):
    pass


class CustomRefreshToken(HeadersTokenMixin, RefreshToken):
    @property
    def access_token(self) -> Token:
        cached = getattr(self, "_cached_access_token", None)
        if cached is not None:
            return cached

        base: Token = super().access_token
        access = CustomAccessToken()
        access.payload = base.payload  # type: ignore[assignment]
        self._cached_access_token = access
        return access


def mint_refresh_for_user(user) -> CustomRefreshToken:
    refresh = CustomRefreshToken.for_user(user)

    kid = get_jwt_kid()
    if kid:
        refresh.headers["kid"] = kid
    access = refresh.access_token
    if kid:
        access.headers["kid"] = kid

    return refresh

