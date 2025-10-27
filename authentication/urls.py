from django.urls import path

from .views import (CustomTokenObtainPairView, CustomTokenRefreshView,
                    current_user_view, logout_view, register_view)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", current_user_view, name="current_user"),
]
