# Django local settings for bottle_service_app project.
# DJANGO_SETTINGS_MODULE = 'bottle_service_app.settings_aws'

from .settings_base import *
import os
from bottle_service_app.tools import split_string

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = split_string(os.environ.get('DJANGO_ALLOWED_HOSTS'))

PASSWORD_MIN_LENGTH = 12
PASSWORD_MIXED_CASE = True
PASSWORD_DIGITS = True
PASSWORD_SYMBOLS = False
VERIFICATION_CODE_LENGTH = 6

MAIL_API_KEY = os.environ.get('MAIL_API_KEY')
MAIL_SENDER = os.environ.get('MAIL_SENDER')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'BottleServiceMariaDB',
        'USER': 'bottle_service_account',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'bottle-service-db.cf4q0skejsur.us-east-1.rds.amazonaws.com',   # Use the hostname or IP address of your MariaDB instance
        'PORT': '3306',  # Use the MariaDB port, which is 3306 by default
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
