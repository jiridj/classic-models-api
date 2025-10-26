import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def get_version():
    """Get version from environment variable or default."""
    return os.environ.get("API_VERSION", "0.3.7")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "0") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Base path configuration
# All URLs are served under /classic-models base path
# This simplifies reverse proxy configuration (no need to strip prefix)

# Enable support for X-Forwarded-* headers from trusted proxies
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    # Project apps
    "classicmodels",
    "authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Classic Models API",
    "DESCRIPTION": """
    API for the Classic Models tutorial database with JWT authentication.
    
    ## Authentication
    
    This API uses JWT (JSON Web Token) authentication. To access protected endpoints:
    
    1. **Login**: POST `/classic-models/api/auth/login/` with username and password
    2. **Use Token**: Include the access token in the Authorization header: `Bearer <access_token>`
    3. **Refresh**: Use POST `/classic-models/api/auth/refresh/` to get a new access token
    4. **Logout**: POST `/classic-models/api/auth/logout/` to invalidate the refresh token
    
    ## Demo User
    
    For testing purposes, you can use:
    - **Username**: `demo`
    - **Password**: `demo123`
    
    ## Base Path
    
    All endpoints are served at `/classic-models` base path.
    
    ## Public Endpoints
    
    - API documentation (this page)
    - Authentication endpoints (`/classic-models/api/auth/`)
    
    ## Protected Endpoints
    
    - All Classic Models data endpoints (`/classic-models/api/v1/classicmodels/`)
    """,
    "VERSION": get_version(),
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "SCHEMA_PATH_PREFIX": "/classic-models/api/",
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "EXTENSIONS_INFO": {
        "x-logo": {
            "url": "https://via.placeholder.com/200x50/0066CC/FFFFFF?text=Classic+Models+API"
        }
    },
    "COMPONENTS": {
        "securitySchemes": {
            "JWTAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from /api/auth/login/",
            }
        }
    },
    "TAGS": [
        {"name": "Authentication", "description": "User authentication and management"},
        {"name": "Product Lines", "description": "Product line categories"},
        {"name": "Products", "description": "Product catalog"},
        {"name": "Offices", "description": "Company office locations"},
        {"name": "Employees", "description": "Employee information"},
        {"name": "Customers", "description": "Customer information"},
        {"name": "Orders", "description": "Customer orders"},
        {"name": "Payments", "description": "Customer payments"},
        {"name": "Order Details", "description": "Order line items"},
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "classicmodels"),
        "USER": os.environ.get("MYSQL_USER", "classicuser"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "classicpass"),
        "HOST": os.environ.get("MYSQL_HOST", "localhost"),
        "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
