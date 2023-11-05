from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from authentication.enums import BottleServiceAccountType
from customer.models import Customer
from distributor.models import Distributor
from restaurant.models import Restaurant


class BottleServiceUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, account_type, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        if not account_type:
            raise ValueError(_("The account type must be set"))
        #
        # if account_type not in [BottleServiceAccountType.ADMIN, BottleServiceAccountType.DISTRIBUTOR,
        #                             BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.CUSTOMER]:
        #     raise ValueError(_("Invalid account type:" + account_type))

        try:
            account_type_obj = BottleServiceAccountType(account_type)
        except ValueError:
            raise ValueError(_("Invalid account type:" + account_type))

        distributor = None
        restaurant = None
        customer = None
        if account_type_obj is BottleServiceAccountType.DISTRIBUTOR:
            distributor = Distributor()
            distributor.save()
        if account_type_obj is BottleServiceAccountType.RESTAURANT:
            restaurant = Restaurant()
            restaurant.save()
        if account_type_obj is BottleServiceAccountType.CUSTOMER:
            customer = (Customer())
            customer.save()

        email = self.normalize_email(email)
        user = self.model(email=email, account_type=account_type_obj, distributor=distributor, restaurant=restaurant,
                          customer=customer, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        return self.create_user(email, BottleServiceAccountType.ADMIN, password, **extra_fields)