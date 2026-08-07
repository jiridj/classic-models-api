# OAuth 2.0 Authentication

This guide covers the OAuth 2.0 Authorization Code + PKCE flow implemented in the Classic Models API — what it is, how to register a client, and how the flow works end to end.

> **Manual testing walkthrough**: See [OAUTH_MANUAL_TESTING.md](OAUTH_MANUAL_TESTING.md) for a step-by-step guide using only a browser and `curl`.

---

## Overview

The API acts as a standards-compliant OAuth 2.0 authorization server (IDP) implementing:

- **RFC 6749 §4.1** — Authorization Code grant
- **RFC 7636** — PKCE (Proof Key for Code Exchange)
- **RFC 7009** — Token Revocation
- **OpenID Connect Discovery** — auto-configuration endpoint

This is the recommended authentication method for third-party application integrations (e.g. watsonx Orchestrate). It preserves user identity in every access token while letting the application manage the token lifecycle without ever handling the user's password.

### Why Authorization Code + PKCE?

| Alternative | Reason not used |
|---|---|
| Resource Owner Password Credentials (ROPC) | Deprecated in OAuth 2.1; client handles credentials directly |
| Client Credentials | No user identity in tokens; breaks `/me` and per-user data scoping |
| API Key | Static credential — no expiry, no user identity, no OAuth compliance |
| **Authorization Code + PKCE** | ✅ OAuth 2.1-recommended; user authenticates once via browser popup; tokens are short-lived and rotated |

---

## Registering an OAuth Client

OAuth clients are registered server-side using the `create_oauth_client` Django management command. The plaintext client secret is printed **once only** and is not recoverable — store it immediately.

```bash
docker-compose exec api python manage.py create_oauth_client \
  "<client-name>" \
  "<redirect-uri>"
```

Example:

```bash
docker-compose exec api python manage.py create_oauth_client \
  "my-app" \
  "https://my-app.example.com/oauth/callback"
```

Output:

```
OAuth client registered successfully.

  Name:          my-app
  Client ID:     3fa85f64-5717-4562-b3fc-2c963f66afa6
  Client Secret: xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0u
  Redirect URIs: https://my-app.example.com/oauth/callback

⚠  The client secret is shown only once and cannot be recovered. Store it securely now.
```

Multiple redirect URIs are supported — pass each as a separate argument:

```bash
docker-compose exec api python manage.py create_oauth_client \
  "my-app" \
  "https://my-app.example.com/oauth/callback" \
  "https://staging.my-app.example.com/oauth/callback"
```

To remove a client:

```bash
docker-compose exec api python manage.py shell -c \
  "from authentication.models import OAuthClient; OAuthClient.objects.filter(name='my-app').delete(); print('Deleted')"
```

---

## Endpoints

All OAuth endpoints accept `application/x-www-form-urlencoded` request bodies (not JSON) and return JSON.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/classic-models/api/oauth/authorize/` | Render the user login form |
| `POST` | `/classic-models/api/oauth/authorize/` | Submit credentials; redirect to client with auth code |
| `POST` | `/classic-models/api/oauth/token/` | Exchange auth code for tokens; refresh tokens |
| `POST` | `/classic-models/api/oauth/token/revoke/` | Revoke a refresh token (RFC 7009) |
| `GET` | `/classic-models/api/auth/.well-known/openid-configuration` | OIDC discovery document |

---

## Flow

```
Client                        Browser / User              API
  │                                │                       │
  │── GET /oauth/authorize/ ───────────────────────────────▶│
  │   ?response_type=code           │                       │
  │   &client_id=<id>               │                       │  Validates client_id
  │   &redirect_uri=<uri>           │                       │  and redirect_uri
  │   &code_challenge=<S256>        │                       │
  │   &code_challenge_method=S256   │                       │
  │   &state=<random>               │                       │
  │                                 │◀── Login form ────────│
  │                                 │                       │
  │                                 │── username/password ──▶│
  │                                 │                       │  Authenticates user
  │                                 │                       │  Creates auth code (10 min, single-use)
  │◀── 302 redirect_uri ────────────│                       │
  │    ?code=<auth_code>            │                       │
  │    &state=<random>              │                       │
  │                                 │                       │
  │── POST /oauth/token/ ──────────────────────────────────▶│
  │   grant_type=authorization_code │                       │  Validates client_id + client_secret
  │   code=<auth_code>              │                       │  Validates PKCE: SHA256(verifier)==challenge
  │   code_verifier=<verifier>      │                       │  Marks code used (single-use)
  │   redirect_uri=<uri>            │                       │
  │   client_id=<id>                │                       │
  │   client_secret=<secret>        │                       │
  │                                 │                       │
  │◀── { access_token, refresh_token, expires_in } ─────────│
  │                                 │                       │
  │── GET /api/v1/... ─────────────────────────────────────▶│
  │   Authorization: Bearer <access_token>                   │
```

---

## Token Lifecycle

| Token | Lifetime | Notes |
|-------|----------|-------|
| Authorization code | 10 minutes | Single-use; expires immediately after exchange |
| Access token | 1 hour | RS256-signed JWT; validated via JWKS |
| Refresh token | 7 days | Rotated on each use; previous token is blacklisted |

**Token rotation** (`ROTATE_REFRESH_TOKENS = True`): every call to the token endpoint with `grant_type=refresh_token` issues a new refresh token and invalidates the old one. Always store the latest refresh token from each response.

---

## Refreshing and Revoking Tokens

### Refresh

```bash
curl -X POST https://<host>/classic-models/api/oauth/token/ \
  -d "grant_type=refresh_token" \
  -d "refresh_token=<REFRESH_TOKEN>" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>"
```

### Revoke

Revoking a refresh token blacklists it immediately. Per RFC 7009 §2.2 the server always returns `200` — it never reveals whether a token was valid.

```bash
curl -X POST https://<host>/classic-models/api/oauth/token/revoke/ \
  -d "token=<REFRESH_TOKEN>" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>"
```

---

## OIDC Discovery

OAuth clients that support auto-discovery read this endpoint to find all endpoint URLs without manual configuration:

```bash
curl https://<host>/classic-models/api/auth/.well-known/openid-configuration
```

```json
{
    "issuer": "https://<host>/classic-models",
    "jwks_uri": "https://<host>/classic-models/api/auth/.well-known/jwks.json",
    "authorization_endpoint": "https://<host>/classic-models/api/oauth/authorize/",
    "token_endpoint": "https://<host>/classic-models/api/oauth/token/",
    "revocation_endpoint": "https://<host>/classic-models/api/oauth/token/revoke/",
    "response_types_supported": ["code"],
    "grant_types_supported": ["authorization_code", "refresh_token"],
    "code_challenge_methods_supported": ["S256"],
    "token_endpoint_auth_methods_supported": ["client_secret_post"]
}
```

---

## watsonx Orchestrate Configuration

Once you have a registered client, configure the OAuth connection in watsonx Orchestrate:

| Field | Value |
|-------|-------|
| Grant type | Authorization Code |
| Authorization URL | `https://<host>/classic-models/api/oauth/authorize/` |
| Token URL | `https://<host>/classic-models/api/oauth/token/` |
| Client ID | (from `manage.py create_oauth_client` output) |
| Client secret | (from `manage.py create_oauth_client` output) |
| Redirect URI | (provided by watsonx Orchestrate during connection setup) |
| Scope | (leave blank) |
| PKCE | S256 |

Use the OIDC discovery URL for auto-configuration where supported:
`https://<host>/classic-models/api/auth/.well-known/openid-configuration`

---

## Error Reference

All error responses follow RFC 6749 §5.2 and use `Content-Type: application/json`.

| HTTP status | `error` value | Cause |
|-------------|---------------|-------|
| `401` | `invalid_client` | Unknown `client_id`, wrong `client_secret`, or missing credentials |
| `400` | `invalid_grant` | Expired code, reused code, wrong `code_verifier`, or invalid refresh token |
| `400` | `unsupported_grant_type` | `grant_type` is not `authorization_code` or `refresh_token` |
| `400` | `invalid_request` | Missing required parameter or unsupported `code_challenge_method` |
| `400` | (plain text) | Invalid `client_id` or unregistered `redirect_uri` on the authorize endpoint — cannot redirect per RFC 6749 §4.1.2.1 |
