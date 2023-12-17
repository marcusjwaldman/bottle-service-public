from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.core.exceptions import ValidationError

from authentication.exceptions import AuthenticationMissingException
from authentication.security import PasswordStrength, VerificationCode
from authentication.session import BottleServiceSession
from authentication.views import redirect_to_account_type
from customer.models import Customer
from distributor.models import Distributor
from restaurant.models import Restaurant
from authentication.models import BottleServiceUser
from authentication.managers import BottleServiceUserManager
from authentication.enums import BottleServiceAccountType
import json
import os
import django
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect, render

class BottleServiceUserManagerTests(TestCase):

    def test_create_user(self):
        email = "normal@user.com"
        User = get_user_model()
        user = User.objects.create_user(email=email, account_type="distributor", password="foo")
        self.assertEqual(user.email, email)
        self.assertEqual(user.account_type, BottleServiceAccountType.DISTRIBUTOR)
        self.assertTrue(user.is_active)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", account_type="distributor", password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", account_type="", password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="second@user.com", account_type="", password="foo")

    def test_create_superuser(self):
        email = "super@user.com"
        User = get_user_model()
        admin_user = User.objects.create_superuser(email=email, password="foo")
        self.assertEqual(admin_user.email, email)
        self.assertEqual(admin_user.account_type, BottleServiceAccountType.ADMIN)
        self.assertTrue(admin_user.is_active)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass


class BottleServiceAccountTypeTest(TestCase):
    def test_choices_method(self):
        choices = BottleServiceAccountType.choices()
        expected_choices = [
            ('distributor', 'DISTRIBUTOR'),
            ('restaurant', 'RESTAURANT'),
            ('customer', 'CUSTOMER'),
            ('admin', 'ADMIN'),
        ]
        self.assertEqual(choices, expected_choices)

    def test_equals_string_method(self):
        distributor_type = BottleServiceAccountType.DISTRIBUTOR
        self.assertTrue(distributor_type.equals_string('distributor'))
        self.assertTrue(distributor_type.equals_string('DISTRIBUTOR'))
        self.assertTrue(distributor_type.equals_string('BottleServiceAccountType.DISTRIBUTOR'))
        self.assertFalse(distributor_type.equals_string('invalid_type'))

    def test_invalid_enum_value(self):
        with self.assertRaises(ValueError):
            invalid_type = BottleServiceAccountType('invalid_value')

    def test_enum_value_access(self):
        admin_type = BottleServiceAccountType.ADMIN
        self.assertEqual(admin_type.value, 'admin')
        self.assertEqual(admin_type.name, 'ADMIN')


class BottleServiceUserManagerTest(TestCase):
    def setUp(self):
        # Create instances of related models if needed
        self.distributor = Distributor.objects.create()
        self.restaurant = Restaurant.objects.create()
        self.customer = Customer.objects.create()

    def test_create_user(self):
        manager = BottleServiceUserManager()
        manager.model = BottleServiceUser
        user = manager.create_user(
            email="user@example.com",
            account_type=BottleServiceAccountType.DISTRIBUTOR,
            password="password"
        )

        # Check if the user was created successfully
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.check_password("notpassword"))
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.account_type, BottleServiceAccountType.DISTRIBUTOR)
        self.assertIsNotNone(user.distributor)
        self.assertIsInstance(user.distributor, Distributor)
        self.assertIsNone(user.restaurant)
        self.assertIsNone(user.customer)

    def test_create_superuser(self):
        manager = BottleServiceUserManager()
        manager.model = BottleServiceUser
        superuser = manager.create_superuser(
            email="admin@example.com",
            password="superpassword",
        )

        # Check if the superuser was created successfully
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertEqual(superuser.account_type, BottleServiceAccountType.ADMIN)
        self.assertIsNone(superuser.distributor)
        self.assertIsNone(superuser.restaurant)
        self.assertIsNone(superuser.customer)

    def test_create_user_invalid_account_type(self):
        manager = BottleServiceUserManager()
        manager.model = BottleServiceUser

        # Attempt to create a user with an invalid account type
        with self.assertRaises(ValueError) as context:
            manager.create_user(
                email="user@example.com",
                account_type="invalid_type",
                password="password",
            )

        self.assertIn("Invalid account type:", str(context.exception))

    def test_create_user_missing_email(self):
        manager = BottleServiceUserManager()
        manager.model = BottleServiceUser

        # Attempt to create a user with a missing email
        with self.assertRaises(ValueError) as context:
            manager.create_user(
                email="",
                account_type=BottleServiceAccountType.CUSTOMER.value,
                password="password",
            )

        self.assertIn("The Email must be set", str(context.exception))

    def test_create_user_missing_account_type(self):
        manager = BottleServiceUserManager()
        manager.model = BottleServiceUser

        # Attempt to create a user with a missing account type
        with self.assertRaises(ValueError) as context:
            manager.create_user(
                email="user@example.com",
                account_type="",
                password="password",
            )

        self.assertIn("The account type must be set", str(context.exception))


class BottleServiceUserTest(TestCase):

    def test_create_user(self):
        user = BottleServiceUser.objects.create_user(
            email="user@example.com",
            account_type=BottleServiceAccountType.DISTRIBUTOR.value,
            password="password"
        )

        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.account_type, BottleServiceAccountType.DISTRIBUTOR)
        self.assertIsInstance(user.distributor, Distributor)
        self.assertIsNone(user.restaurant)
        self.assertIsNone(user.customer)

    def test_create_superuser(self):
        superuser = BottleServiceUser.objects.create_superuser(
            email="admin@example.com",
            password="superpassword",
        )

        self.assertEqual(superuser.email, "admin@example.com")
        self.assertEqual(superuser.account_type, BottleServiceAccountType.ADMIN)
        self.assertIsNone(superuser.distributor)
        self.assertIsNone(superuser.restaurant)
        self.assertIsNone(superuser.customer)

    def test_user_string_representation(self):
        user = BottleServiceUser.objects.create_user(
            email="user@example.com",
            account_type=BottleServiceAccountType.CUSTOMER.value,
            password="password",
        )

        expected_str = f'user@example.com - BottleServiceAccountType.{BottleServiceAccountType.CUSTOMER.name} - Active'
        self.assertEqual(str(user), expected_str)


class BottleServiceJSONEncoderTest(TestCase):

    def test_encoder_user(self):
        user = BottleServiceUser.objects.create_user(
            email="user@example.com",
            account_type=BottleServiceAccountType.DISTRIBUTOR.value,
            password="password"
        )

        json_str = json.JSONEncoder().encode(user)
        json_obj = json.loads(json_str)
        self.assertEqual(json_obj['email'], 'user@example.com')
        self.assertEqual(json_obj['account_type']['name'], BottleServiceAccountType.DISTRIBUTOR.name)
        self.assertEqual(json_obj['account_type']['value'], BottleServiceAccountType.DISTRIBUTOR.value)
        self.assertEqual(json_obj['is_active'], True)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bottle_service_app.settings")
django.setup()


class PasswordStrengthTest(TestCase):
    def setUp(self):
        # Set password rules to default values
        settings.PASSWORD_MIN_LENGTH = 1
        settings.PASSWORD_MIXED_CASE = False
        settings.PASSWORD_DIGITS = False
        settings.PASSWORD_SYMBOLS = False

    def test_check_password_min_length(self):
        # Test with a password that doesn't meet the minimum length requirement
        settings.PASSWORD_MIN_LENGTH = 8
        self.assertFalse(PasswordStrength.check_password("short"))

        # Test with a password that meets the minimum length requirement
        self.assertTrue(PasswordStrength.check_password("password1"))

    def test_check_password_mixed_case(self):
        # Test with a password that doesn't have mixed case characters
        settings.PASSWORD_MIXED_CASE = True
        self.assertFalse(PasswordStrength.check_password("lowercase"))

        # Test with a password that has mixed case characters
        self.assertTrue(PasswordStrength.check_password("MixedCase1"))

    def test_check_password_digits(self):
        # Test with a password that doesn't have digits
        settings.PASSWORD_DIGITS = True
        self.assertFalse(PasswordStrength.check_password("nodigits"))

        # Test with a password that has digits
        self.assertTrue(PasswordStrength.check_password("Password123"))

    def test_check_password_symbols(self):
        # Test with a password that doesn't have symbols
        settings.PASSWORD_SYMBOLS = True
        self.assertFalse(PasswordStrength.check_password("nosymbols"))

        # Test with a password that has symbols
        self.assertTrue(PasswordStrength.check_password("Password!"))

    def test_password_rules(self):
        # Set password rules to specific values
        settings.PASSWORD_MIN_LENGTH = 8
        settings.PASSWORD_MIXED_CASE = True
        settings.PASSWORD_DIGITS = True
        settings.PASSWORD_SYMBOLS = True

        expected_rules = {
            'min_length': 8,
            'requires_mixed_case': True,
            'requires_digits': True,
            'requires_symbols': True,
            'symbols': '!#$%*+-?',
        }

        rules = PasswordStrength.password_rules()
        self.assertEqual(rules, expected_rules)

    def test_password_rules_no_symbols(self):
        # Set password rules without symbols
        settings.PASSWORD_MIN_LENGTH = 8
        settings.PASSWORD_MIXED_CASE = True
        settings.PASSWORD_DIGITS = True
        settings.PASSWORD_SYMBOLS = False

        expected_rules = {
            'min_length': 8,
            'requires_mixed_case': True,
            'requires_digits': True,
            'requires_symbols': False,
        }

        rules = PasswordStrength.password_rules()
        self.assertEqual(rules, expected_rules)


class VerificationCodeTest(TestCase):
    def setUp(self):
        # Set the verification code length for testing
        self.old_verification_code_length = settings.VERIFICATION_CODE_LENGTH
        settings.VERIFICATION_CODE_LENGTH = 6


    def tearDown(self):
        # Restore the original verification code length after testing
        settings.VERIFICATION_CODE_LENGTH = self.old_verification_code_length

    def test_generate(self):
        code = VerificationCode.generate()
        self.assertEqual(len(code), settings.VERIFICATION_CODE_LENGTH)

    def test_store_and_retrieve_code(self):
        request = self.client.request().wsgi_request
        email = "test@example.com"
        code = "123456"

        # Store the code in the session
        VerificationCode.store_code(request, code, email)

        # Retrieve the stored code
        retrieved_code = VerificationCode.retrieve_code(request, email)
        self.assertEqual(retrieved_code, code)

    def test_check_code(self):
        request = self.client.request().wsgi_request
        email = "test@example.com"
        code = "123456"

        # Store the code in the session
        VerificationCode.store_code(request, code, email)

        # Check the code against the stored code
        result = VerificationCode.check_code(request, code, email)
        self.assertTrue(result)

    def test_notify_code(self):
        # Redirect the standard output to capture printed text
        import sys
        from io import StringIO
        original_stdout = sys.stdout
        sys.stdout = StringIO()

        email = "test@example.com"
        code = "123456"
        request = self.client.request().wsgi_request

        # Notify the code (this prints to the captured stdout)
        VerificationCode.notify_code(request, email, code)

        # Get the printed text
        printed_text = sys.stdout.getvalue()

        # Restore the original standard output
        sys.stdout = original_stdout

        self.assertIn(email, printed_text)
        self.assertIn(code, printed_text)


class BottleServiceSessionTest(TestCase):
    def setUp(self):
        # Create a user object for testing
        self.user = BottleServiceUser.objects.create_user(
            email="test@example.com",
            account_type=BottleServiceAccountType.DISTRIBUTOR,
            password="testpassword",
        )

    def test_has_user(self):
        request = self.client.request().wsgi_request

        # Ensure there's no user in the session initially
        self.assertFalse(BottleServiceSession.has_user(request))

        # Store the user in the session
        BottleServiceSession.store_user_obj(request, self.user)

        # Check if the user is now in the session
        self.assertTrue(BottleServiceSession.has_user(request))

    def test_get_user(self):
        request = self.client.request().wsgi_request

        # Store the user in the session
        BottleServiceSession.store_user_obj(request, self.user)

        # Retrieve the stored user
        retrieved_user = BottleServiceSession.get_user(request)

        # Check if the retrieved user is the same as the original user
        self.assertEqual(retrieved_user, self.user)

    def test_get_account_type(self):
        request = self.client.request().wsgi_request

        # Ensure there's no user in the session initially
        with self.assertRaises(AuthenticationMissingException):
            BottleServiceSession.get_account_type(request)

        # Store the user in the session
        BottleServiceSession.store_user_obj(request, self.user)

        # Retrieve and check the account type of the stored user
        account_type = BottleServiceSession.get_account_type(request)
        self.assertEqual(account_type, self.user.account_type)

    def test_clear_session(self):
        request = self.client.request().wsgi_request

        # Store the user in the session
        BottleServiceSession.store_user_obj(request, self.user)

        # Ensure the user is in the session
        self.assertTrue(BottleServiceSession.has_user(request))

        # Clear the session
        BottleServiceSession.clear_session(request)

        # Ensure the user is no longer in the session
        self.assertFalse(BottleServiceSession.has_user(request))


class RedirectToAccountTypeTest(TestCase):
    def test_redirect_distributor_enum_type(self):
        # Simulate a request to /distributor
        request = HttpRequest()

        response = redirect_to_account_type(request, BottleServiceAccountType.DISTRIBUTOR)

        # Check if the response is a redirect to /distributor
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for a redirect
        self.assertEqual(response.url, '/distributor/')

    def test_redirect_restaurant_name(self):
        # Simulate a request to /distributor
        request = HttpRequest()

        response = redirect_to_account_type(request, BottleServiceAccountType.RESTAURANT.name)

        # Check if the response is a redirect to /distributor
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for a redirect
        self.assertEqual(response.url, '/restaurant/')

    def test_redirect_admin_value(self):
        # Simulate a request to /distributor
        request = HttpRequest()

        response = redirect_to_account_type(request, BottleServiceAccountType.ADMIN.value)

        # Check if the response is a redirect to /distributor
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for a redirect
        self.assertEqual(response.url, '/administration/')

    def test_redirect_invalid(self):
        # Simulate a request to /distributor
        request = HttpRequest()

        response = redirect_to_account_type(request, 'invalid')

        # Check if the response is a redirect to /distributor
        self.assertEqual(response.status_code, 200)
        response_str = str(response.content)
        self.assertIn('Invalid account type', response_str)
