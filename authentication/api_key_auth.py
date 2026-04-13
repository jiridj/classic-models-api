"""
API Key Authentication for Demo Purposes

This module provides a simple API key authentication mechanism that grants
full admin access. It's designed for demo/testing purposes and should be
used with caution in production environments.

Usage:
    Add the X-API-Key header to your requests:
    X-API-Key: your-secret-api-key

Configuration:
    Set the API_KEY environment variable in your .env file
"""

import os

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions


class SystemUser(AnonymousUser):
    """
    A special user class representing system-level API key access.
    This user has admin privileges but is not a real database user.
    """

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return True

    @property
    def is_superuser(self):
        return True

    @property
    def username(self):
        return "system_api_key"

    def __str__(self):
        return "System API Key User"


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """
    Simple API Key authentication for demo purposes.
    
    Checks for X-API-Key header and validates against environment variable.
    If valid, returns a SystemUser with full admin privileges.
    
    This authentication method works as an alternative to JWT authentication,
    allowing clients to use either JWT tokens OR an API key.
    """

    keyword = "X-API-Key"

    def authenticate(self, request):
        """
        Authenticate the request using API key from header.
        
        Returns:
            tuple: (user, None) if authentication successful
            None: if API key header not present (allows other auth methods)
            
        Raises:
            AuthenticationFailed: if API key is invalid
        """
        api_key = request.META.get("HTTP_X_API_KEY")

        # If no API key provided, return None to allow other authentication methods
        if not api_key:
            return None

        # Get the expected API key from environment
        expected_api_key = os.environ.get("API_KEY")

        # If API_KEY is not configured, reject API key authentication
        if not expected_api_key:
            raise exceptions.AuthenticationFailed(
                "API key authentication is not configured on this server"
            )

        # Validate the API key
        if api_key != expected_api_key:
            raise exceptions.AuthenticationFailed("Invalid API key")

        # Return SystemUser with full privileges
        return (SystemUser(), None)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return self.keyword

# Made with Bob
