"""
Django settings for api project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l+0&3qo7p(5c5@js1e@x)9(4157d6o5o67p#$qno12fsorc1rs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'adminpanel',
    'suit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'corsheaders',

    'seller',
    'seller.authentication',
    'seller.user',
    'seller.eater',
    'seller.vendor',
    'seller.dish',
    'seller.review',
    'seller.chat',
    'seller.purchase',
    'seller.notification',

    'ajax_select',
    'scarface',
    'rest_framework',
    'django_filters',
    'rest_framework_swagger',
    'rest_framework_filters',
    'django_celery_beat',
    'django_celery_results',
    'explorer',
    'crispy_forms',

    'django_pgviews',
    'fcm_django'
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'qinspect.middleware.QueryInspectMiddleware',
    'api.middleware.TimezoneMiddleware',
]

try:
    from api.settings_local import DEBUG_TOOLBAR  # noqa
except ImportError:
    DEBUG_TOOLBAR = False

if DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar', ]
    MIDDLEWARE_CLASSES = [
                             'debug_toolbar.middleware.DebugToolbarMiddleware', ] + MIDDLEWARE_CLASSES
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'api.middleware.show_toolbar',
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, '/seller/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True
        },
    },
]

ROOT_URLCONF = 'api.urls'

WSGI_APPLICATION = 'api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'sellerdb',
        'USER': 'sellerdbuser',
        'PASSWORD': 'seller123!',
        'HOST': '127.0.0.1'
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

USE_SENTRY = False
SENTRY_DSN = 'https://700938fb6a1a0ab1@sentry.xyz.com/10'
ENVIRONMENT = '?'

try:
    from api.settings_local import USE_SENTRY, ENVIRONMENT, SENTRY_DSN
except ImportError:
    print('Warn: Sentry Not Enabled')

if USE_SENTRY:
    import raven  # noqa

    # Get the release number from deploy
    rno = os.path.abspath(os.path.realpath(__file__)).split('/')[5]
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': rno,
        'environment': ENVIRONMENT,
        'ignore_exceptions': [
            'django.security.DisallowedHost',
        ],
    }
    INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
    MIDDLEWARE_CLASSES += ('raven.contrib.django.middleware.SentryMiddleware',)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'seller': {
                'level': 'WARNING',
                'handlers': ['console', 'sentry', ],
            },
            'boto': {
                'level': 'CRITICAL',
                'handlers': ['sentry', 'console', ],
                'propagate': False,
            }
        },
    }

QUERY_INSPECT_ENABLED = False

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

DEFAULT_ADMIN_TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/sites/seller/shared/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/var/sites/seller/shared/uploads/'

MEDIA_URL = '/uploads/'

# REST Framework
# http://www.django-rest-framework.org/#installation

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.generics.authentication.TokenAuthentication',
    ),
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%SZ",
    'PAGE_SIZE': 10,

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    # 'EXCEPTION_HANDLER': 'api.generics.exception_handler.custom_exception_handler'
}

CRISPY_TEMPLATE_PACK = 'bootstrap'

AUTH_USER_MODEL = 'user.User'

LOGIN_URL = "/admin/login"

BASE_URL = 'http://192.168.56.111'

WEB_BASE_URL = 'http://192.168.56.111'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_SEARCH_RANGE_IN_MILES = 10
DEFAULT_SRID = 4326

GUEST_AUTH_TOKEN = 'GUESTAUTHTOKEN'

SCARFACE_PLATFORM_STRATEGIES = [
    # Note: Until a PR on scarface is merged, this is a hacky way to get
    # mutable-content working
    'seller.notification.platform_strategy.ApplePlatformStrategy',
    'seller.notification.platform_strategy.AppleSandboxPlatformStrategy',
]

ENVIRONMENT = None

try:
    from api.settings_local import CACHALOT_ENABLED
except ImportError:
    CACHALOT_ENABLED = False

if CACHALOT_ENABLED:
    INSTALLED_APPS += ['cachalot', ]

# celery setup
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json', 'yaml']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ALWAYS_EAGER = True

try:
    from api.settings_local import *  # noqa
except ImportError:
    pass

if ENVIRONMENT in ['Local', 'Vagrant', 'Dev'] and DEBUG:
    INSTALLED_APPS += ('silk',)
    MIDDLEWARE_CLASSES += ('silk.middleware.SilkyMiddleware',)

# explorer
EXPLORER_CONNECTIONS = {'Default': 'readonly'}
EXPLORER_DEFAULT_CONNECTION = 'readonly'

# Django Templated Email
DOMAIN = BASE_URL.split('://')[1]
