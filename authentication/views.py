from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import LoginSerializer, UserSerializer, RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with detailed responses"""
    
    @extend_schema(
        operation_id="login",
        summary="User Login",
        description="Authenticate user with username and password to obtain JWT tokens",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: {
                "description": "Login successful",
                "content": {
                    "application/json": {
                        "example": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "user": {
                                "id": 1,
                                "username": "demo_user",
                                "email": "demo@example.com",
                                "first_name": "Demo",
                                "last_name": "User",
                                "is_active": True,
                                "date_joined": "2024-01-01T00:00:00Z"
                            }
                        }
                    }
                }
            },
            400: {"description": "Invalid credentials"},
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="logout",
    summary="User Logout",
    description="Logout user by blacklisting the refresh token",
    tags=["Authentication"],
    request={
        "type": "object",
        "properties": {
            "refresh": {
                "type": "string",
                "description": "Refresh token to blacklist"
            }
        },
        "required": ["refresh"]
    },
    responses={
        200: {"description": "Logout successful"},
        400: {"description": "Invalid token"},
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout view that blacklists the refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Successfully logged out'}, 
            status=status.HTTP_200_OK
        )
    except TokenError:
        return Response(
            {'error': 'Invalid token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    operation_id="register",
    summary="User Registration",
    description="Register a new user account",
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User created successfully",
                        "user": {
                            "id": 1,
                            "username": "new_user",
                            "email": "new@example.com",
                            "first_name": "New",
                            "last_name": "User",
                            "is_active": True,
                            "date_joined": "2024-01-01T00:00:00Z"
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid data"},
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="get_current_user",
    summary="Get Current User",
    description="Get information about the currently authenticated user",
    tags=["Authentication"],
    responses={
        200: {
            "description": "User information",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "demo_user",
                        "email": "demo@example.com",
                        "first_name": "Demo",
                        "last_name": "User",
                        "is_active": True,
                        "date_joined": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    """Get current user information"""
    return Response(UserSerializer(request.user).data)
