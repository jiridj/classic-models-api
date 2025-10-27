"""
Custom throttle classes for API rate limiting.

Rate limits are designed to:
- Prevent abuse (authentication endpoints)
- Allow reasonable usage (read operations)
- Limit write operations to prevent data corruption
- Provide clear feedback via headers
"""

import time
from rest_framework import throttling


def add_rate_limit_headers(request, throttle_instance):
    """
    Helper function to add rate limit headers to request.
    Called after throttling check.
    Note: This is a simplified implementation that adds basic headers
    without trying to calculate remaining requests accurately.
    """
    # Initialize headers dict if needed
    if not hasattr(request, '_throttle_headers'):
        request._throttle_headers = {}
    
    # Calculate reset time (approximate)
    reset_timestamp = int(time.time()) + int(throttle_instance.duration)
    
    # Add basic headers
    # Note: Remaining count is not calculated here due to complexity
    # For a full implementation, you'd need to track state
    request._throttle_headers.update({
        'X-RateLimit-Limit': str(throttle_instance.num_requests),
        'X-RateLimit-Reset': str(reset_timestamp),
    })


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
    
    def wait(self):
        """
        Returns the recommended next request time in seconds,
        and optionally adds headers to the response.
        """
        import time
        from datetime import datetime, timedelta
        
        wait_time = super().wait()
        if wait_time:
            # We're being throttled
            # The history contains timestamps from the cache
            # Calculate when the window resets
            reset_time = time.time() + wait_time
            
            # Add headers if request object exists
            if hasattr(self, 'request'):
                if not hasattr(self.request, '_throttle_headers'):
                    self.request._throttle_headers = {}
                self.request._throttle_headers.update({
                    'X-RateLimit-Limit': str(self.num_requests),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': str(int(reset_time)),
                    'Retry-After': str(int(wait_time)),
                })
        
        return wait_time
    
    def allow_request(self, request, view):
        """
        Override to store request and add headers on success.
        """
        import time
        from datetime import datetime
        
        # Store request reference for use in wait()
        self.request = request
        
        if not hasattr(request, '_throttle_headers'):
            request._throttle_headers = {}
        
        # Calculate remaining BEFORE calling parent (which may modify cache)
        key = self.get_cache_key(request, view)
        reset_time = time.time() + self.duration
        history = []
        
        if key:
            # Get history from cache BEFORE calling parent
            cache_data = self.cache.get(key, [])
            # Filter out old entries (outside the time window)
            now = datetime.now()
            window_start = now.timestamp() - self.duration
            history = [h for h in cache_data if h > window_start]
        
        # Calculate remaining BEFORE the current request is processed
        # After allow_request, this will be one less
        remaining_before = max(0, self.num_requests - len(history))
        
        # Call parent to check throttling (this may add current request to cache)
        is_allowed = super().allow_request(request, view)
        
        # Calculate remaining AFTER the current request
        # If allowed and not throttled, this request was consumed
        remaining_after = remaining_before
        if is_allowed and remaining_before > 0:
            remaining_after = remaining_before - 1
        
        headers = {
            'X-RateLimit-Limit': str(self.num_requests),
            'X-RateLimit-Remaining': str(remaining_after),
            'X-RateLimit-Reset': str(int(reset_time)),
        }
        request._throttle_headers.update(headers)
        
        return is_allowed

