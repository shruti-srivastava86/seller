# flake8: noqa
from .settings import *
import logging

ENVIRONMENT = 'test'

# Cheap testing speedups - explained at
# http://www.daveoncode.com/2013/09/23/effective-tdd-tricks-to-speed-up-django-tests-up-to-10x-faster/
DEBUG = False
TEMPLATE_DEBUG = False
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

MEDIA_ROOT = '/var/sites/app/media/'

APPS_TO_REMOVE = []
MIDDLEWARE_TO_REMOVE = []

INSTALLED_APPS = [i for i in INSTALLED_APPS if i not in APPS_TO_REMOVE]
MIDDLEWARE_CLASSES = [i for i in MIDDLEWARE_CLASSES if i not in MIDDLEWARE_TO_REMOVE]

# disable all migrations when testing to increase speed of tests
DISABLE_MIGRATIONS_FOR = []  # ['auth', 'contenttypes', 'default', 'sessions', 'user']

MIGRATION_MODULES = {k: None for k in DISABLE_MIGRATIONS_FOR}

# Immediately execute celery tasks, don't wait for them to be picked up by a worker
# This allows them to run when executing in CI environment
CELERY_ALWAYS_EAGER = True

# ignore logging in test
logging.disable(logging.CRITICAL)

SESSION_ENGINE = "django.contrib.sessions.backends.file"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'postgres',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

REDIS_HOST = 'redis'
