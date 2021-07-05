import os
import sys

from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
RUN_DIR = os.path.join(STORAGE_DIR, 'run')
MSD_DIR = os.path.join(STORAGE_DIR, 'msd')
LOG_DIR = os.path.join(STORAGE_DIR, 'logs')

DEBUG = config('DEBUG', default=False, cast=bool)

DATABASE_ENGINE = config('DATABASE_ENGINE')
MIGRATED = config('MIGRATED', default=True, cast=bool)
MSD_EXT = '.msd'

TIMEZONE = config('TIMEZONE', default='Asia/Jakarta')

LOGGING_ROOT = LOG_DIR
LOG_LEVEL = config('LOG_LEVEL', default='info').upper()

if DEBUG:
    LOG_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{asctime} {levelname} {name} {process:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'production': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'bulletin.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'production'],
            'level': LOG_LEVEL
        },
        '__main__': {
            'handlers': ['console', 'production'],
            'level': LOG_LEVEL,
            'propagate': False,
        }
    }
}

LOCKFILE = os.path.join(DATA_DIR, 'bulletin.lock')

SEEDLINK_HOST = config('SEEDLINK_HOST', default='localhost')
SEEDLINK_PORT = config('SEEDLINK_PORT', default=18000, cast=int)
ARCLINK_HOST = config('ARCLINK_HOST', default='localhost')
ARCLINK_PORT = config('ARCLINK_PORT', default=18001, cast=int)