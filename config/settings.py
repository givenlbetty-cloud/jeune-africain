"""
Django settings for BNC (Bibliothèque Numérique) project.
Modern security practices and custom user model.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security & Environment
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ.get("RENDER_EXTERNAL_HOSTNAME"))

# CSRF & Security Configuration
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://0.0.0.0:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://0.0.0.0:8001",
    "https://localhost:8001",
    "https://127.0.0.1:8001",
    "https://0.0.0.0:8001",
    "http://localhost:8003",
    "http://127.0.0.1:8003",
    "http://0.0.0.0:8003",
    "https://localhost:8003",
    "https://127.0.0.1:8003",
    "https://0.0.0.0:8003",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://0.0.0.0:8080",
    "https://localhost:8080",
    "https://127.0.0.1:8080",
    "https://0.0.0.0:8080",
    "https://bug-free-space-palm-tree-gxxwxj7v554h6vr-8000.app.github.dev",
]

if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}")


CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Keep False for Jazzmin admin
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True

# CORS Configuration for mobile apps
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
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
    "django.contrib.sites",  # Required for allauth
    
    # REST Framework
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    
    # Authentication (django-allauth)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.microsoft",
    
    # Third-party
    "import_export",
    "mathfilters",
    
    # Local apps
    "users.apps.UsersConfig",
    "catalogue.apps.CatalogueConfig",
    "catalogue.apps.MediaConfig",
    "catalogue.apps.FinanceConfig",
    "catalogue.apps.EventsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Whitenoise for static files
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Language middleware (MUST be after SessionMiddleware)
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # Required for allauth
    "config.pwa_config.PWAMiddleware",  # PWA support
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
                "django.template.context_processors.i18n",  # i18n context processor
                "catalogue.context_processors.site_configuration",
                "catalogue.context_processors.featured_books",  # CORRECTION #4
                "catalogue.context_processors.site_categories",  # Navigation
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

# Render PostgreSQL Database (Production)
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

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

# Internationalization (i18n)
LANGUAGE_CODE = "fr"  # Default language
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('ar', 'العربية'),
]
TIME_ZONE = "Africa/Dakar"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Locale paths for translations
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Language cookie settings
LANGUAGE_COOKIE_AGE = 31536000  # 1 year
LANGUAGE_COOKIE_SECURE = True
LANGUAGE_COOKIE_HTTPONLY = False  # Must be False for JavaScript access
LANGUAGE_COOKIE_SAMESITE = 'Lax'

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = []
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = BASE_DIR / "staticfiles"

# Storage configuration
STATIC_FILES_BACKEND = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if DEBUG:
    STATIC_FILES_BACKEND = "django.contrib.staticfiles.storage.StaticFilesStorage"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": STATIC_FILES_BACKEND,
    },
}

# Upload Limits (Increased for bulk processing)
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 MB (default 2.5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 MB (default 2.5MB)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        # 'django_filters.rest_framework.DjangoFilterBackend',  # Temporarily disabled
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

# Jazzmin Configuration - SIMPLIFIÉ POUR NON-TECHNICIENS
JAZZMIN_SETTINGS = {
    "site_title": "Administration Calures",
    "site_header": "Bibliothèque Calures",
    "site_brand": "Calures Admin",
    "site_logo": None,  # Utilise le css si null
    "welcome_sign": "Bienvenue dans l'administration Calures",
    "copyright": "Calures Éditions",
    "user_avatar": None,
    
    # ✅ Navigation optimisée
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": False,
    
    # ✅ Icônes professionnelles
    "icons": {
        "users.CustomUser": "fas fa-users",
        
        # Configuration
        "catalogue.SiteConfiguration": "fas fa-cogs",
        
        # Catalogue Principal
        "catalogue.Book": "fas fa-book-open",
        "catalogue.Author": "fas fa-feather-alt",
        "catalogue.Category": "fas fa-tags",
        
        # Médias (Proxies)
        "catalogue.AudiobookProxy": "fas fa-headphones",
        "catalogue.VideoProxy": "fas fa-video",
        "catalogue.PodcastProxy": "fas fa-microphone",
        
        # Gestion
        "catalogue.Payment": "fas fa-credit-card",
        "catalogue.MerchantAccountProxy": "fas fa-university",
        "catalogue.EventProxy": "fas fa-calendar-alt",
        "catalogue.ReadingSession": "fas fa-chart-pie",
        "catalogue.Library": "fas fa-building",
    },
    
    # ✅ Ordre LOGIQUE (Pertinence)
    "order_with_respect_to": [
        # 1. Configuration (Le plus important pour personnaliser)
        "catalogue.SiteConfiguration",
        
        # 2. Le Catalogue (Cœur du métier)
        "catalogue.Book",
        "catalogue.Author",
        "catalogue.Category",
        
        # 3. Les Médias Interactifs
        "catalogue.AudiobookProxy",
        "catalogue.VideoProxy",
        "catalogue.PodcastProxy",
        
        # 4. Utilisateurs & Clients
        "users.CustomUser",
        "catalogue.ReadingSession",
        
        # 5. Finances & Gestion
        "catalogue.Payment",
        "catalogue.MerchantAccountProxy",
        "catalogue.EventProxy",
        "catalogue.Library",
    ],
    
    # ✅ Modèles masqués (bruit visuel)
    "hide_models": [
        "auth.Group",
        "sites.Site",
        "account.EmailAddress",
        "socialaccount.SocialAccount",
        "socialaccount.SocialApp",
        "socialaccount.SocialToken",
        "authtoken.TokenProxy",
        "catalogue.AuthorMedia",
        "catalogue.LibraryBook",
        "catalogue.AuthorBook",
        "catalogue.AuditLog",
        "catalogue.ReaderActivity",
        "catalogue.BookSimilarity",
        "catalogue.UserRecommendation",
        "catalogue.RecommendationStatistic",
        "catalogue.SyncQueue",
        "catalogue.UserRecommendationFeedback",
        # Masquer les modèles originaux remplacés par les proxies
        "catalogue.AudiobookMetadata",
        "catalogue.VideoMaterial",
        "catalogue.Podcast",
        "catalogue.MerchantPaymentAccount",
    ],
    
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "search_model": ["catalogue.Book", "users.CustomUser", "catalogue.Author"],
}

# ✅ Design Professionnel (Thème sombre/bleu "Enterprise")
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-indigo",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-indigo",  # Bleu professionnel foncé
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "main_bg_color": "#f4f6f9",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
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

# Django-allauth Configuration
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # Custom Backend for Phone/OTP Authentication
    'users.authentication.PhoneBackend',
    
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    
    # Social account authentication (handled by provider plugins)
    # No need to specify explicit backends - providers are auto-discovered
]

# Allauth settings (updated to new API)
# Deprecated: ACCOUNT_AUTHENTICATION_METHOD replaced by ACCOUNT_LOGIN_METHODS
ACCOUNT_LOGIN_METHODS = {'email'}
# Deprecated: ACCOUNT_EMAIL_REQUIRED replaced by ACCOUNT_SIGNUP_FIELDS
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Can be 'mandatory', 'optional', or 'none'

# Login URLs
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'

# OAuth Multi-Provider Configuration (Google, Apple, Microsoft)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_OAUTH_SECRET', ''),
            'key': ''
        }
    },
    'apple': {
        'SCOPE': [
            'email',
            'name',
        ],
        'AUTH_PARAMS': {
            'response_mode': 'form_post',
        },
        'APP': {
            'client_id': os.getenv('APPLE_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('APPLE_OAUTH_SECRET', ''),
            'key': os.getenv('APPLE_TEAM_ID', ''),
        },
        'VERIFIED_EMAIL': True,
        'VERSION': 'v1',
    },
    'microsoft': {
        'TENANT': os.getenv('MICROSOFT_TENANT', 'common'),
        'SCOPE': [
            'User.Read',
            'email',
            'profile',
        ],
        'AUTH_PARAMS': {},
        'APP': {
            'client_id': os.getenv('MICROSOFT_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('MICROSOFT_OAUTH_SECRET', ''),
            'key': '',
        },
        'VERIFIED_EMAIL': True,
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

# Social account custom adapter for profile population
# SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'
# Use default adapter temporarily to debug recursion
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# ============================================================================
# PAYMENT GATEWAYS CONFIGURATION
# ============================================================================

# Stripe Configuration
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

# Mobile Money Configuration (Airtel Money, M-Pesa, Orange Money RDC)
AIRTEL_CLIENT_ID = os.getenv('AIRTEL_CLIENT_ID', '')
AIRTEL_CLIENT_SECRET = os.getenv('AIRTEL_CLIENT_SECRET', '')
AIRTEL_PIN = os.getenv('AIRTEL_PIN', '')

MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')

ORANGE_MONEY_API_KEY = os.getenv('ORANGE_MONEY_API_KEY', '')
ORANGE_MONEY_API_SECRET = os.getenv('ORANGE_MONEY_API_SECRET', '')

# Payment Configuration
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
DEFAULT_CURRENCY = 'CDF'  # Francs Congolais
PAYMENT_TIMEOUT_MINUTES = 30  # Délai avant annulation paiement

# Free preview pages (livres payants)
FREE_PREVIEW_PAGES = int(os.getenv('FREE_PREVIEW_PAGES', '30'))
