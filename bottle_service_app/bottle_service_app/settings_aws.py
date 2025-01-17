# Django local settings for bottle_service_app project.

from .settings_base import *
import os
from bottle_service_app.tools import split_string

# Implement when SSL is ready
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = split_string(os.environ.get('DJANGO_ALLOWED_HOSTS'))

PASSWORD_MIN_LENGTH = 12
PASSWORD_MIXED_CASE = True
PASSWORD_DIGITS = True
PASSWORD_SYMBOLS = False
VERIFICATION_CODE_LENGTH = 6
CONFIRMATION_CODE_LENGTH = 8

AUTH_TIMEOUT_MINUTES = os.environ.get('AUTH_TIMEOUT_MINUTES')

MAIL_API_KEY = os.environ.get('MAIL_API_KEY')
MAIL_SENDER = os.environ.get('MAIL_SENDER')

MAP_API_KEY = os.environ.get('MAP_API_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'BottleServiceMariaDB',
        'USER': 'bottle_service_account',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': '<db_hostname>',   # Use the hostname or IP address of your MariaDB instance
        'PORT': '3306',  # Use the MariaDB port, which is 3306 by default
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')