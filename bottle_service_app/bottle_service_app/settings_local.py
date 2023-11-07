# Django local settings for bottle_service_app project.
# DJANGO_SETTINGS_MODULE = 'bottle_service_app.settings_local'

from .settings_base import *

PASSWORD_MIN_LENGTH = 4
PASSWORD_MIXED_CASE = True
PASSWORD_DIGITS = True
PASSWORD_SYMBOLS = False
VERIFICATION_CODE_LENGTH = 4
