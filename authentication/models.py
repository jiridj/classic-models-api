import secrets
import uuid
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def _default_expiry():
    from django.conf import settings

    seconds = getattr(settings, "OAUTH_AUTH_CODE_EXPIRY_SECONDS", 600)
    return timezone.now() + timedelta(seconds=seconds)


class OAuthClient(models.Model):
    """A registered OAuth 2.0 client (e.g. watsonx Orchestrate)."""

    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_secret_hash = models.CharField(max_length=256)
    name = models.CharField(max_length=255)
    # Newline-separated list of allowed redirect URIs.
    redirect_uris = models.TextField(
        help_text="Newline-separated list of allowed redirect URIs."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oauth_client"

    def __str__(self):
        return f"{self.name} ({self.client_id})"

    def set_secret(self, raw_secret: str) -> None:
        """Hash and store a plaintext client secret."""
        self.client_secret_hash = make_password(raw_secret)

    def verify_secret(self, raw_secret: str) -> bool:
        """Return True if raw_secret matches the stored hash."""
        return check_password(raw_secret, self.client_secret_hash)

    def get_redirect_uris(self) -> list[str]:
        """Return the list of allowed redirect URIs."""
        return [uri.strip() for uri in self.redirect_uris.splitlines() if uri.strip()]

    def is_redirect_uri_allowed(self, uri: str) -> bool:
        return uri in self.get_redirect_uris()


class AuthorizationCode(models.Model):
    """A short-lived, single-use OAuth 2.0 authorization code."""

    code = models.CharField(max_length=128, unique=True, db_index=True)
    client = models.ForeignKey(
        OAuthClient, on_delete=models.CASCADE, related_name="authorization_codes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="oauth_authorization_codes"
    )
    redirect_uri = models.TextField()
    # PKCE fields
    code_challenge = models.CharField(max_length=256)
    code_challenge_method = models.CharField(max_length=10, default="S256")
    # Lifecycle
    expires_at = models.DateTimeField(default=_default_expiry)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oauth_authorization_code"

    def __str__(self):
        return f"AuthorizationCode({self.code[:8]}…, user={self.user_id})"

    @classmethod
    def generate_code(cls) -> str:
        return secrets.token_urlsafe(32)

    def is_valid(self) -> bool:
        """Return True if the code has not been used and has not expired."""
        return not self.used and timezone.now() < self.expires_at
