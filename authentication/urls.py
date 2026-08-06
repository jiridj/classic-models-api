from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    current_user_view,
    logout_view,
    rate_limit_demo_view,
    signup_view,
)
from .well_known import jwks_view, openid_configuration_view
from .oauth_views import authorize_view, token_view, revoke_view

auth_urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", current_user_view, name="current_user"),
    path("rate-limit-demo/", rate_limit_demo_view, name="rate_limit_demo"),
    path(".well-known/jwks.json", jwks_view, name="jwks"),
    path(
        ".well-known/openid-configuration",
        openid_configuration_view,
        name="openid_configuration",
    ),
]

oauth_urlpatterns = [
    path("authorize/", authorize_view, name="oauth_authorize"),
    path("token/", token_view, name="oauth_token"),
    path("token/revoke/", revoke_view, name="oauth_revoke"),
]

urlpatterns = auth_urlpatterns
