"""
Production settings for Smart-Sync Concierge.
Inherits from base.py with production-specific security configurations.
"""

import os
import dj_database_url
from .base import *

# ============================================================================
# SECURITY SETTINGS - PRODUCTION
# ============================================================================

DEBUG = False

# Must be configured for production environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Generate a new one if not provided (should be set in production)
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()

# Must be configured for specific production domain
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]
print(f"[DJANGO] ALLOWED_HOSTS configured: {ALLOWED_HOSTS}")

# ============================================================================
# HTTPS & SECURITY
# ============================================================================

# Enable SSL redirect only if HTTPS is actually configured
# EasyPanel proxies requests, so we need to check X-Forwarded-Proto header
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'",),
    "style-src": ("'self'", "'unsafe-inline'"),
}

# ============================================================================
# CORS SETTINGS - PRODUCTION
# ============================================================================

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'https://api.smartsync.example.com'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# DATABASE - PRODUCTION (PostgreSQL)
# ============================================================================

# Use dj-database-url to configure PostgreSQL from DATABASE_URL environment variable
# DATABASE_URL must be set in production environment
try:
    print(f"[DJANGO] DATABASE_URL value: {os.environ.get('DATABASE_URL', 'NOT SET')[:50] if os.environ.get('DATABASE_URL') else 'NOT SET'}...")
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("[DJANGO] Successfully configured PostgreSQL from DATABASE_URL")
except Exception as e:
    print(f"[DJANGO] Error configuring PostgreSQL: {e}")
    print("[DJANGO] Falling back to SQLite")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================================
# EMAIL CONFIGURATION - PRODUCTION
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@smartsync.example.com')

# ============================================================================
# STATIC FILES - PRODUCTION
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise to serve static files efficiently in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# MEDIA FILES - PRODUCTION
# ============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Consider using S3 or other cloud storage in production:
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# AWS_DEFAULT_ACL = 'public-read'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# ============================================================================
# LOGGING - PRODUCTION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'syslog': {
            'level': 'ERROR',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'syslog'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'syslog'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# CACHE - PRODUCTION
# ============================================================================
# Use Redis or Memcached in production for better performance

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'smart-sync-concierge-cache',
    }
    # Redis example (uncomment to use):
    # {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    #     'OPTIONS': {
    #         'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #         'SOCKET_CONNECT_TIMEOUT': 5,
    #         'SOCKET_TIMEOUT': 5,
    #         'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
    #     }
    # }
}

# ============================================================================
# THROTTLING - PRODUCTION
# ============================================================================

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '60/minute',
    'user': '60/minute',
}

# ============================================================================
# SENTRY / ERROR TRACKING (Optional)
# ============================================================================
# Uncomment and configure if using Sentry for error tracking:
#
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
#
# sentry_sdk.init(
#     dsn=os.environ.get('SENTRY_DSN'),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=0.1,
#     send_default_pii=False
# )

# ============================================================================
# MIDDLEWARE - Add WhiteNoise for production static file serving
# ============================================================================

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# ============================================================================
# REST FRAMEWORK - PRODUCTION PERMISSIONS
# ============================================================================

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.IsAuthenticated',
]

# ============================================================================
# ALLOWED ADMIN USERS
# ============================================================================

ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@smartsync.example.com')),
]

# ============================================================================
# PRODUCTION NOTES
# ============================================================================
# Environment variables required for production:
# - SECRET_KEY: Django secret key
# - ALLOWED_HOSTS: Comma-separated list of allowed hosts
# - CORS_ALLOWED_ORIGINS: Comma-separated list of CORS origins
# - DATABASE_URL: PostgreSQL connection string (required)
# - EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# - DEFAULT_FROM_EMAIL: Default email sender
# - ADMIN_EMAIL: Admin email address
#
# Optional:
# - REDIS_URL: Redis connection URL for caching
# - SENTRY_DSN: Sentry error tracking DSN
#
# Set DJANGO_SETTINGS_MODULE=config.settings.production before deployment
