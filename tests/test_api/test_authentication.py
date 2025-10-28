"""
Tests for authentication API endpoints.
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from authentication.serializers import UserSerializer


class TestAuthenticationAPI:
    """Test cases for authentication API endpoints."""

    @pytest.mark.django_db
    def test_register_success(self, api_client):
        """Test successful user registration."""
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == "newuser"
        assert response.data["user"]["email"] == "newuser@example.com"
        assert response.data["user"]["first_name"] == "New"
        assert response.data["user"]["last_name"] == "User"
        assert response.data["user"]["is_active"] is True
        assert (
            "password" not in response.data["user"]
        )  # Password should not be returned

    @pytest.mark.django_db
    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpass123",
            "password_confirm": "differentpass",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    @pytest.mark.django_db
    def test_register_short_password(self, api_client):
        """Test registration with password too short."""
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "short",
            "password_confirm": "short",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    @pytest.mark.django_db
    def test_register_duplicate_username(self, api_client, user):
        """Test registration with duplicate username."""
        url = reverse("signup")
        data = {
            "username": user.username,  # Existing username
            "email": "different@example.com",
            "first_name": "Different",
            "last_name": "User",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    @pytest.mark.django_db
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields."""
        url = reverse("signup")
        data = {
            "username": "newuser",
            # Missing other required fields
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "first_name" in response.data
        assert "last_name" in response.data
        assert "password" in response.data

    @pytest.mark.django_db
    def test_login_success(self, api_client, user):
        """Test successful user login."""
        url = reverse("login")
        data = {"username": user.username, "password": "testpass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == user.username
        assert response.data["user"]["email"] == user.email

    @pytest.mark.django_db
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        url = reverse("login")
        data = {"username": "nonexistent", "password": "wrongpassword"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    @pytest.mark.django_db
    def test_login_inactive_user(self, api_client):
        """Test login with inactive user."""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="testpass123",
            is_active=False,
        )

        url = reverse("login")
        data = {"username": inactive_user.username, "password": "testpass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    @pytest.mark.django_db
    def test_login_missing_fields(self, api_client):
        """Test login with missing fields."""
        url = reverse("login")
        data = {
            "username": "testuser",
            # Missing password
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    @pytest.mark.django_db
    def test_logout_success(self, api_client, user):
        """Test successful user logout."""
        # First login to get tokens
        login_url = reverse("login")
        login_data = {"username": user.username, "password": "testpass123"}
        login_response = api_client.post(login_url, login_data, format="json")
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # Now logout using the access token for authentication
        url = reverse("logout")
        data = {"refresh": refresh_token}

        # Use the access token for authentication
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @pytest.mark.django_db
    def test_logout_missing_token(self, api_client, user):
        """Test logout without refresh token."""
        # First login to get access token
        login_url = reverse("login")
        login_data = {"username": user.username, "password": "testpass123"}
        login_response = api_client.post(login_url, login_data, format="json")
        access_token = login_response.data["access"]

        # Now logout without refresh token
        url = reverse("logout")
        data = {}  # Missing refresh token

        # Use the access token for authentication
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    @pytest.mark.django_db
    def test_logout_invalid_token(self, api_client, user):
        """Test logout with invalid refresh token."""
        # First login to get access token
        login_url = reverse("login")
        login_data = {"username": user.username, "password": "testpass123"}
        login_response = api_client.post(login_url, login_data, format="json")
        access_token = login_response.data["access"]

        # Now logout with invalid refresh token
        url = reverse("logout")
        data = {"refresh": "invalid_token"}

        # Use the access token for authentication
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    @pytest.mark.django_db
    def test_current_user_authenticated(self, authenticated_api_client, user):
        """Test getting current user when authenticated."""
        url = reverse("current_user")

        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email
        assert response.data["first_name"] == user.first_name
        assert response.data["last_name"] == user.last_name

    @pytest.mark.django_db
    def test_current_user_unauthenticated(self, api_client):
        """Test getting current user when not authenticated."""
        url = reverse("current_user")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_token_refresh(self, api_client, user):
        """Test token refresh functionality."""
        # First login to get tokens
        login_url = reverse("login")
        login_data = {"username": user.username, "password": "testpass123"}
        login_response = api_client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        # Now refresh the token
        url = reverse("token_refresh")
        data = {"refresh": refresh_token}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    @pytest.mark.django_db
    def test_token_refresh_invalid_token(self, api_client):
        """Test token refresh with invalid token."""
        url = reverse("token_refresh")
        data = {"refresh": "invalid_token"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_serializer(self, user):
        """Test UserSerializer functionality."""
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["id"] == user.id
        assert data["username"] == user.username
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert data["is_active"] == user.is_active
        assert "password" not in data  # Password should not be included

    @pytest.mark.django_db
    def test_register_serializer_validation(self):
        """Test RegisterSerializer validation."""
        from authentication.serializers import RegisterSerializer

        # Test password mismatch
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "password_confirm": "different123",
        }

        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password_confirm" in serializer.errors

    @pytest.mark.django_db
    def test_register_serializer_create(self):
        """Test RegisterSerializer create method."""
        from authentication.serializers import RegisterSerializer

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "password_confirm": "password123",
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.check_password("password123")

    @pytest.mark.django_db
    def test_login_serializer_validation(self):
        """Test LoginSerializer validation."""
        from authentication.serializers import LoginSerializer

        # Test with invalid credentials
        data = {"username": "nonexistent", "password": "wrongpassword"}

        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    @pytest.mark.django_db
    def test_login_serializer_valid_credentials(self, user):
        """Test LoginSerializer with valid credentials."""
        from authentication.serializers import LoginSerializer

        data = {"username": user.username, "password": "testpass123"}

        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert "user" in serializer.validated_data
        assert serializer.validated_data["user"] == user

    @pytest.mark.django_db
    def test_authentication_endpoints_require_authentication(self, api_client):
        """Test that protected endpoints require authentication."""
        # Test logout endpoint
        logout_url = reverse("logout")
        response = api_client.post(logout_url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test current user endpoint
        current_user_url = reverse("current_user")
        response = api_client.get(current_user_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_authentication_endpoints_allow_anonymous(self, api_client):
        """Test that public endpoints allow anonymous access."""
        # Test signup endpoint
        register_url = reverse("signup")
        response = api_client.get(
            register_url
        )  # GET should return 405 Method Not Allowed
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Test login endpoint
        login_url = reverse("login")
        response = api_client.get(login_url)  # GET should return 405 Method Not Allowed
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
