# OAuth IDP Plan — Authorization Code + PKCE for watsonx Orchestrate

## Overview

**Goal:** Make the Classic Models API a standards-compliant OAuth 2.0 IDP using the
**Authorization Code + PKCE** flow (RFC 6749 §4.1 + RFC 7636), so that watsonx Orchestrate
can connect to it as a registered OAuth client with full user identity preserved in tokens.

**Why Authorization Code + PKCE and not the alternatives:**

- **Not ROPC (password grant):** Deprecated in OAuth 2.1; ruled out.
- **Not Client Credentials:** No user identity in tokens; breaks `/me` and per-user data scoping.
- **Not API Key:** Already works with wxO today but is a static credential — no OAuth compliance,
  no expiry, no user identity in the token.
- **Authorization Code + PKCE:** The OAuth 2.1-recommended flow. watsonx Orchestrate opens a
  browser popup for the user to log in once; wxO stores the resulting access+refresh tokens and
  handles renewal automatically. User identity (`user_id`) is preserved in every JWT.

**Scope:** All existing auth endpoints (`/auth/login/`, `/auth/refresh/`, `/auth/logout/`) and
the JWT/JWKS/RS256 infrastructure remain **completely untouched**. This plan adds a new OAuth
layer on top.

**New endpoints added:**
- `GET /classic-models/api/oauth/authorize/` — shows the login form (authorization endpoint)
- `POST /classic-models/api/oauth/authorize/` — processes the login form, issues auth code
- `POST /classic-models/api/oauth/token/` — exchanges auth code for tokens; handles refresh
- `POST /classic-models/api/oauth/token/revoke/` — revokes a refresh token (RFC 7009)

**New model:** `OAuthClient` — stores registered clients (client_id + hashed secret + redirect
URI allowlist).

**Updated:** `/.well-known/openid-configuration` — enriched with `authorization_endpoint`,
`token_endpoint`, `revocation_endpoint`, and supported grant/PKCE metadata.

---

## How the Flow Works

```
1. wxO opens browser popup → GET /oauth/authorize/?response_type=code
                              &client_id=<id>&redirect_uri=<uri>
                              &code_challenge=<S256>&code_challenge_method=S256
                              &state=<random>

2. User sees Django login form, enters username + password

3. POST /oauth/authorize/ — Django validates credentials, generates a short-lived
   auth code (stored in DB), redirects to redirect_uri?code=<code>&state=<state>

4. wxO back-channel: POST /oauth/token/
   grant_type=authorization_code, code=<code>,
   code_verifier=<verifier>, client_id=<id>, redirect_uri=<uri>

5. API validates: PKCE (SHA256(verifier) == challenge), code not expired, not reused,
   client_id matches → mints access + refresh JWT via existing mint_refresh_for_user()

6. Response: { access_token, token_type, expires_in, refresh_token, scope }

7. Subsequent calls: wxO sends Authorization: Bearer <access_token>
   Renewal:          POST /oauth/token/ grant_type=refresh_token
```

---

## Sub-Tasks

---

### Sub-Task 1 — OAuthClient and AuthorizationCode models

**Intent:** Introduce two database models:
- `OAuthClient` — represents a registered OAuth client (watsonx Orchestrate). Stores `client_id`,
  hashed `client_secret`, human-readable `name`, allowed `redirect_uris`, and `is_active` flag.
- `AuthorizationCode` — a short-lived single-use record issued during the authorization step.
  Stores the PKCE `code_challenge`, the `user` who authenticated, expiry timestamp, and a `used`
  flag to enforce single-use.

Also adds a Django management command `create_oauth_client` to generate and register clients
without needing the admin UI.

**Expected Outcomes:**
- `authentication/models.py` created with both models.
- Django migration generated and applied.
- `OAuthClient.verify_secret(raw)` helper uses `django.contrib.auth.hashers.check_password`.
- `AuthorizationCode` has a `is_valid()` method checking expiry and `used` flag.
- `manage.py create_oauth_client <name> <redirect_uri>` prints `client_id` and plaintext
  `client_secret` once, then stores only the hash.

**Todo List:**
1. Create `authentication/models.py` with `OAuthClient` and `AuthorizationCode`.
2. Run `makemigrations authentication` and apply migration.
3. Create `authentication/management/__init__.py`,
   `authentication/management/commands/__init__.py`, and
   `authentication/management/commands/create_oauth_client.py`.

**Relevant Context:**
- No existing `authentication/models.py` — new file.
- Use `django.contrib.auth.hashers.make_password` / `check_password` for secret hashing
  (PBKDF2-SHA256, already available, no new dependency).
- `AuthorizationCode.code` should be a `secrets.token_urlsafe(32)` string stored as a plain
  indexed CharField (it's short-lived, ~10 minutes, single-use — hashing is not necessary here).
- Auth code lifetime: 10 minutes (configurable via `OAUTH_AUTH_CODE_EXPIRY_SECONDS` setting).

**Status:** [ ] pending

---

### Sub-Task 2 — Authorization endpoint (login UI + code issuance)

**Intent:** Implement the authorization endpoint that watsonx Orchestrate redirects users to.
A `GET` request renders a Django HTML login form. A `POST` request validates credentials, performs
PKCE parameter validation, creates an `AuthorizationCode` record, and redirects back to the
client's `redirect_uri` with `?code=<code>&state=<state>`.

**Expected Outcomes:**
- `GET /classic-models/api/oauth/authorize/` renders a login form template with PKCE and OAuth
  parameters embedded as hidden fields. Returns HTTP 400 if required parameters are missing or
  `redirect_uri` is not in the client's allowlist.
- `POST /classic-models/api/oauth/authorize/` validates username/password, creates an
  `AuthorizationCode`, and returns HTTP 302 to `redirect_uri?code=<code>&state=<state>`.
  On invalid credentials it re-renders the form with an error message.
- Error cases that cannot safely redirect (unknown `client_id`, invalid `redirect_uri`) return a
  plain HTTP 400 — never redirect with error params to an untrusted URI (RFC 6749 §4.1.2.1).
- Error cases where the redirect is safe (e.g. `response_type` unsupported) redirect with
  `?error=unsupported_response_type`.
- The form is CSRF-protected (it is a standard Django form POST from the same origin).
- `code_challenge_method` must be `S256`; plain is rejected.

**Todo List:**
1. Create `authentication/oauth_views.py` with `authorize_view`.
2. Create `authentication/templates/authentication/oauth_authorize.html` — a minimal, functional
   login form (no custom styling required; Django's built-in form rendering is fine).
3. Add `DIRS` to the `TEMPLATES` setting in `config/settings/base.py` if needed, or rely on
   `APP_DIRS: True` which already resolves `<app>/templates/`.
4. Register `GET|POST oauth/authorize/` in `authentication/urls.py`.
5. Add throttling: reuse `LoginThrottle` (50/hour per IP) on the POST handler.

**Relevant Context:**
- `authentication/serializers.py` `LoginSerializer.validate()` uses `django.contrib.auth.authenticate()`
  — reuse this logic directly (or call `authenticate()` directly in the view).
- `config/settings/base.py` `TEMPLATES` — `APP_DIRS: True` is already set; templates placed in
  `authentication/templates/authentication/` are auto-discovered.
- PKCE validation: `base64url(SHA256(code_verifier)) == code_challenge` — use `hashlib.sha256`
  and `base64.urlsafe_b64encode`. This happens in Sub-Task 3 (token endpoint), not here. The
  authorization endpoint only stores `code_challenge` and `code_challenge_method`.

**Status:** [ ] pending

---

### Sub-Task 3 — Token endpoint (authorization_code + refresh_token grants)

**Intent:** Implement the token endpoint that watsonx Orchestrate calls server-side (back-channel)
to exchange an auth code for tokens, and later to refresh an access token.

**Expected Outcomes:**
- `POST /classic-models/api/oauth/token/` accepts `application/x-www-form-urlencoded`.
- For `grant_type=authorization_code`:
  - Validates `client_id` + `client_secret` against `OAuthClient`.
  - Looks up `AuthorizationCode` by `code`; checks it is not expired and not `used`.
  - Validates PKCE: `base64url(SHA256(code_verifier)) == code_challenge` stored on the code record.
  - Validates `redirect_uri` matches what was used during the authorization request.
  - Marks the code as `used = True` (single-use enforcement).
  - Calls `mint_refresh_for_user(auth_code.user)` to produce access + refresh JWTs.
  - Returns RFC 6749 §5.1 JSON: `{ access_token, token_type: "Bearer", expires_in, refresh_token, scope: "" }`.
- For `grant_type=refresh_token`:
  - Validates `client_id` + `client_secret`.
  - Validates the refresh token via SimpleJWT's `RefreshToken(token)`.
  - Rotates and blacklists per existing `ROTATE_REFRESH_TOKENS` / `BLACKLIST_AFTER_ROTATION` settings.
  - Returns a new access token (and new refresh token if rotation is enabled).
- Error responses follow RFC 6749 §5.2:
  `{ "error": "invalid_client" | "invalid_grant" | "unsupported_grant_type" }`, HTTP 400
  (HTTP 401 for `invalid_client` per spec).
- The endpoint is exempt from CSRF (`@csrf_exempt`) — it is a machine-to-machine back-channel call.

**Todo List:**
1. Add `token_view` to `authentication/oauth_views.py`.
2. Add `OAuthTokenThrottle` to `config/throttles.py` (50/hour per IP, same pattern as
   `LoginThrottle`). Add its rate to `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` in
   `config/settings/base.py`.
3. Register `POST oauth/token/` in `authentication/urls.py`.
4. Use `SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()` for the `expires_in` value.

**Relevant Context:**
- `authentication/jwt_tokens.py` `mint_refresh_for_user()` — call this directly; it handles `kid`
  headers and RS256 signing.
- `config/settings/base.py` `SIMPLE_JWT` — `ACCESS_TOKEN_LIFETIME`, `ROTATE_REFRESH_TOKENS`,
  `BLACKLIST_AFTER_ROTATION`.
- `authentication/views.py` `logout_view` — shows the `RefreshToken(token).blacklist()` pattern
  to reuse for refresh token validation.
- **Do not** modify the existing `/auth/refresh/` endpoint.

**Status:** [ ] pending

---

### Sub-Task 4 — Token revocation endpoint (RFC 7009)

**Intent:** Allow watsonx Orchestrate to revoke a refresh token when the user disconnects the
skill connection. Maps directly to the existing token blacklist mechanism.

**Expected Outcomes:**
- `POST /classic-models/api/oauth/token/revoke/` accepts `application/x-www-form-urlencoded` with
  `token`, `client_id`, `client_secret`.
- Validates client credentials.
- Calls `RefreshToken(token).blacklist()` to invalidate the token.
- Per RFC 7009 §2.2: always returns HTTP 200 — even if the token is already invalid or expired.
  Never leak token validity information.
- CSRF exempt.

**Todo List:**
1. Add `revoke_view` to `authentication/oauth_views.py`.
2. Register `POST oauth/token/revoke/` in `authentication/urls.py`.

**Relevant Context:**
- `authentication/views.py` `logout_view` — identical blacklist logic; reuse the try/except
  `TokenError` pattern.
- RFC 7009 §2.2: "The authorization server responds with HTTP status code 200 if the token has
  been revoked successfully or if the client submitted an invalid token."

**Status:** [ ] pending

---

### Sub-Task 5 — Enrich OIDC discovery document

**Intent:** watsonx Orchestrate reads `/.well-known/openid-configuration` to auto-discover
endpoints. The current document only has `issuer` and `jwks_uri`. Adding the OAuth endpoint
fields enables full auto-configuration in wxO.

**Expected Outcomes:**
- `GET /classic-models/api/auth/.well-known/openid-configuration` now returns:
  ```json
  {
    "issuer": "...",
    "jwks_uri": "...",
    "authorization_endpoint": "https://<host>/classic-models/api/oauth/authorize/",
    "token_endpoint": "https://<host>/classic-models/api/oauth/token/",
    "revocation_endpoint": "https://<host>/classic-models/api/oauth/token/revoke/",
    "response_types_supported": ["code"],
    "grant_types_supported": ["authorization_code", "refresh_token"],
    "code_challenge_methods_supported": ["S256"],
    "token_endpoint_auth_methods_supported": ["client_secret_post"]
  }
  ```

**Todo List:**
1. Edit `openid_configuration_view` in `authentication/well_known.py` to include the new fields.
2. Use the existing `_absolute_url(request, path)` helper for all endpoint URLs.

**Relevant Context:**
- `authentication/well_known.py` — minimal edit, additive only.
- `token_endpoint_auth_methods_supported: ["client_secret_post"]` — client credentials are sent
  as form fields, not HTTP Basic Auth, matching the implementation in Sub-Task 3.

**Status:** [ ] pending

---

### Sub-Task 6 — Tests

**Intent:** Full test coverage for the OAuth flow, matching the existing test style in
`tests/test_api/`.

**Expected Outcomes:**
- `tests/test_api/test_oauth.py` covers:
  - `GET /oauth/authorize/` with valid params → 200 with form HTML.
  - `GET /oauth/authorize/` with unknown `client_id` → 400.
  - `GET /oauth/authorize/` with unregistered `redirect_uri` → 400.
  - `POST /oauth/authorize/` with valid credentials → 302 redirect with `code` param.
  - `POST /oauth/authorize/` with invalid credentials → 200 re-render with error.
  - `POST /oauth/token/` `authorization_code` grant — happy path → valid JWT response.
  - `POST /oauth/token/` `authorization_code` — expired code → `invalid_grant`.
  - `POST /oauth/token/` `authorization_code` — code reuse → `invalid_grant`.
  - `POST /oauth/token/` `authorization_code` — wrong PKCE verifier → `invalid_grant`.
  - `POST /oauth/token/` — invalid `client_secret` → `invalid_client` (HTTP 401).
  - `POST /oauth/token/` `refresh_token` grant — happy path → new access token.
  - `POST /oauth/token/revoke/` — valid refresh token → 200.
  - `POST /oauth/token/revoke/` — already-revoked token → 200 (RFC 7009).
- An `oauth_client` pytest fixture added to `tests/conftest.py`.
- All existing tests continue to pass.

**Todo List:**
1. Read `tests/conftest.py` to understand fixture patterns before writing.
2. Add `oauth_client` fixture to `tests/conftest.py`.
3. Create `tests/test_api/test_oauth.py`.

**Relevant Context:**
- `tests/test_api/test_authentication.py` — reference for auth test patterns.
- `tests/conftest.py` — add the `oauth_client` fixture here.

**Status:** [ ] pending

---

## watsonx Orchestrate Configuration Reference

Once implemented, configure the OAuth connection in watsonx Orchestrate with:

| Field | Value |
|---|---|
| **Grant type** | Authorization Code |
| **Authorization URL** | `https://<host>/classic-models/api/oauth/authorize/` |
| **Token URL** | `https://<host>/classic-models/api/oauth/token/` |
| **Client ID** | (output of `manage.py create_oauth_client`) |
| **Client secret** | (output of `manage.py create_oauth_client`) |
| **Redirect URI** | (provided by wxO during connection setup) |
| **Scope** | (leave blank) |
| **PKCE** | S256 |

OIDC discovery URL for auto-configuration:
`https://<host>/classic-models/api/auth/.well-known/openid-configuration`
