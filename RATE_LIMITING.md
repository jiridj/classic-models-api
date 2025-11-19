# Rate Limiting Documentation

## Overview

This API implements comprehensive rate limiting to protect against abuse, ensure fair usage, and maintain system performance. Rate limits are applied using Django REST Framework's built-in throttling mechanisms.

> **Note**: For general API information, see [README.md](README.md). For deployment configuration, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Rate Limit Categories

### Authentication Endpoints

These endpoints have strict rate limits to prevent brute force attacks and spam:

- **Login** (`POST /auth/login/`): **5 requests per hour per IP address**
  - Prevents brute force attacks
  - Resets every hour
  
- **Signup** (`POST /auth/signup/`): **5 requests per hour per IP address**
  - Prevents spam account creation
  - Resets every hour

- **Token Refresh** (`POST /auth/refresh/`): **10 requests per minute per user**
  - Reasonable for normal token refresh operations
  - Per authenticated user

- **Logout** (`POST /auth/logout/`): **20 requests per minute per user**
  - Rare operation, but allows some flexibility
  
- **Get Current User** (`GET /auth/me/`): **60 requests per minute per user**
  - Frequently accessed endpoint
  - Generous limit for user information retrieval

### API Endpoints

Rate limits differentiate between read and write operations:

#### Read Operations (GET requests)
- **List/Retrieve**: **100 requests per minute per user**
  - Includes: list all resources, retrieve specific resource
  - More lenient since reads don't modify data
  - Suitable for browsing, pagination, and data exploration

#### Write Operations (POST, PUT, PATCH, DELETE)
- **Create/Update/Delete**: **20 requests per minute per user**
  - Includes: create new records, update existing records, delete records
  - More restrictive to prevent data corruption and abuse
  - Limits accidental bulk operations

### Default Rates

- **Anonymous users**: 20 requests per hour per IP
- **Authenticated users**: 100 requests per minute per user

## Rate Limit Headers

The API returns standard rate limit headers in all responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the time window
- `X-RateLimit-Remaining`: The number of requests remaining in the current window
- `X-RateLimit-Reset`: The time when the rate limit resets (Unix timestamp)

## Rate Limit Exceeded Response

When a rate limit is exceeded, the API returns:

```json
{
  "detail": "Request was throttled. Expected available in N seconds."
}
```

HTTP Status Code: **429 Too Many Requests**

## Implementation Details

### Throttle Classes

Located in `config/throttles.py`:

- `LoginThrottle`: For login endpoints (IP-based)
- `RegisterThrottle`: For registration endpoints (IP-based)
- `TokenRefreshThrottle`: For token refresh (user-based)
- `LogoutThrottle`: For logout (user-based)
- `CurrentUserThrottle`: For current user endpoint (user-based)
- `ReadThrottle`: For read operations (user-based)
- `WriteThrottle`: For write operations (user-based)

### Configuration

Rate limits are configured in `config/settings/base.py` under `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']`.

### Per-Endpoint Application

- Authentication views: Explicitly apply throttle classes via decorators
- API viewsets: Automatically apply read/write throttles based on action type
- Base viewset applies different throttles for list/retrieve vs create/update/delete

## Best Practices for Clients

1. **Implement retry logic**: When receiving a 429 status, wait for the time specified in `Retry-After` header (if available) or exponential backoff
2. **Monitor rate limit headers**: Track `X-RateLimit-Remaining` to avoid hitting limits
3. **Cache data when possible**: Reduce unnecessary API calls by caching responses
4. **Batch operations wisely**: Use write operations sparingly to stay within limits
5. **Handle 429 gracefully**: Display user-friendly messages when rate limited

## Adjusting Rate Limits

To adjust rate limits, modify `config/settings/base.py`:

```python
"DEFAULT_THROTTLE_RATES": {
    "login": "5/hour",        # Increase/decrease as needed
    "read": "100/min",        # Adjust based on usage patterns
    "write": "20/min",         # Adjust based on usage patterns
    # ...
}
```

After changes, restart the Django application.

## Testing Rate Limits

You can test rate limits using tools like:

1. **curl**: Make repeated requests to an endpoint
2. **Postman**: Create collections with multiple iterations
3. **Python**: Write scripts that make rapid API calls
4. **Load testing tools**: Use tools like Apache Bench (ab) or locust

Example with curl:

```bash
# Test login rate limit (5/hour)
for i in {1..10}; do
  curl -X POST http://localhost:8000/classic-models/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"demo123"}'
  echo "Request $i"
done
```

## Notes

- Rate limits are user/IP-based for authenticated/anonymous users respectively
- Throttling uses a sliding window approach for better accuracy
- Rate limits reset based on their time window (per minute/hour)
- Different endpoints may have different limits based on their sensitivity
- All authenticated endpoints inherit throttling from the base viewset

