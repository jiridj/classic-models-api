from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.throttles import (
    CurrentUserThrottle,
    DemoRateLimitThrottle,
    LoginThrottle,
    LogoutThrottle,
    RegisterThrottle,
    TokenRefreshThrottle,
)

from .serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    RateLimitDemoResponseSerializer,
    RegisterSerializer,
    SignupResponseSerializer,
    UserSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with detailed responses"""

    throttle_classes = [LoginThrottle]

    @extend_schema(
        operation_id="login",
        summary="User Login",
        description="Authenticate user with username and password to obtain JWT tokens",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: {"description": "Invalid credentials"},
        },
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view with throttling."""

    throttle_classes = [TokenRefreshThrottle]

    @extend_schema(
        operation_id="token_refresh",
        summary="Refresh Token",
        description="Refresh JWT access token using a valid refresh token",
        tags=["Authentication"],
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        """Override post to add schema documentation"""
        return super().post(request, *args, **kwargs)


@extend_schema(
    operation_id="logout",
    summary="User Logout",
    description="Logout user by blacklisting the refresh token",
    tags=["Authentication"],
    request=LogoutSerializer,
    responses={
        200: {"description": "Logout successful"},
        400: {"description": "Invalid token"},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([LogoutThrottle])
def logout_view(request):
    """Logout view that blacklists the refresh token"""
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    except TokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="signup",
    summary="User Signup",
    description="Create a new user account",
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
        201: SignupResponseSerializer,
        400: {"description": "Invalid data"},
    },
    auth=[],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([RegisterThrottle])
def signup_view(request):
    """Create a new user (signup)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User created successfully", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="get_current_user",
    summary="Get Current User",
    description="Get information about the currently authenticated user",
    tags=["Authentication"],
    responses={
        200: UserSerializer,
        401: {"description": "Authentication required"},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CurrentUserThrottle])
def current_user_view(request):
    """Get current user information"""
    return Response(UserSerializer(request.user).data)


@extend_schema(
    operation_id="rate_limit_demo",
    summary="Rate Limit Demo",
    description="Public endpoint to demonstrate rate limiting. Limited to 5 requests per minute per IP.",
    tags=["Authentication"],
    responses={
        200: RateLimitDemoResponseSerializer,
    },
    auth=[],
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([DemoRateLimitThrottle])
def rate_limit_demo_view(request):
    """Demo endpoint to demonstrate rate limiting"""
    from django.utils import timezone

    response_data = {
        "message": "Rate limit demo endpoint",
        "rate_limit": "5 requests per minute per IP address",
        "timestamp": timezone.now().isoformat(),
    }

    response = Response(response_data, status=status.HTTP_200_OK)

    # Add rate limit headers if they were set
    if hasattr(request, "_throttle_headers") and request._throttle_headers:
        for header_name, header_value in request._throttle_headers.items():
            response[header_name] = str(header_value)

    return response
