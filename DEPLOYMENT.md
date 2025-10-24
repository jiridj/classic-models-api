# Deployment Guide

## Overview

This application supports multiple deployment scenarios with different access patterns.

## Deployment Environments

### 1. Local Development (Docker Compose)

**Access**: Direct - `http://localhost:8000`  
**Proxy**: None  
**Configuration**: Default settings (no environment variables needed)

```bash
# Start local development
make start

# Access API
curl http://localhost:8000/api/docs/
```

### 2. AWS Production (ECS Fargate)

**Access**:
- **Direct**: `http://[aws-endpoint]:8000` (no prefix)
- **Via Traefik**: `https://router.jiridj.be/classic-models` (with prefix)

**Proxy**: Traefik **without** `strip_prefix` (Django handles the prefix)  
**Configuration**: No `SCRIPT_NAME` needed - works for both access methods

The AWS deployment can be accessed in two ways:

1. **Direct Access** (no proxy):
   - Requests go directly to AWS ECS
   - URLs like `/api/docs/` work as expected

2. **Via Traefik Proxy** (with prefix):
   - Receives requests at `https://router.jiridj.be/classic-models/*`
   - **Does NOT strip** the `/classic-models` prefix
   - Forwards to AWS ECS at `http://[aws-endpoint]/classic-models/*`
   - Django receives the full path and handles it correctly

## Environment Variables for AWS Deployment

Add these environment variables to your ECS task definition:

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
ALLOWED_HOSTS=router.jiridj.be,<your-aws-domain>,<your-aws-ip>

# Note: NO SCRIPT_NAME needed - Django will handle paths dynamically
# The X-Forwarded headers are enabled by default in settings
```

## How It Works

### Reverse Proxy Path Handling (WITHOUT strip_prefix)

**Critical**: Configure Traefik with `strip_prefix: false` (or don't use strip_prefix at all)

When Traefik proxies requests **without** stripping the prefix:

1. **Incoming Request**: `https://router.jiridj.be/classic-models/api/docs/`
2. **Traefik keeps prefix**: `/classic-models` is NOT stripped
3. **Forwarded to AWS**: `http://[aws-endpoint]/classic-models/api/docs/`
4. **Django receives**: `/classic-models/api/docs/` as the full path
5. **Django routes**: Matches the request to the correct endpoint
6. **Generated URLs**: Django generates relative URLs that work correctly

### Direct Access (No Proxy)

When accessing AWS directly:

1. **Direct Request**: `http://[aws-ip]:8000/api/docs/`
2. **Django receives**: `/api/docs/` as the path
3. **Django routes**: Matches the request to the correct endpoint
4. **Generated URLs**: Django generates relative URLs without prefix

### Django Settings

The application uses these Django settings:

- **`FORCE_SCRIPT_NAME`**: Left as `None` to allow dynamic path handling
- **`USE_X_FORWARDED_HOST`**: `True` - respects the original host from proxy headers
- **`USE_X_FORWARDED_PORT`**: `True` - respects the original port from proxy headers
- **`SECURE_PROXY_SSL_HEADER`**: Respects HTTPS from proxy

### URL Configuration

Django's URL patterns are configured to accept both root and prefixed paths:

```python
# config/urls.py
urlpatterns = [
    path("", include(api_patterns)),              # Direct: /api/docs/
    path("classic-models/", include(api_patterns)), # Proxy: /classic-models/api/docs/
]
```

This means both access methods work with the same deployment:
- **Direct**: `http://aws-ip:8000/api/docs/` ✅
- **Proxy**: `https://router.jiridj.be/classic-models/api/docs/` ✅

## Testing Different Access Methods

### Local Development
```bash
# No path prefix
curl http://localhost:8000/api/docs/
curl http://localhost:8000/api/auth/login/
```

### AWS via Traefik Proxy (Production)
```bash
# With /classic-models prefix
curl https://router.jiridj.be/classic-models/api/docs/
curl https://router.jiridj.be/classic-models/api/auth/login/
```

## Troubleshooting

### Issue: 404 errors when accessing via Traefik

**Symptoms**: `https://router.jiridj.be/classic-models/api/docs/` returns 404

**Solutions**:
1. Ensure Traefik is configured with `strip_prefix: false` (or no strip_prefix)
2. Verify the URL pattern in `config/urls.py` includes the `classic-models/` path

### Issue: Direct AWS access returns 404

**Symptoms**: `http://aws-ip:8000/api/docs/` returns 404

**Solution**: This should work automatically. Check that the root URL pattern `path("", include(api_patterns))` exists in `config/urls.py`

### Issue: CORS errors when accessing from proxy

**Symptoms**: Browser shows CORS errors when accessing through Traefik

**Solution**: Ensure `ALLOWED_HOSTS` includes `router.jiridj.be`

### Issue: Some API URLs work but others don't

**Symptoms**: `/api/docs/` works but `/api/v1/classicmodels/products/` doesn't

**Solution**: Verify all URL includes are using `api_patterns` in both root and prefixed paths

## Postman Testing

Use the appropriate Postman environment:

- **Local Development**: `Classic_Models_API_Local.postman_environment.json`
  - Base URL: `http://localhost:8000`
  
- **AWS Production (via Traefik)**: `Classic_Models_API_AWS.postman_environment.json`
  - Base URL: `https://router.jiridj.be/classic-models`

## Summary

| Access Method | URL | Django URL Pattern | Traefik Config | Environment Variables |
|---------------|-----|-------------------|----------------|----------------------|
| **Local Dev** | `http://localhost:8000/api/docs/` | `path("", include(api_patterns))` | N/A | Default |
| **AWS Direct** | `http://aws-ip:8000/api/docs/` | `path("", include(api_patterns))` | N/A | Production vars only |
| **AWS via Traefik** | `https://router.jiridj.be/classic-models/api/docs/` | `path("classic-models/", include(api_patterns))` | `strip_prefix: false` | Production vars only |

**Key Points:**
- ✅ Single deployment works for both direct and proxied access
- ✅ No `SCRIPT_NAME` environment variable needed
- ✅ Traefik must be configured to NOT strip the prefix
- ✅ Django handles both path patterns in the same codebase

