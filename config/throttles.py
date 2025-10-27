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
    
    Allow 5 login attempts per hour per IP address.
    """
    scope = "login"


class RegisterThrottle(throttling.AnonRateThrottle):
    """
    Throttle registration attempts to prevent spam accounts.
    
    Allow 5 registration attempts per hour per IP address.
    """
    scope = "register"


class TokenRefreshThrottle(throttling.UserRateThrottle):
    """
    Throttle token refresh requests.
    
    Allow 10 refresh requests per minute per authenticated user.
    """
    scope = "token_refresh"
    rate = "10/min"


class LogoutThrottle(throttling.UserRateThrottle):
    """
    Throttle logout requests.
    
    Allow 20 logout requests per minute per authenticated user.
    """
    scope = "logout"
    rate = "20/min"


class CurrentUserThrottle(throttling.UserRateThrottle):
    """
    Throttle current user information requests.
    
    Allow 60 requests per minute per authenticated user.
    """
    scope = "current_user"
    rate = "60/min"


class ReadThrottle(throttling.UserRateThrottle):
    """
    Throttle read operations (GET requests).
    
    Allow 100 read requests per minute per authenticated user.
    This is more lenient since reads don't modify data.
    """
    scope = "read"
    rate = "100/min"


class WriteThrottle(throttling.UserRateThrottle):
    """
    Throttle write operations (POST, PUT, PATCH, DELETE).
    
    Allow 20 write requests per minute per authenticated user.
    This is more restrictive since writes modify data.
    """
    scope = "write"
    rate = "20/min"


class BurstThrottle(throttling.UserRateThrottle):
    """
    Allow short bursts of requests.
    
    Allow 100 requests per minute per authenticated user.
    Useful for endpoints that might receive bursts.
    """
    scope = "burst"
    rate = "100/min"

