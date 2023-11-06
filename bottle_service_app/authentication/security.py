import os
import django
from django.conf import settings
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bottle_service_app.settings")
django.setup()


default_min_password_length = 8
default_symbols = '!#$%*+-?'
default_verification_code_length = 6
verification_code_key = "verification_code"


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


def generate_random_digit_string(n):
    if n <= 0:
        return ""

    random_string = ''.join(str(random.randint(0, 9)) for _ in range(n))
    return random_string


class VerificationCode:
    @staticmethod
    def check_code(request, code, email):
        stored_code = VerificationCode.retrieve_code(request, email)
        if not stored_code:
            return False
        if stored_code == code:
            return True
        return False

    @staticmethod
    def create_code():
        if settings.VERIFICATION_CODE_LENGTH:
            verification_len = settings.VERIFICATION_CODE_LENGTH
        else:
            verification_len = default_verification_code_length
        return generate_random_digit_string(verification_len)

    # Store verification code in session. User must complete verification from browser without closing it.
    @staticmethod
    def store_code(request, code, email):
        request.session[verification_code_key] = code

    @staticmethod
    def retrieve_code(request, email):
        return request.session.get(verification_code_key, None)

    # Print verification code to console - Future version will send email
    @staticmethod
    def notify_code(request, email, code):
        print('Email: ', email, 'Code: ', code)