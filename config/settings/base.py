import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def get_version():
    """Get version from environment variable or default."""
    return os.environ.get("API_VERSION", "4.7.0")


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "0") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Security: Hide sensitive settings in error reports
# These settings will be masked in error traces and debug pages
SECURE_SETTINGS_HIDDEN_VARS = [
    'SECRET_KEY',
    'MYSQL_PASSWORD',
    'DATABASE_URL',
    'API_KEY',
    'PASSWORD',
    'TOKEN',
    'SECRET',
]

# Base path configuration
# All URLs are served under /classic-models base path
# This simplifies reverse proxy configuration (no need to strip prefix)

# Enable support for X-Forwarded-* headers from trusted proxies
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Automatically append trailing slashes to URLs
# This allows URLs to work with or without trailing slashes
APPEND_SLASH = True

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
    "config.middleware.SleepDelayMiddleware",
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
        "authentication.api_key_auth.ApiKeyAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Authentication endpoints
        "login": "50/hour",  # 50 login attempts per hour per IP
        "register": "50/hour",  # 50 registration attempts per hour per IP
        "token_refresh": "100/min",  # 100 token refreshes per minute per user
        "logout": "200/min",  # 200 logout requests per minute per user
        "current_user": "600/min",  # 600 /me requests per minute per user
        # Data endpoints
        "read": "1000/min",  # 1000 read requests per minute per user
        "write": "200/min",  # 200 write requests per minute per user
        "burst": "1000/min",  # 1000 burst requests per minute per user
        "demo_rate_limit": "5/min",  # 5 requests per minute per IP (public demo)
        "oauth_token": "50/hour",  # 50 OAuth token requests per hour per IP
        # Default rates
        "anon": "200/hour",  # Anonymous users
        "user": "1000/min",  # Authenticated users
    },
}


# Get base URL from environment or use default
def get_base_url():
    """Get base URL from environment variable or default to localhost."""
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    # Ensure it doesn't end with a slash
    return base_url.rstrip("/")


SPECTACULAR_SETTINGS = {
    "TITLE": "Classic Models API",
    "DESCRIPTION": (
        "API for the Classic Models tutorial database with multiple authentication options.\n\n"
        "## Authentication Methods\n\n"
        "This API supports three authentication methods:\n\n"
        "### 1. OAuth 2.0 (Authorization Code + PKCE)\n\n"
        "Standards-compliant OAuth 2.0 IDP flow — recommended for third-party application "
        "integrations such as watsonx Orchestrate:\n\n"
        "1. **Register client**: `manage.py create_oauth_client <name> <redirect_uri>`\n"
        "2. **Authorize**: GET `/classic-models/api/oauth/authorize/` — user logs in via browser\n"
        "3. **Exchange code**: POST `/classic-models/api/oauth/token/` — "
        "`grant_type=authorization_code` + PKCE verifier\n"
        "4. **Use token**: `Authorization: Bearer <access_token>`\n"
        "5. **Refresh**: POST `/classic-models/api/oauth/token/` — `grant_type=refresh_token`\n"
        "6. **Revoke**: POST `/classic-models/api/oauth/token/revoke/`\n\n"
        "OIDC discovery: `GET /classic-models/api/auth/.well-known/openid-configuration`\n\n"
        "### 2. JWT Authentication\n\n"
        "Direct user authentication — suitable for first-party clients and testing:\n\n"
        "1. **Login**: POST `/classic-models/api/auth/login/` with username and password\n"
        "2. **Use Token**: `Authorization: Bearer <access_token>`\n"
        "3. **Refresh**: POST `/classic-models/api/oauth/token/` — `grant_type=refresh_token`\n"
        "4. **Logout**: POST `/classic-models/api/auth/logout/`\n\n"
        "### 3. API Key Authentication\n\n"
        "System-level authentication with full admin access (demo purposes):\n\n"
        "- **Header**: `X-API-Key: your-api-key`\n"
        "- **Access**: Full read/write/delete permissions\n"
        "- **Configuration**: Set `API_KEY` environment variable\n"
        "- **Use Case**: Automated scripts, testing, system integrations\n\n"
        "## Base Path\n\n"
        "All endpoints are served at `/classic-models` base path.\n\n"
        "## Public Endpoints\n\n"
        "- API documentation (this page)\n"
        "- Authentication endpoints (`/classic-models/api/auth/`)\n"
        "- OAuth 2.0 endpoints (`/classic-models/api/oauth/`)\n\n"
        "## Protected Endpoints\n\n"
        "- All Classic Models data endpoints (`/classic-models/api/v1/`)\n"
        "- Require either a JWT/OAuth Bearer token OR API key"
    ),
    "VERSION": get_version(),
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "SCHEMA_PATH_PREFIX": "/classic-models/api/",
    "SERVERS": [
        {"url": get_base_url(), "description": "API Server"},
    ],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    "AUTHENTICATION_WHITELIST": [
        "authentication.api_key_auth.ApiKeyAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "TAGS": [
        {"name": "OAuth 2.0", "description": "OAuth 2.0 Authorization Code + PKCE IDP endpoints (RFC 6749, RFC 7636, RFC 7009)"},
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
def _read_optional_file(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return None


JWT_ISSUER = os.environ.get("JWT_ISSUER")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE")
JWT_PRIVATE_KEY_PEM = os.environ.get("JWT_PRIVATE_KEY_PEM") or _read_optional_file(
    os.environ.get("JWT_PRIVATE_KEY_FILE")
)
JWT_PUBLIC_KEY_PEM = os.environ.get("JWT_PUBLIC_KEY_PEM") or _read_optional_file(
    os.environ.get("JWT_PUBLIC_KEY_FILE")
)
JWT_KEY_ID = os.environ.get("JWT_KEY_ID")

# OAuth 2.0 Authorization Code expiry (seconds). Default: 10 minutes.
OAUTH_AUTH_CODE_EXPIRY_SECONDS = int(os.environ.get("OAUTH_AUTH_CODE_EXPIRY_SECONDS", "600"))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "RS256" if (JWT_PRIVATE_KEY_PEM and JWT_PUBLIC_KEY_PEM) else "HS256",
    "SIGNING_KEY": JWT_PRIVATE_KEY_PEM or SECRET_KEY,
    "VERIFYING_KEY": JWT_PUBLIC_KEY_PEM,
    "AUDIENCE": JWT_AUDIENCE,
    "ISSUER": JWT_ISSUER,
    "JWK_URL": None,
    "LEEWAY": int(os.environ.get("JWT_LEEWAY_SECONDS", "0")),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("authentication.jwt_tokens.CustomAccessToken",),
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
