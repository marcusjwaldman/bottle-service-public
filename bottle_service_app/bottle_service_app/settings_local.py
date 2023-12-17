# Django local settings for bottle_service_app project.
# DJANGO_SETTINGS_MODULE = 'bottle_service_app.settings_local'
import os

from .settings_base import *

PASSWORD_MIN_LENGTH = 4
PASSWORD_MIXED_CASE = True
PASSWORD_DIGITS = True
PASSWORD_SYMBOLS = False
VERIFICATION_CODE_LENGTH = 4

AUTH_TIMEOUT_MINUTES = 60

MAIL_API_KEY = os.environ.get('MAIL_API_KEY')
MAIL_SENDER = os.environ.get('MAIL_SENDER')

MAP_API_KEY = os.environ.get('MAP_API_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bottle_service_db',
        'USER': 'bottle_service_account',
        'PASSWORD': 'LocalBSpwd$',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
