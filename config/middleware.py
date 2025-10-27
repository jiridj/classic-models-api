"""
Middleware to add rate limit headers to responses.
"""

from django.utils.deprecation import MiddlewareMixin


class RateLimitHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that adds rate limit headers to responses.
    
    This middleware checks if the request has throttle headers set by
    our custom throttle classes and adds them to the response.
    """
    
    def process_response(self, request, response):
        """Add rate limit headers to the response if they exist on the request."""
        if hasattr(request, '_throttle_headers') and request._throttle_headers:
            for header_name, header_value in request._throttle_headers.items():
                response[header_name] = str(header_value)
        
        return response
