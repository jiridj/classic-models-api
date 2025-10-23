from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (CustomTokenObtainPairView, current_user_view, logout_view,
                    register_view)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", current_user_view, name="current_user"),
]
