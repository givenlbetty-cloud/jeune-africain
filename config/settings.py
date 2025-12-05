"""
Django settings for BNC (Bibliothèque Numérique) project.
Modern security practices and custom user model.
"""

from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security & Environment
SECRET_KEY = "django-insecure-dev-key-change-in-production"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# CSRF & Security Configuration
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://0.0.0.0:8000",
]

CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Keep False for Jazzmin admin
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True

# CORS Configuration for mobile apps
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8100",  # Ionic
    "http://localhost:8081",  # React Native
]

CORS_ALLOW_CREDENTIALS = True

# Application definition - Jazzmin MUST be first
INSTALLED_APPS = [
    # Jazzmin (avant Django admin)
    "jazzmin",
    
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # REST Framework
    "rest_framework",
    "corsheaders",
    
    # Third-party
    "import_export",
    
    # Local apps
    "users.apps.UsersConfig",
    "catalogue.apps.CatalogueConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Auth & Custom User Model
AUTH_USER_MODEL = "users.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "fr-FR"
TIME_ZONE = "Africa/Dakar"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "BNC Admin",
    "site_header": "Bibliothèque Numérique Continentale",
    "site_brand": "BNC",
    "welcome_sign": "Bienvenue à l'administration BNC",
    "user_avatar": None,
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["users", "catalogue"],
    "icons": {
        "users.CustomUser": "fas fa-user",
        "catalogue.Library": "fas fa-building",
        "catalogue.Book": "fas fa-book",
        "catalogue.Author": "fas fa-pen",
        "catalogue.ReadingSession": "fas fa-book-reader",
        "catalogue.Payment": "fas fa-credit-card",
    },
    "default_icon_parents": "fas fa-chevron-right",
    "default_icon_children": "fas fa-arrow-right",
    "search_model": ["users.CustomUser", "catalogue.Book", "catalogue.Author"],
    "toasts_position": "top-right",
    "show_ui_builder": False,
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
