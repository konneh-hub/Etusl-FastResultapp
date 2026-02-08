"""
Test configuration for FastResult Backend
"""
import os
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'rest_framework',
            'accounts',
            'universities',
            'academics',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()
