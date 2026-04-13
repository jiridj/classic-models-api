"""
Tests for API Key Authentication

Tests the system-level API key authentication mechanism.
"""

import os
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from authentication.api_key_auth import SystemUser


@pytest.mark.django_db
class TestApiKeyAuthentication:
    """Test API key authentication functionality"""

    def setup_method(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.test_api_key = "test-api-key-12345"
        self.products_url = "/classic-models/api/v1/products/"

    def test_api_key_authentication_success(self):
        """Test successful authentication with valid API key"""
        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            response = self.client.get(
                self.products_url, HTTP_X_API_KEY=self.test_api_key
            )
            assert response.status_code == status.HTTP_200_OK

    def test_api_key_authentication_invalid_key(self):
        """Test authentication fails with invalid API key"""
        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            response = self.client.get(
                self.products_url, HTTP_X_API_KEY="wrong-api-key"
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid API key" in str(response.data)

    def test_api_key_authentication_no_key_provided(self):
        """Test that missing API key falls back to other auth methods"""
        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            # Without API key, should get 401 (no JWT either)
            response = self.client.get(self.products_url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api_key_authentication_not_configured(self):
        """Test authentication fails when API_KEY is not configured"""
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get(
                self.products_url, HTTP_X_API_KEY="some-key"
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "not configured" in str(response.data)

    def test_api_key_grants_full_access(self):
        """Test that API key grants full access to protected endpoints"""
        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            # Test GET (read)
            response = self.client.get(
                self.products_url, HTTP_X_API_KEY=self.test_api_key
            )
            assert response.status_code == status.HTTP_200_OK

            # Test POST (create) - should have permission
            product_data = {
                "productCode": "TEST_API_KEY_001",
                "productName": "Test Product via API Key",
                "productLine": "Classic Cars",
                "productScale": "1:10",
                "productVendor": "Test Vendor",
                "productDescription": "Test product created with API key",
                "quantityInStock": 100,
                "buyPrice": "50.00",
                "MSRP": "75.00",
            }
            response = self.client.post(
                self.products_url,
                product_data,
                format="json",
                HTTP_X_API_KEY=self.test_api_key,
            )
            assert response.status_code == status.HTTP_201_CREATED

    def test_api_key_works_alongside_jwt(self):
        """Test that API key authentication works as alternative to JWT"""
        # Create a user and get JWT token
        user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        login_response = self.client.post(
            "/classic-models/api/auth/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        jwt_token = login_response.data["access"]

        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            # Test with JWT token (should work)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
            response = self.client.get(self.products_url)
            assert response.status_code == status.HTTP_200_OK

            # Test with API key (should also work)
            self.client.credentials()  # Clear JWT
            response = self.client.get(
                self.products_url, HTTP_X_API_KEY=self.test_api_key
            )
            assert response.status_code == status.HTTP_200_OK

    def test_system_user_properties(self):
        """Test SystemUser class properties"""
        system_user = SystemUser()

        assert system_user.is_authenticated is True
        assert system_user.is_staff is True
        assert system_user.is_superuser is True
        assert system_user.username == "system_api_key"
        assert str(system_user) == "System API Key User"

    def test_api_key_with_current_user_endpoint(self):
        """Test that API key works with /me endpoint"""
        with patch.dict(os.environ, {"API_KEY": self.test_api_key}):
            response = self.client.get(
                "/classic-models/api/auth/me/", HTTP_X_API_KEY=self.test_api_key
            )
            # SystemUser should work with the endpoint
            assert response.status_code == status.HTTP_200_OK
            assert response.data["username"] == "system_api_key"

# Made with Bob
