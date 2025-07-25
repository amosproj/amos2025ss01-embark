"""
Django settings for djangoProject project.
Generated by 'django-admin startproject' using Django 3.2.
"""
__copyright__ = 'Copyright 2021-2025 Siemens Energy AG, Copyright 2025 The AMOS Projects'
__author__ = 'Benedikt Kuehne, SirGankalot, ClProsser'
__license__ = 'MIT'

from pathlib import Path
import os
import pytz

from dotenv import load_dotenv

from embark.helper import get_version_strings

# load .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

DOMAIN = "embark.local"
EMAIL_ACTIVE = False

# EMBA stuff
# EMBA location
EMBA_ROOT = os.path.join(BASE_DIR.parent, 'emba')
EMBA_LOG_ROOT = os.path.join(BASE_DIR.parent, 'emba_logs')
EMBA_LOG_URL = 'emba_logs/'

# Application definition - defines what apps gets migrated
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apscheduler',
    'django_bootstrap5',
    'django_tables2',
    'django_celery_beat',
    'mod_wsgi.server',
    'uploader',
    'users',
    'reporter',
    'dashboard',
    'tracker',
    'porter',
    'updater',
    'rest_framework',
    'workers',
    'settings',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'embark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', EMBA_LOG_ROOT],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'settings.context_processors.show_worker_app_processor',
            ],
        },
    },
]

# CSRF and SESSION cookies are:
# 1. separate for now but basically linked (==CSRF_USE_SESSION)
# 2. only active after login

# CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = False  # False since we will grab it via universal-cookies

SESSION_COOKIE_SAMESITE = 'Strict'
# SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

WSGI_APPLICATION = 'embark.wsgi.application'
ASGI_APPLICATION = 'embark.asgi.application'

# Database - uses *.env to configure
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD"),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
        'CONN_MAX_AGE': 300,
        'OPTIONS': {
            # 'threaded': True,
        },
    },
}

# Logging stuff
# ERRORS/WARNINGS->console
# DEBUG->debug.log
# INFO->embark.log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {process:d} {thread:d} {pathname} {levelname} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console_handler': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'debug_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'formatter': 'verbose',
            'filename': BASE_DIR / 'debug.log',
        },
        'info_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': BASE_DIR / 'embark.log',
        },
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': ['info_handler', 'console_handler'],
        },
        'uploader': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'dashboard': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'users': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'reporter': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'tracker': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'porter': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'updater': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'DEBUG',
        },
        'embark': {
            'handlers': ['debug_handler', 'info_handler', 'console_handler'],
            'level': 'INFO',
        },
        'requests': {
            'handlers': ['info_handler'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')
STATICFILES_DIRS = [
    BASE_DIR / 'static/'
]
# STATICFILES_STORAGE
# STATICFILES_FINDERS

# URL of Login-Page
LOGIN_URL = ''

# URL of Logout-Page
LOGOUT_REDIRECT_URL = ''

# Upload Media
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
MEDIA_URL = '/media/'

# Active Firmware
ACTIVE_FW = os.path.join(BASE_DIR.parent, 'active')

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Format string for displaying run time timestamps in the Django admin site. The default
# just adds seconds to the standard Django format, which is useful for displaying the timestamps
# for jobs that are scheduled to run on intervals of less than one minute.
#
# See https://docs.djangoproject.com/en/dev/ref/settings/#datetime-format for format string
# syntax details.
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

# Maximum run time allowed for jobs that are triggered manually via the Django admin site, which
# prevents admin site HTTP requests from timing out.
#
# Longer running jobs should probably be handed over to a background task processing library
# that supports multiple background worker processes instead (e.g. Dramatiq, Celery, Django-RQ,
# etc. See: https://djangopackages.org/grids/g/workers-queues-tasks/ for popular options).
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds

# redis/channel layers setup
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# SSL stuff
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False

VERSION = get_version_strings()

# Worker setup
WORKER_FILES_PATH = os.path.join(BASE_DIR.parent, "WORKER_FILES")
WORKER_UPDATE_CHECK = os.path.join(WORKER_FILES_PATH, "update_check")
WORKER_KEY_LOCATION = os.path.join(WORKER_FILES_PATH, "ssh_keys")
WORKER_SETUP_LOGS = os.path.join(WORKER_FILES_PATH, "logs/worker_setup_{timestamp}.log")
WORKER_EMBA_ROOT = "/root/emba/"
WORKER_FIRMWARE_DIR = "/root/firmware/"
WORKER_EMBA_LOGS = "/root/emba_logs/"
WORKER_UPDATE_QUEUE_SIZE = 50
WORKER_SSH_KEY_SIZE = 2048
WORKER_REACHABLE_TIMEOUT = 10

# Celery task queue
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_TASK_TRACK_STARTED = True
