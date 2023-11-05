import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bottle_service_app.settings")
django.setup()


default_min_password_length = 8
default_symbols = '!#$%*+-?'


# Class enforces password requirements
class PasswordStrength:
    @staticmethod
    def check_password(password):
        if settings.PASSWORD_MIN_LENGTH:
            min_password_length = settings.PASSWORD_MIN_LENGTH
        else:
            min_password_length = default_min_password_length

        if len(password) < min_password_length:
            return False

        if settings.PASSWORD_MIXED_CASE:
            if not (any(char.isupper() for char in password) and any(char.islower() for char in password)):
                return False
        if settings.PASSWORD_DIGITS:
            if not any(char.isdigit() for char in password):
                return False
        if settings.PASSWORD_SYMBOLS:
            if not any(char in default_symbols for char in password):
                return False
        return True

    @staticmethod
    def password_rules():
        rules = {
            'min_length': settings.PASSWORD_MIN_LENGTH,
            'requires_mixed_case': settings.PASSWORD_MIXED_CASE,
            'requires_digits': settings.PASSWORD_DIGITS,
            'requires_symbols': settings.PASSWORD_SYMBOLS,
            }
        if settings.PASSWORD_SYMBOLS:
            rules['symbols'] = default_symbols
        return rules
