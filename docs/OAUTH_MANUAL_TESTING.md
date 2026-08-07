# Testing the OAuth 2.0 Authorization Code + PKCE Flow Manually

This guide walks through testing the OAuth IDP endpoints step by step using
only a browser and `curl`. No special tooling required beyond a running API
instance.

## Prerequisites

- API running locally: `make start` or `docker-compose up -d`
- `curl` and `python3` available in your shell
- Base URL: `http://localhost:8000`

---

## Step 1 — Register an OAuth client

The `create_oauth_client` management command creates a client record and prints
its credentials. The plaintext secret is shown **once only**.

```bash
docker-compose exec api python manage.py create_oauth_client \
  "my-test-client" \
  "http://localhost:9999/callback"
```

Example output:

```
OAuth client registered successfully.

  Name:          my-test-client
  Client ID:     3fa85f64-5717-4562-b3fc-2c963f66afa6
  Client Secret: xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0u
  Redirect URIs: http://localhost:9999/callback

⚠  The client secret is shown only once and cannot be recovered. Store it securely now.
```

Export the values for use in subsequent steps:

```bash
export CLIENT_ID=3fa85f64-5717-4562-b3fc-2c963f66afa6
export CLIENT_SECRET=xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0u
export REDIRECT_URI=http://localhost:9999/callback
```

---

## Step 2 — Generate a PKCE pair

PKCE requires a random `code_verifier` and its SHA-256 base64url-encoded
`code_challenge`. Generate both with:

```bash
python3 - <<'EOF'
import base64, hashlib, secrets

verifier  = secrets.token_urlsafe(32)
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b"=").decode()

print(f"export CODE_VERIFIER={verifier}")
print(f"export CODE_CHALLENGE={challenge}")
EOF
```

Copy the two `export` lines and run them in your shell:

```bash
export CODE_VERIFIER=<output from above>
export CODE_CHALLENGE=<output from above>
```

---

## Step 3 — Open the login form in a browser

Construct the authorization URL and open it in your browser:

```
http://localhost:8000/classic-models/api/oauth/authorize/?response_type=code&client_id=<CLIENT_ID>&redirect_uri=http://localhost:9999/callback&code_challenge=<CODE_CHALLENGE>&code_challenge_method=S256&state=test-state-123
```

Or build it with a one-liner that uses your exported variables:

```bash
echo "http://localhost:8000/classic-models/api/oauth/authorize/?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256&state=test-state-123"
```

You will see the **Sign in** page:

```
┌─────────────────────────────────┐
│  Sign in                        │
│  Authorizing access for         │
│  my-test-client                 │
│                                 │
│  Username  [____________]       │
│  Password  [____________]       │
│                                 │
│  [ Sign in ]                    │
└─────────────────────────────────┘
```

Log in with the demo credentials:

| Field    | Value    |
|----------|----------|
| Username | `demo`   |
| Password | `demo123`|

After a successful login the browser redirects to:

```
http://localhost:9999/callback?code=<AUTH_CODE>&state=test-state-123
```

Nothing is listening on port 9999, so the browser will show a connection error
— that is expected. Copy the `code=` value from the browser's address bar.

```bash
export AUTH_CODE=<paste the code value here>
```

---

## Step 4 — Exchange the authorization code for tokens

Call the token endpoint server-side (back-channel). This is the step a real
OAuth client application performs after catching the redirect.

```bash
curl -s -X POST http://localhost:8000/classic-models/api/oauth/token/ \
  -d "grant_type=authorization_code" \
  -d "code=${AUTH_CODE}" \
  -d "code_verifier=${CODE_VERIFIER}" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  | python3 -m json.tool
```

Expected response (RFC 6749 §5.1):

```json
{
    "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii...",
    "scope": ""
}
```

Export the tokens:

```bash
export ACCESS_TOKEN=<access_token value>
export REFRESH_TOKEN=<refresh_token value>
```

### Error cases to try

**Wrong `code_verifier`** — tamper with the verifier to confirm PKCE enforcement:
```bash
curl -s -X POST http://localhost:8000/classic-models/api/oauth/token/ \
  -d "grant_type=authorization_code" \
  -d "code=${AUTH_CODE}" \
  -d "code_verifier=wrong-verifier" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"
# → {"error": "invalid_grant"}
```

**Wrong `client_secret`** — confirm client authentication:
```bash
curl -s -X POST http://localhost:8000/classic-models/api/oauth/token/ \
  -d "grant_type=authorization_code" \
  -d "code=${AUTH_CODE}" \
  -d "code_verifier=${CODE_VERIFIER}" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=wrong-secret"
# → HTTP 401  {"error": "invalid_client"}
```

**Reusing the code** — run the successful exchange a second time to confirm
single-use enforcement:
```bash
# (run the Step 4 curl again with the same AUTH_CODE after a successful exchange)
# → {"error": "invalid_grant"}
```

---

## Step 5 — Call a protected API endpoint

Use the access token as a Bearer token:

```bash
curl -s http://localhost:8000/classic-models/api/v1/products/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  | python3 -m json.tool | head -20
```

Expected: HTTP 200 with a list of products.

**Without a token** — confirm the endpoint rejects unauthenticated requests:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8000/classic-models/api/v1/products/
# → 401
```

---

## Step 6 — Refresh the access token

When the access token expires (1 hour), use the refresh token to obtain a new
one without the user logging in again.

```bash
curl -s -X POST http://localhost:8000/classic-models/api/oauth/token/ \
  -d "grant_type=refresh_token" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  | python3 -m json.tool
```

Expected response:

```json
{
    "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii...",
    "scope": ""
}
```

> **Note:** Token rotation is enabled (`ROTATE_REFRESH_TOKENS = True`). Each
> refresh issues a new refresh token and invalidates the previous one. Always
> use the latest refresh token.

Update your shell variable with the new tokens:

```bash
export ACCESS_TOKEN=<new access_token>
export REFRESH_TOKEN=<new refresh_token>
```

---

## Step 7 — Revoke the refresh token

Revoking a refresh token invalidates it and all future refresh attempts. This
is what a client application calls when a user explicitly disconnects.

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8000/classic-models/api/oauth/token/revoke/ \
  -d "token=${REFRESH_TOKEN}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"
# → 200
```

Confirm the revoked token is rejected:

```bash
curl -s -X POST http://localhost:8000/classic-models/api/oauth/token/ \
  -d "grant_type=refresh_token" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"
# → {"error": "invalid_grant"}
```

Revoking an already-revoked (or otherwise invalid) token also returns 200 per
RFC 7009 §2.2 — the server never reveals whether a token was valid:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8000/classic-models/api/oauth/token/revoke/ \
  -d "token=${REFRESH_TOKEN}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"
# → 200
```

---

## Step 8 — Verify the OIDC discovery document

Any OAuth client that supports auto-discovery can read this endpoint to find
all OAuth endpoint URLs automatically:

```bash
curl -s http://localhost:8000/classic-models/api/auth/.well-known/openid-configuration \
  | python3 -m json.tool
```

Expected:

```json
{
    "issuer": "...",
    "jwks_uri": "http://localhost:8000/classic-models/api/auth/.well-known/jwks.json",
    "authorization_endpoint": "http://localhost:8000/classic-models/api/oauth/authorize/",
    "token_endpoint": "http://localhost:8000/classic-models/api/oauth/token/",
    "revocation_endpoint": "http://localhost:8000/classic-models/api/oauth/token/revoke/",
    "response_types_supported": ["code"],
    "grant_types_supported": ["authorization_code", "refresh_token"],
    "code_challenge_methods_supported": ["S256"],
    "token_endpoint_auth_methods_supported": ["client_secret_post"]
}
```

---

## Cleanup

Remove the test client when you are done:

```bash
docker-compose exec api python manage.py shell -c \
  "from authentication.models import OAuthClient; OAuthClient.objects.filter(name='my-test-client').delete(); print('Deleted')"
```

---

## Quick reference

| Step | Method | URL |
|------|--------|-----|
| 1. Register client | `manage.py` | — |
| 2. Generate PKCE | `python3` | — |
| 3. Authorization form | `GET` (browser) | `/classic-models/api/oauth/authorize/` |
| 4. Token exchange | `POST` (curl) | `/classic-models/api/oauth/token/` |
| 5. Call API | `GET` (curl) | `/classic-models/api/v1/*` |
| 6. Refresh token | `POST` (curl) | `/classic-models/api/oauth/token/` |
| 7. Revoke token | `POST` (curl) | `/classic-models/api/oauth/token/revoke/` |
| 8. Discovery doc | `GET` (curl) | `/classic-models/api/auth/.well-known/openid-configuration` |

All token endpoint requests use `Content-Type: application/x-www-form-urlencoded`
(the default for `curl -d`).
