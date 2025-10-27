"""
Custom throttle classes for API rate limiting.

Rate limits are designed to:
- Prevent abuse (authentication endpoints)
- Allow reasonable usage (read operations)
- Limit write operations to prevent data corruption
- Provide clear feedback via headers
"""

from rest_framework import throttling


class LoginThrottle(throttling.AnonRateThrottle):
    """
    Throttle login attempts to prevent brute force attacks.
    
    Allow 50 login attempts per hour per IP address.
    """
    scope = "login"
    rate = "50/hour"


class RegisterThrottle(throttling.AnonRateThrottle):
    """
    Throttle registration attempts to prevent spam accounts.
    
    Allow 50 registration attempts per hour per IP address.
    """
    scope = "register"
    rate = "50/hour"


class TokenRefreshThrottle(throttling.UserRateThrottle):
    """
    Throttle token refresh requests.
    
    Allow 100 refresh requests per minute per authenticated user.
    """
    scope = "token_refresh"
    rate = "100/min"


class LogoutThrottle(throttling.UserRateThrottle):
    """
    Throttle logout requests.
    
    Allow 200 logout requests per minute per authenticated user.
    """
    scope = "logout"
    rate = "200/min"


class CurrentUserThrottle(throttling.UserRateThrottle):
    """
    Throttle current user information requests.
    
    Allow 600 requests per minute per authenticated user.
    """
    scope = "current_user"
    rate = "600/min"


class ReadThrottle(throttling.UserRateThrottle):
    """
    Throttle read operations (GET requests).
    
    Allow 1000 read requests per minute per authenticated user.
    This is more lenient since reads don't modify data.
    """
    scope = "read"
    rate = "1000/min"
    
    def allow_request(self, request, view):
        # Only apply this throttle to read operations
        if hasattr(view, 'action') and view.action:
            # Skip throttling for write actions, let WriteThrottle handle them
            if view.action in ['create', 'update', 'partial_update', 'destroy']:
                return True
        return super().allow_request(request, view)


class WriteThrottle(throttling.UserRateThrottle):
    """
    Throttle write operations (POST, PUT, PATCH, DELETE).
    
    Allow 200 write requests per minute per authenticated user.
    This is more restrictive since writes modify data.
    """
    scope = "write"
    rate = "200/min"
    
    def allow_request(self, request, view):
        # Only apply this throttle to write operations
        if hasattr(view, 'action') and view.action:
            # Skip throttling for read actions, let ReadThrottle handle them
            if view.action in ['list', 'retrieve']:
                return True
        return super().allow_request(request, view)


class BurstThrottle(throttling.UserRateThrottle):
    """
    Allow short bursts of requests.
    
    Allow 1000 requests per minute per authenticated user.
    Useful for endpoints that might receive bursts.
    """
    scope = "burst"
    rate = "1000/min"


class DemoRateLimitThrottle(throttling.AnonRateThrottle):
    """
    Throttle demo endpoint to demonstrate rate limiting.
    
    Allow 5 requests per minute per IP address.
    Public endpoint for demonstration purposes.
    """
    scope = "demo_rate_limit"
    rate = "5/min"

