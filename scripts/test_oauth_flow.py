#!/usr/bin/env python3
"""
Local end-to-end test for the OAuth 2.0 Authorization Code + PKCE flow.

Usage:
    python3 scripts/test_oauth_flow.py

Requires the API to be running on localhost:8000 (make start / docker-compose up -d).
Creates a temporary OAuth client, runs the full flow, then cleans up.
"""

import base64
import hashlib
import http.server
import secrets
import subprocess
import threading
import urllib.parse
import sys

import requests

BASE = "http://localhost:8000/classic-models/api"
REDIRECT_URI = "http://localhost:19876/callback"
CLIENT_NAME = "oauth-local-test"
USERNAME = "demo"
PASSWORD = "demo123"

# ── PKCE ─────────────────────────────────────────────────────────────────────

def pkce_pair():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Catch the redirect with a one-shot local HTTP server ─────────────────────

_received_code = None
_server_ready = threading.Event()


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _received_code
        qs = urllib.parse.urlparse(self.path).query
        params = dict(urllib.parse.parse_qsl(qs))
        _received_code = params.get("code")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - you can close this tab")

    def log_message(self, *_):
        pass  # suppress request logs


def _start_callback_server():
    server = http.server.HTTPServer(("localhost", 19876), _CallbackHandler)
    _server_ready.set()
    server.handle_request()  # handle exactly one request then stop
    server.server_close()


# ── Register a client via management command ──────────────────────────────────

def create_client():
    print("▶  Registering OAuth client...")
    result = subprocess.run(
        [
            "docker-compose", "exec", "-T", "api",
            "python", "manage.py", "create_oauth_client",
            CLIENT_NAME, REDIRECT_URI,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

    client_id = client_secret = None
    for line in result.stdout.splitlines():
        if "Client ID:" in line:
            client_id = line.split(":", 1)[1].strip()
        if "Client Secret:" in line:
            client_secret = line.split(":", 1)[1].strip()

    if not client_id or not client_secret:
        print("Failed to parse client credentials from output:")
        print(result.stdout)
        sys.exit(1)

    print(f"   client_id:     {client_id}")
    print(f"   client_secret: {client_secret[:8]}…")
    return client_id, client_secret


def delete_client():
    """Remove the test client so the script can be re-run."""
    subprocess.run(
        [
            "docker-compose", "exec", "-T", "api",
            "python", "manage.py", "shell", "-c",
            f"from authentication.models import OAuthClient; "
            f"OAuthClient.objects.filter(name='{CLIENT_NAME}').delete()",
        ],
        capture_output=True,
    )


# ── Flow steps ────────────────────────────────────────────────────────────────

def step_authorization(client_id, verifier, challenge, state):
    print("\n▶  Starting callback listener on :19876...")
    t = threading.Thread(target=_start_callback_server, daemon=True)
    t.start()
    _server_ready.wait()

    print("▶  Posting credentials to authorization endpoint...")
    session = requests.Session()
    # GET first to obtain the CSRF token
    get_resp = session.get(
        f"{BASE}/oauth/authorize/",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
        },
        allow_redirects=False,
    )
    assert get_resp.status_code == 200, f"Authorize GET failed: {get_resp.status_code}"
    csrftoken = session.cookies.get("csrftoken", "")

    # POST credentials (simulates the user filling in the form)
    post_resp = session.post(
        f"{BASE}/oauth/authorize/",
        data={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "username": USERNAME,
            "password": PASSWORD,
            "csrfmiddlewaretoken": csrftoken,
        },
        headers={"Referer": f"{BASE}/oauth/authorize/"},
        allow_redirects=True,  # follow redirect to our local callback server
    )

    t.join(timeout=5)
    code = _received_code
    assert code, f"Did not receive auth code. Last URL: {post_resp.url}"
    print(f"   auth code:     {code[:12]}…")
    return code


def step_token_exchange(client_id, client_secret, code, verifier):
    print("\n▶  Exchanging auth code for tokens...")
    resp = requests.post(
        f"{BASE}/oauth/token/",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    assert resp.status_code == 200, f"Token exchange failed {resp.status_code}: {resp.text}"
    tokens = resp.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "Bearer"
    assert "refresh_token" in tokens
    print(f"   access_token:  {tokens['access_token'][:24]}…")
    print(f"   expires_in:    {tokens['expires_in']}s")
    print(f"   refresh_token: {tokens['refresh_token'][:24]}…")
    return tokens


def step_use_api(access_token):
    print("\n▶  Calling protected API with access token...")
    resp = requests.get(
        f"{BASE}/v1/products/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200, f"API call failed {resp.status_code}: {resp.text}"
    data = resp.json()
    count = data.get("count", len(data)) if isinstance(data, dict) else len(data)
    print(f"   ✓ Got {count} products")


def step_refresh(client_id, client_secret, refresh_token):
    print("\n▶  Refreshing access token...")
    resp = requests.post(
        f"{BASE}/oauth/token/",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    assert resp.status_code == 200, f"Refresh failed {resp.status_code}: {resp.text}"
    tokens = resp.json()
    assert "access_token" in tokens
    print(f"   new access_token: {tokens['access_token'][:24]}…")
    return tokens


def step_revoke(client_id, client_secret, refresh_token):
    print("\n▶  Revoking refresh token...")
    resp = requests.post(
        f"{BASE}/oauth/token/revoke/",
        data={
            "token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    assert resp.status_code == 200, f"Revoke failed {resp.status_code}"
    print("   ✓ Revoked")

    # Confirm the revoked token no longer works
    print("▶  Confirming revoked token is rejected...")
    resp2 = requests.post(
        f"{BASE}/oauth/token/",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    assert resp2.status_code == 400, f"Expected 400 after revocation, got {resp2.status_code}"
    assert resp2.json()["error"] == "invalid_grant"
    print("   ✓ Revoked token correctly rejected")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  OAuth 2.0 Authorization Code + PKCE — local E2E test")
    print("=" * 60)

    delete_client()  # clean up any leftover from a previous run
    client_id, client_secret = create_client()

    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(8)

    try:
        code = step_authorization(client_id, verifier, challenge, state)
        tokens = step_token_exchange(client_id, client_secret, code, verifier)
        step_use_api(tokens["access_token"])
        refreshed = step_refresh(client_id, client_secret, tokens["refresh_token"])
        step_revoke(client_id, client_secret, refreshed["refresh_token"])
    finally:
        delete_client()

    print("\n" + "=" * 60)
    print("  ✓ All steps passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
