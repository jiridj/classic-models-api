# Deployment Guide

## Overview

This application is **always** served at the `/classic-models` base path in all environments. This simplifies reverse proxy configuration and ensures consistent URLs across local development and production.

> **Note**: For local development setup, see the [Quick Start](../README.md#-quick-start) section in the main README. For Kubernetes/OpenShift deployment see [HELM_DEPLOYMENT.md](HELM_DEPLOYMENT.md). For QNAP NAS deployment, see [NAS_DEPLOYMENT.md](NAS_DEPLOYMENT.md).

## Base Path

**All URLs include `/classic-models` prefix:**
- API Documentation: `/classic-models/api/docs/`
- API Endpoints: `/classic-models/api/v1/...`
- Authentication: `/classic-models/api/auth/...`
- Admin: `/classic-models/admin/`

## Deployment Environments

### 1. Local Development (Docker Compose)

**Access**: `http://localhost:8000/classic-models`

```bash
# Start local development
make start

# Access API documentation
open http://localhost:8000/classic-models/api/docs/

# Test an endpoint
curl http://localhost:8000/classic-models/api/auth/login/
```

### 2. Production (VPS NGINX reverse proxy)

**Public Access**: `https://jiridj.be/classic-models`

In production, traffic terminates TLS on your VPS (Let's Encrypt), and NGINX proxies requests to your upstream deployment (e.g. QNAP via myqnapcloud).

#### NGINX configuration notes

- Do **not** strip the `/classic-models` prefix. Forward the full request URI upstream.
- Forward `Host` and `X-Forwarded-Proto https` so Django can build correct absolute URLs (for the OIDC discovery doc and Swagger servers list).

## Environment variables (production)

```bash
# Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=classicmodels
MYSQL_USER=classicuser
MYSQL_PASSWORD=<your-password>

# Django Configuration
DEBUG=0
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=jiridj.be,<your-upstream-host>,localhost

# JWT (RS256 + JWKS) for API gateways (recommended)
JWT_ISSUER=https://jiridj.be/classic-models
JWT_AUDIENCE=classic-models-api
JWT_PRIVATE_KEY_FILE=/run/secrets/jwt_private.pem
JWT_PUBLIC_KEY_FILE=/run/secrets/jwt_public.pem

# Proxy support is enabled by default in settings (X-Forwarded-* headers)
```

## Testing Different Access Methods

### Local Development
```bash
# API Documentation
curl http://localhost:8000/classic-models/api/docs/

# Login
curl -X POST http://localhost:8000/classic-models/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# Products
curl http://localhost:8000/classic-models/api/v1/products/
```

### Production via VPS (NGINX)
```bash
# API Documentation
curl https://jiridj.be/classic-models/api/docs/

# Login
curl -X POST https://jiridj.be/classic-models/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# JWKS (public key set)
curl https://jiridj.be/classic-models/api/auth/.well-known/jwks.json
```

## Troubleshooting

### Issue: 404 errors on all endpoints

**Symptoms**: All endpoints return 404

**Solution**: Make sure you're including `/classic-models` in the path. The API is NOT available at the root path.

❌ Wrong: `http://localhost:8000/api/docs/`  
✅ Correct: `http://localhost:8000/classic-models/api/docs/`

### Issue: API docs redirect incorrectly

**Symptoms**: Accessing docs causes redirect loops or wrong paths

**Solution**: This should not happen with the fixed base path. If it does:
1. Clear browser cache
2. Verify `SCHEMA_PATH_PREFIX` is set to `/classic-models/api/` in settings
3. Check `USE_X_FORWARDED_HOST` is `True`

### Issue: CORS errors

**Symptoms**: Browser shows CORS errors when accessing through Traefik

**Solution**: Ensure `ALLOWED_HOSTS` includes your public domain: `jiridj.be`

## Postman Testing

For detailed Postman collection setup and authentication configuration, see the [Postman Collection](README.md#-postman-collection) section in the main README.

**Available Environments:**
- **Local Development**: `Classic_Models_API_Local.postman_environment.json`
  - Base URL: `http://localhost:8000/classic-models`
- **Production**: `Classic_Models_API_AWS.postman_environment.json`
  - Base URL: Configure with your production URL

Both environments use the same `/classic-models` base path.

## Summary

| Access Method | Full URL Example |
|---------------|------------------|
| **Local Dev** | `http://localhost:8000/classic-models/api/docs/` |
| **Production via VPS (NGINX)** | `https://jiridj.be/classic-models/api/docs/` |

**Key Benefits:**
- ✅ Consistent URL structure across all environments
- ✅ Simple NGINX configuration (no prefix stripping needed)
- ✅ No environment variable configuration for base path
- ✅ Works with direct access and reverse proxy
- ✅ Easier to reason about and debug

**The application ALWAYS expects requests at `/classic-models` base path.**
