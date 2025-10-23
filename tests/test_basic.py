"""
Basic tests to verify pytest setup works.
"""

import pytest
from rest_framework.test import APIClient


class TestBasicSetup:
    """Test basic setup without database access."""

    @pytest.mark.django_db
    def test_django_setup(self):
        """Test that Django is properly configured."""
        from django.conf import settings

        assert "classicmodels" in settings.INSTALLED_APPS
        assert "authentication" in settings.INSTALLED_APPS

    @pytest.mark.django_db
    def test_api_client_creation(self):
        """Test that API client can be created."""
        client = APIClient()
        assert client is not None

    @pytest.mark.django_db
    def test_imports_work(self):
        """Test that all imports work correctly."""
        from authentication.serializers import LoginSerializer
        from classicmodels.models import Customer, Office, Product

        assert Office is not None
        assert Product is not None
        assert Customer is not None
        assert LoginSerializer is not None
