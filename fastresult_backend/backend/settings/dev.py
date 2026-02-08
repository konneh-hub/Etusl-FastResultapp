"""
Development settings for FastResult backend.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Development-specific middleware (debug_toolbar optional)
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
