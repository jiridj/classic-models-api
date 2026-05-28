# Using this API with API Connect + DataPower Nano Gateway (JWT)

This repo issues **self-managed JWTs** (login/refresh) and can also authenticate via **API key** (`X-API-Key`).

For API Connect + DataPower Nano Gateway, the gateway typically validates JWT **signature + issuer + audience** before proxying to the upstream API. This repo now supports that model by issuing **RS256** tokens and publishing a **JWKS**.

## What this API provides

- **JWT login**: `POST /classic-models/api/auth/login/`
- **JWT refresh**: `POST /classic-models/api/auth/refresh/`
- **JWKS**: `GET /classic-models/api/auth/.well-known/jwks.json`
- **OIDC discovery (minimal)**: `GET /classic-models/api/auth/.well-known/openid-configuration`

The access token is sent as:

- `Authorization: Bearer <access_token>`

Tokens include:

- **Header**: `kid`
- **Claims**: `iss`, `aud`, `exp`, `iat`, `jti`, `user_id`, `token_type`

## Configuration (this API)

Set these environment variables for RS256 + gateway-friendly validation:

- **`JWT_ISSUER`**: issuer string to place in `iss`
- **`JWT_AUDIENCE`**: audience string to place in `aud`
- **`JWT_PRIVATE_KEY_FILE`** (preferred): path to RSA private key PEM (mounted file) used to sign
- **`JWT_PUBLIC_KEY_FILE`** (preferred): path to RSA public key PEM (mounted file) used to verify + serve via JWKS
- **`JWT_PRIVATE_KEY_PEM`** (optional): RSA private key PEM provided directly via env var
- **`JWT_PUBLIC_KEY_PEM`** (optional): RSA public key PEM provided directly via env var
- **`JWT_KEY_ID`** (optional): key id to emit as JWT header `kid` and JWKS `kid`
- **`JWT_LEEWAY_SECONDS`** (optional): clock skew leeway in seconds (0 by default)

If `JWT_PRIVATE_KEY_PEM`/`JWT_PUBLIC_KEY_PEM` are not set, the app falls back to HS256 for local/dev, but gateway JWKS validation will not apply.

## API Connect / DataPower Nano Gateway configuration (high level)

In your API assembly (DataPower gateway), configure a **JWT validation** policy (commonly `jwt-validate`) to:

- **Read JWT from**: `Authorization` header (`Bearer` token)
- **Algorithm**: `RS256`
- **Issuer validation**: require `iss` to match `JWT_ISSUER`
- **Audience validation**: require `aud` to match `JWT_AUDIENCE`
- **Key material**: use the JWKS published by this API at:
  - `/classic-models/api/auth/.well-known/jwks.json`

Depending on your APIC/DataPower policy capabilities, you may either:

- Configure a validator object/policy that can fetch JWKS directly, or
- Fetch the JWKS in the assembly and pass it to the `jwt-validate` policy via a runtime variable.

## Key rotation guidance

For clean rotation without breaking existing clients:

- Keep the old public key in JWKS until all tokens signed by the old private key have expired.
- Use `kid` to distinguish keys.
- Rotate by deploying a new keypair + `JWT_KEY_ID`, then later remove the old key after token TTL passes.

