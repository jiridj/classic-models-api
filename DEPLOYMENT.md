# Deployment Guide

## Overview

This application is **always** served at the `/classic-models` base path in all environments. This simplifies reverse proxy configuration and ensures consistent URLs across local development and production.

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

### 2. AWS Production (ECS Fargate)

**Direct Access**: `http://[aws-ip]:8000/classic-models`  
**Via Traefik Proxy**: `https://router.jiridj.be/classic-models`

Both access methods use the same base path, which simplifies Traefik configuration.

## Traefik Reverse Proxy Configuration

**Critical**: Configure Traefik to **NOT strip the prefix**

```yaml
# Traefik configuration (do NOT use strip_prefix)
routers:
  classic-models:
    rule: "PathPrefix(`/classic-models`)"
    service: classic-models-service

services:
  classic-models-service:
    loadBalancer:
      servers:
        - url: "http://aws-ip:8000"
```

**How it works:**
1. Client requests: `https://router.jiridj.be/classic-models/api/docs/`
2. Traefik matches: PathPrefix `/classic-models`
3. Traefik forwards: `http://aws-ip:8000/classic-models/api/docs/` (full path)
4. Django receives: `/classic-models/api/docs/`
5. Django routes correctly ✅

## Environment Variables for AWS Deployment

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

# Proxy support is enabled by default in settings
# No additional environment variables needed!
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
curl http://localhost:8000/classic-models/api/v1/classicmodels/products/
```

### AWS Direct Access
```bash
# API Documentation
curl http://aws-ip:8000/classic-models/api/docs/

# Login
curl -X POST http://aws-ip:8000/classic-models/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

### AWS via Traefik Proxy
```bash
# API Documentation
curl https://router.jiridj.be/classic-models/api/docs/

# Login
curl -X POST https://router.jiridj.be/classic-models/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

## Troubleshooting

### Issue: 404 errors on all endpoints

**Symptoms**: All endpoints return 404

**Solution**: Make sure you're including `/classic-models` in the path. The API is NOT available at the root path.

❌ Wrong: `http://localhost:8000/api/docs/`  
✅ Correct: `http://localhost:8000/classic-models/api/docs/`

### Issue: Traefik returns 404

**Symptoms**: Direct access works but Traefik returns 404

**Solutions**:
1. Verify Traefik PathPrefix rule: `PathPrefix(\`/classic-models\`)`
2. Ensure Traefik is NOT using `strip_prefix`
3. Check Traefik is forwarding the full path to Django

### Issue: API docs redirect incorrectly

**Symptoms**: Accessing docs causes redirect loops or wrong paths

**Solution**: This should not happen with the fixed base path. If it does:
1. Clear browser cache
2. Verify `SCHEMA_PATH_PREFIX` is set to `/classic-models/api/` in settings
3. Check `USE_X_FORWARDED_HOST` is `True`

### Issue: CORS errors

**Symptoms**: Browser shows CORS errors when accessing through Traefik

**Solution**: Ensure `ALLOWED_HOSTS` includes the Traefik domain: `router.jiridj.be`

## Postman Testing

**Local Development Environment:**
- File: `Classic_Models_API_Local.postman_environment.json`
- Base URL: `http://localhost:8000/classic-models`

**AWS Production Environment:**
- File: `Classic_Models_API_AWS.postman_environment.json`
- Base URL: `https://router.jiridj.be/classic-models`

Both environments use the same `/classic-models` base path.

## Summary

| Access Method | Full URL Example | Traefik Config |
|---------------|------------------|----------------|
| **Local Dev** | `http://localhost:8000/classic-models/api/docs/` | N/A |
| **AWS Direct** | `http://aws-ip:8000/classic-models/api/docs/` | N/A |
| **AWS via Traefik** | `https://router.jiridj.be/classic-models/api/docs/` | PathPrefix, NO strip_prefix |

**Key Benefits:**
- ✅ Consistent URL structure across all environments
- ✅ Simple Traefik configuration (no prefix stripping needed)
- ✅ No environment variable configuration for base path
- ✅ Works with direct access and reverse proxy
- ✅ Easier to reason about and debug

**The application ALWAYS expects requests at `/classic-models` base path.**
