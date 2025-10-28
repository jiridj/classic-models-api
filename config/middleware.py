"""
Project middlewares
"""

from django.utils.deprecation import MiddlewareMixin
import time


class SleepDelayMiddleware(MiddlewareMixin):
    """Sleep for N seconds when 'Sleep' header is provided (applies to all endpoints)."""

    MAX_SLEEP_SECONDS = 30

    def process_request(self, request):
        sleep_header = request.META.get("HTTP_SLEEP")
        if not sleep_header:
            return None
        try:
            seconds = int(sleep_header)
        except (TypeError, ValueError):
            return None
        if seconds <= 0:
            return None
        # Clamp to safety bounds
        seconds = min(self.MAX_SLEEP_SECONDS, seconds)
        time.sleep(seconds)
        return None
