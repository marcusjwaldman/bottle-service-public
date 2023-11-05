from django.contrib.auth import get_user_model
from django.test import TestCase

from authentication.enums import BottleServiceAccountType


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
