"""
Tests for OAuth 2.0 Authorization Code + PKCE endpoints.

Covers:
- GET  /oauth/authorize/  — parameter validation and form rendering
- POST /oauth/authorize/  — credential validation and auth code issuance
- POST /oauth/token/      — authorization_code and refresh_token grants
- POST /oauth/token/revoke/ — RFC 7009 revocation
"""

import base64
import hashlib
import secrets

import pytest
from django.urls import reverse
from rest_framework import status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pkce_pair():
    """Return (code_verifier, code_challenge) using S256."""
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _authorize_params(client, challenge, state="test-state"):
    return {
        "response_type": "code",
        "client_id": str(client.client_id),
        "redirect_uri": client.get_redirect_uris()[0],
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }


# ---------------------------------------------------------------------------
# Authorization endpoint — GET
# ---------------------------------------------------------------------------

class TestAuthorizeGet:

    @pytest.mark.django_db
    def test_renders_login_form(self, django_client, oauth_client):
        """Valid parameters → 200 with login form HTML."""
        _, challenge = _pkce_pair()
        params = _authorize_params(oauth_client, challenge)
        url = reverse("oauth_authorize") + "?" + "&".join(f"{k}={v}" for k, v in params.items())

        response = django_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert b"Sign in" in response.content
        assert oauth_client.name.encode() in response.content

    @pytest.mark.django_db
    def test_unknown_client_id_returns_400(self, django_client, oauth_client):
        """Unknown client_id must not redirect — must return 400."""
        _, challenge = _pkce_pair()
        url = (
            reverse("oauth_authorize")
            + f"?response_type=code&client_id=00000000-0000-0000-0000-000000000000"
            f"&redirect_uri=https://example.com/callback"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        response = django_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_unregistered_redirect_uri_returns_400(self, django_client, oauth_client):
        """redirect_uri not in client allowlist must return 400 (RFC 6749 §4.1.2.1)."""
        _, challenge = _pkce_pair()
        url = (
            reverse("oauth_authorize")
            + f"?response_type=code&client_id={oauth_client.client_id}"
            f"&redirect_uri=https://evil.example.com/callback"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        response = django_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_missing_code_challenge_redirects_error(self, django_client, oauth_client):
        """Missing code_challenge → redirect with error=invalid_request."""
        redirect_uri = oauth_client.get_redirect_uris()[0]
        url = (
            reverse("oauth_authorize")
            + f"?response_type=code&client_id={oauth_client.client_id}"
            f"&redirect_uri={redirect_uri}&state=s1"
        )
        response = django_client.get(url)
        assert response.status_code == 302
        assert "error=invalid_request" in response["Location"]

    @pytest.mark.django_db
    def test_unsupported_response_type_redirects_error(self, django_client, oauth_client):
        """response_type=token → redirect with error=unsupported_response_type."""
        _, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]
        url = (
            reverse("oauth_authorize")
            + f"?response_type=token&client_id={oauth_client.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        response = django_client.get(url)
        assert response.status_code == 302
        assert "error=unsupported_response_type" in response["Location"]


# ---------------------------------------------------------------------------
# Authorization endpoint — POST
# ---------------------------------------------------------------------------

class TestAuthorizePost:

    @pytest.mark.django_db
    def test_valid_credentials_redirect_with_code(self, django_client, oauth_client, user):
        """Valid credentials → 302 to redirect_uri with code and state params."""
        verifier, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]

        response = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "xyz",
                "username": user.username,
                "password": "testpass123",
            },
        )

        assert response.status_code == 302
        location = response["Location"]
        assert location.startswith(redirect_uri)
        assert "code=" in location
        assert "state=xyz" in location

    @pytest.mark.django_db
    def test_invalid_password_rerenders_form(self, django_client, oauth_client, user):
        """Wrong password → re-render form with error, no redirect."""
        _, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]

        response = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "xyz",
                "username": user.username,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 200
        assert b"Invalid username or password" in response.content

    @pytest.mark.django_db
    def test_state_preserved_in_redirect(self, django_client, oauth_client, user):
        """State parameter must be forwarded unchanged to the redirect URI."""
        _, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]
        original_state = "some-opaque-state-value"

        response = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": original_state,
                "username": user.username,
                "password": "testpass123",
            },
        )

        assert response.status_code == 302
        assert f"state={original_state}" in response["Location"]


# ---------------------------------------------------------------------------
# Token endpoint — authorization_code grant
# ---------------------------------------------------------------------------

class TestTokenAuthorizationCode:

    def _get_auth_code(self, django_client, oauth_client, user, challenge):
        """Helper: complete the authorize POST and return the issued code string."""
        redirect_uri = oauth_client.get_redirect_uris()[0]
        response = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "s",
                "username": user.username,
                "password": "testpass123",
            },
        )
        assert response.status_code == 302
        location = response["Location"]
        code = dict(p.split("=") for p in location.split("?")[1].split("&"))["code"]
        return code

    @pytest.mark.django_db
    def test_happy_path_returns_tokens(self, django_client, api_client, oauth_client, user):
        """Valid code + verifier → RFC 6749 §5.1 JSON with access and refresh tokens."""
        verifier, challenge = _pkce_pair()
        code = self._get_auth_code(django_client, oauth_client, user, challenge)
        redirect_uri = oauth_client.get_redirect_uris()[0]

        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": redirect_uri,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        assert "expires_in" in data
        assert "refresh_token" in data
        assert data["scope"] == ""

    @pytest.mark.django_db
    def test_code_reuse_returns_invalid_grant(self, django_client, api_client, oauth_client, user):
        """Reusing a code → invalid_grant (single-use enforcement)."""
        verifier, challenge = _pkce_pair()
        code = self._get_auth_code(django_client, oauth_client, user, challenge)
        redirect_uri = oauth_client.get_redirect_uris()[0]

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": redirect_uri,
            "client_id": str(oauth_client.client_id),
            "client_secret": oauth_client._raw_secret,
        }
        r1 = api_client.post(reverse("oauth_token"), data=payload, format="multipart")
        assert r1.status_code == 200

        r2 = api_client.post(reverse("oauth_token"), data=payload, format="multipart")
        assert r2.status_code == 400
        assert r2.json()["error"] == "invalid_grant"

    @pytest.mark.django_db
    def test_wrong_pkce_verifier_returns_invalid_grant(self, django_client, api_client, oauth_client, user):
        """Wrong code_verifier → invalid_grant."""
        _, challenge = _pkce_pair()
        code = self._get_auth_code(django_client, oauth_client, user, challenge)
        redirect_uri = oauth_client.get_redirect_uris()[0]

        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": "this-is-the-wrong-verifier",
                "redirect_uri": redirect_uri,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert response.json()["error"] == "invalid_grant"

    @pytest.mark.django_db
    def test_expired_code_returns_invalid_grant(self, api_client, oauth_client, user):
        """Expired authorization code → invalid_grant."""
        from django.utils import timezone
        from datetime import timedelta
        from authentication.models import AuthorizationCode

        _, challenge = _pkce_pair()
        auth_code = AuthorizationCode.objects.create(
            code=AuthorizationCode.generate_code(),
            client=oauth_client,
            user=user,
            redirect_uri=oauth_client.get_redirect_uris()[0],
            code_challenge=challenge,
            code_challenge_method="S256",
            expires_at=timezone.now() - timedelta(seconds=1),  # already expired
        )

        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": auth_code.code,
                "code_verifier": "any",
                "redirect_uri": oauth_client.get_redirect_uris()[0],
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert response.json()["error"] == "invalid_grant"

    @pytest.mark.django_db
    def test_invalid_client_secret_returns_401(self, api_client, oauth_client):
        """Wrong client_secret → invalid_client HTTP 401."""
        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": "irrelevant",
                "code_verifier": "irrelevant",
                "redirect_uri": oauth_client.get_redirect_uris()[0],
                "client_id": str(oauth_client.client_id),
                "client_secret": "wrong-secret",
            },
            format="multipart",
        )

        assert response.status_code == 401
        assert response.json()["error"] == "invalid_client"

    @pytest.mark.django_db
    def test_unsupported_grant_type_returns_error(self, api_client, oauth_client):
        """Unknown grant_type → unsupported_grant_type."""
        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "implicit",
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert response.json()["error"] == "unsupported_grant_type"


# ---------------------------------------------------------------------------
# Token endpoint — refresh_token grant
# ---------------------------------------------------------------------------

class TestTokenRefresh:

    def _get_tokens(self, django_client, api_client, oauth_client, user):
        """Complete the full auth code flow and return the token response JSON."""
        verifier, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]

        r1 = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "s",
                "username": user.username,
                "password": "testpass123",
            },
        )
        location = r1["Location"]
        code = dict(p.split("=") for p in location.split("?")[1].split("&"))["code"]

        r2 = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": redirect_uri,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )
        return r2.json()

    @pytest.mark.django_db
    def test_refresh_returns_new_access_token(self, django_client, api_client, oauth_client, user):
        """Valid refresh_token → new access token issued."""
        tokens = self._get_tokens(django_client, api_client, oauth_client, user)

        response = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"


# ---------------------------------------------------------------------------
# Revocation endpoint
# ---------------------------------------------------------------------------

class TestRevoke:

    def _get_refresh_token(self, django_client, api_client, oauth_client, user):
        verifier, challenge = _pkce_pair()
        redirect_uri = oauth_client.get_redirect_uris()[0]

        r1 = django_client.post(
            reverse("oauth_authorize"),
            data={
                "response_type": "code",
                "client_id": str(oauth_client.client_id),
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": "s",
                "username": user.username,
                "password": "testpass123",
            },
        )
        location = r1["Location"]
        code = dict(p.split("=") for p in location.split("?")[1].split("&"))["code"]

        r2 = api_client.post(
            reverse("oauth_token"),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": redirect_uri,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )
        return r2.json()["refresh_token"]

    @pytest.mark.django_db
    def test_revoke_valid_token_returns_200(self, django_client, api_client, oauth_client, user):
        """Revoking a valid refresh token → HTTP 200."""
        refresh_token = self._get_refresh_token(django_client, api_client, oauth_client, user)

        response = api_client.post(
            reverse("oauth_revoke"),
            data={
                "token": refresh_token,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_revoke_already_revoked_token_returns_200(self, django_client, api_client, oauth_client, user):
        """RFC 7009: revoking an already-invalid token still returns 200."""
        refresh_token = self._get_refresh_token(django_client, api_client, oauth_client, user)

        # First revocation
        api_client.post(
            reverse("oauth_revoke"),
            data={
                "token": refresh_token,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        # Second revocation of the same token
        response = api_client.post(
            reverse("oauth_revoke"),
            data={
                "token": refresh_token,
                "client_id": str(oauth_client.client_id),
                "client_secret": oauth_client._raw_secret,
            },
            format="multipart",
        )

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_revoke_invalid_client_returns_401(self, api_client, oauth_client):
        """Wrong client_secret → invalid_client HTTP 401 even on revoke."""
        response = api_client.post(
            reverse("oauth_revoke"),
            data={
                "token": "any",
                "client_id": str(oauth_client.client_id),
                "client_secret": "wrong",
            },
            format="multipart",
        )

        assert response.status_code == 401
