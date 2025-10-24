from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.permissions import AllowAny

# Core URL patterns (work with or without prefix)
api_patterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
    path("api/auth/", include("authentication.urls")),
    # OpenAPI schema and docs (public access)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[AllowAny]
        ),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="redoc",
    ),
]

# URL patterns support both:
# - Direct access: /api/docs/
# - Via proxy: /classic-models/api/docs/
urlpatterns = [
    path("", include(api_patterns)),  # Direct access (no prefix)
    path("classic-models/", include(api_patterns)),  # Via Traefik proxy
]
