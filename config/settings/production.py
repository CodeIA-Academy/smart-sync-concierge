"""
Production settings for Smart-Sync Concierge.
Inherits from base.py with production-specific security configurations.
"""

import os
from .base import *

# ============================================================================
# SECURITY SETTINGS - PRODUCTION
# ============================================================================

DEBUG = False

# Must be configured for production environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable must be set in production. "
        "Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# Must be configured for specific production domain
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# ============================================================================
# HTTPS & SECURITY
# ============================================================================

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
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
# DATABASE - PRODUCTION
# ============================================================================
# This will be updated to PostgreSQL when scaling beyond MVP

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
    }
}

# Future PostgreSQL configuration (commented for reference):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'smartsync'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'ATOMIC_REQUESTS': True,
#         'CONN_MAX_AGE': 600,
#     }
# }

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

# For serving static files through whitenoise or CDN
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
# - EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# - DEFAULT_FROM_EMAIL: Default email sender
# - ADMIN_EMAIL: Admin email address
#
# Optional:
# - DATABASE_NAME: Path to SQLite database (default: db.sqlite3)
# - REDIS_URL: Redis connection URL for caching
# - AWS_STORAGE_BUCKET_NAME: AWS S3 bucket for media storage
#
# Set DJANGO_SETTINGS_MODULE=config.settings.production before deployment
