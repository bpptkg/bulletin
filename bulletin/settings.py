from pathlib import Path

from corsheaders.defaults import default_headers
from decouple import Csv, config
from django.core import exceptions

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS',
                       default='localhost,127.0.0.1', cast=Csv())

STORAGE_DIR = BASE_DIR / 'storage'


PREREQUISITE_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]

PROJECT_APPS = [
    'bulletin.webobs',
]

INSTALLED_APPS = PREREQUISITE_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bulletin.urls'

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

WSGI_APPLICATION = 'bulletin.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME'),
        'HOST': config('DATABASE_HOST', default='127.0.0.1'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'PORT': config('DATABASE_PORT', default=3306, cast=int)
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config('MEMCACHED_LOCATION', default='127.0.0.1:11211'),
    }
}

LOGGING_ROOT = config(
    'LOGGING_ROOT', default=STORAGE_DIR / 'logs')
LOG_LEVEL = config('LOG_LEVEL', default='info').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{asctime} {levelname} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'production': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_ROOT / 'bulletin.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'production'],
            'level': LOG_LEVEL
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATIC_ROOT = config(
    'STATIC_ROOT', default=STORAGE_DIR / 'static')
STATICFILES_DIRS = [
    BASE_DIR / 'bulletin' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=STORAGE_DIR / 'media')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-socket-id',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DATETIME_INPUT_FORMATS': [
        'iso-8601',
        '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
        '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
        '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
        '%Y-%m-%d',              # '2006-10-25'
        '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
        '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
        '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
        '%m/%d/%Y',              # '10/25/2006'
        '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
        '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
        '%m/%d/%y %H:%M',        # '10/25/06 14:30'
        '%m/%d/%y',              # '10/25/06'
    ],
    'DATE_INPUT_FORMATS': [
        'iso-8601',
        '%Y-%m-%d',   # '2006-10-25'
        '%m/%d/%Y',   # '10/25/2006'
        '%m/%d/%y',   # '10/25/06'
        '%b %d %Y',   # 'Oct 25 2006'
        '%b %d, %Y',  # 'Oct 25, 2006'
        '%d %b %Y',   # '25 Oct 2006'
        '%d %b, %Y',  # '25 Oct, 2006'
        '%B %d %Y',   # 'October 25 2006'
        '%B %d, %Y',  # 'October 25, 2006'
        '%d %B %Y',   # '25 October 2006'
        '%d %B, %Y',  # '25 October, 2006'
    ],
    'TIME_INPUT_FORMATS': [
        'iso-8601',
        '%H:%M:%S',     # '14:30:59'
        '%H:%M:%S.%f',  # '14:30:59.000200'
        '%H:%M',        # '14:30'
    ],
}

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json', 'application/x-python-serialize']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

MOCK_SEISCOMP_SERVER = config('MOCK_SEISCOMP_SERVER', default=False, cast=bool)
if not DEBUG and MOCK_SEISCOMP_SERVER:
    raise exceptions.ImproperlyConfigured(
        'You have set MOCK_SEISCOMP_SERVER=True while DEBUG=False. '
        'MOCK_SEISCOMP_SERVER only works in development environment when '
        'DEBUG=True to prevent settings misconfiguration.')

WEBOBS_UPDATE_EVENT_DELAY = config(
    'WEBOBS_UPDATE_EVENT_DELAY', default=10, cast=int)
