"""
Django Settings for Mental Health Anonymous Support Platform
============================================================
This file configures the entire Django backend including:
- MySQL database connection
- JWT Authentication
- Django Channels (WebSockets)
- CORS settings
- Installed apps
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config
from decouple import Config, RepositoryEnv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from decouple import AutoConfig
config = AutoConfig()
# ─────────────────────────────────────────────────────────────────
# BASE CONFIGURATION
# ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Keep secret key in environment variable, never hardcode it
SECRET_KEY = config('SECRET_KEY', default='your-super-secret-key-change-in-production')

# SECURITY: Set to False in production
DEBUG = config('DEBUG', default=True, cast=bool)

# In production, replace '*' with your actual domain
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')


# ─────────────────────────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',            # Django REST Framework for APIs
    'rest_framework_simplejwt',  # JWT Authentication
    'corsheaders',               # Allow React frontend to call our APIs
    'channels',                  # WebSocket support for real-time chat

    # Our custom apps
    'apps.users',     # Anonymous user management
    'apps.chat',      # Real-time chat rooms & messages
    'apps.mood',      # Daily mood tracking
    'apps.emergency', # Emergency keyword detection
    'apps.chatbot',   # AI chatbot integration
]


# ─────────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be FIRST for CORS to work
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mental_health_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Django Channels replaces the default WSGI with ASGI for WebSocket support
ASGI_APPLICATION = 'mental_health_project.asgi.application'


# ─────────────────────────────────────────────────────────────────
# DATABASE - MYSQL CONFIGURATION
# ─────────────────────────────────────────────────────────────────
# We use MySQL instead of the default SQLite for production readiness
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # MySQL engine
        'NAME': config('DB_NAME', default='mental_health_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='db'),     # 'db' is the Docker service name
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',  # Support emojis and special characters
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# ─────────────────────────────────────────────────────────────────
# DJANGO CHANNELS - REDIS CHANNEL LAYER
# ─────────────────────────────────────────────────────────────────
# Redis acts as a message broker for WebSocket messages
# When User A sends a message, Redis routes it to User B's connection
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}


# ─────────────────────────────────────────────────────────────────
# DJANGO REST FRAMEWORK CONFIGURATION
# ─────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    # Use JWT tokens for all API authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # All endpoints require authentication by default
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Pagination: return 20 items per page for performance
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Throttling (Rate Limiting) to prevent abuse
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}


# ─────────────────────────────────────────────────────────────────
# JWT CONFIGURATION
# ─────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    # Access token expires in 7 days (user stays logged in longer since anonymous)
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    # Refresh token expires in 30 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    # We use 'user_id' which maps to UUID in our custom user model
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# ─────────────────────────────────────────────────────────────────
# CORS CONFIGURATION (Cross-Origin Resource Sharing)
# ─────────────────────────────────────────────────────────────────
# This allows our React frontend (running on port 3000) to call our Django APIs (port 8000)
CORS_ALLOWED_ORIGINS = [
    "https://mental-health-platform-puce.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ─────────────────────────────────────────────────────────────────
# AUTHENTICATION - Custom Anonymous User Model
# ─────────────────────────────────────────────────────────────────
# We replace Django's default User model with our custom AnonymousUser
AUTH_USER_MODEL = 'users.AnonymousUser'


# ─────────────────────────────────────────────────────────────────
# OPENAI CONFIGURATION
# ─────────────────────────────────────────────────────────────────
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# ─────────────────────────────────────────────────────────────────
# STATIC AND MEDIA FILES
# ─────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────────────────────────
# LOGGING CONFIGURATION
# ─────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
# Production Database (PostgreSQL on Render)
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

