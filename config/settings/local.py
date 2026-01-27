"""
Local development settings for Smart-Sync Concierge.
Inherits from base.py with development-specific overrides.
"""

from .base import *

# ============================================================================
# DEBUG SETTINGS
# ============================================================================

DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# ============================================================================
# SECRET KEY
# ============================================================================
# Safe to use a development key here since this file should never be in production

SECRET_KEY = 'django-insecure-dev-key-9w5u-7y3q-4x2z-8k6m-9p0o-local-only'

# ============================================================================
# CORS SETTINGS FOR DEVELOPMENT
# ============================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5000",
]

CORS_ALLOW_CREDENTIALS = True

# Allow all origins in development (ONLY FOR DEVELOPMENT!)
# CORS_ALLOW_ALL_ORIGINS = True  # Uncomment if needed for quick testing

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
# Use console backend in development to see emails in terminal

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================================================
# DJANGO EXTENSIONS (Optional)
# ============================================================================

# Uncomment the following if you install django-extensions
# try:
#     INSTALLED_APPS.insert(0, 'django_extensions')
# except:
#     pass

# ============================================================================
# LOGGING FOR DEVELOPMENT
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ============================================================================
# DEVELOPMENT TOOLS
# ============================================================================

# Rest Framework settings for development
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Include browsable API
    ],
}

# ============================================================================
# STATIC FILES
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ============================================================================
# MEDIA FILES
# ============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================
# Simple in-memory cache for development

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'smart-sync-concierge-cache',
    }
}

# ============================================================================
# SECURITY SETTINGS FOR DEVELOPMENT
# ============================================================================
# Relaxed security settings for development

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ============================================================================
# THROTTLING DISABLED FOR DEVELOPMENT
# ============================================================================

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/hour',  # Very high limit for development
    'user': '10000/hour',  # Very high limit for development
}

# ============================================================================
# INTERNAL IPS (For Django Debug Toolbar)
# ============================================================================

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# ============================================================================
# DEVELOPMENT NOTES
# ============================================================================
# This is the default settings file for development.
# Set DJANGO_SETTINGS_MODULE=config.settings.local (default in manage.py)
#
# Common development commands:
# - python manage.py runserver
# - python manage.py migrate
# - python manage.py createsuperuser
# - python manage.py shell
# - python manage.py dbshell
