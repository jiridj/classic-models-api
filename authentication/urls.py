from django.urls import path

from .views import (CustomTokenObtainPairView, CustomTokenRefreshView,
                    current_user_view, logout_view, rate_limit_demo_view,
                    signup_view)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", current_user_view, name="current_user"),
    path("rate-limit-demo/", rate_limit_demo_view, name="rate_limit_demo"),
]
