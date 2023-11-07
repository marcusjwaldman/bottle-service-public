from django.utils import timezone

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin

from authentication.enums import BottleServiceAccountType
from authentication.managers import BottleServiceUserManager
from distributor.models import Distributor
from restaurant.models import Restaurant
from customer.models import Customer
import json


class BottleServiceUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    account_type = models.CharField(max_length=50, choices=[(choice.value, choice.name) for choice in
                                                            BottleServiceAccountType])
    # account_type = models.IntegerField(choices=BottleServiceAccountType.choices())
    # If of type distributor must have a distributor
    distributor = models.ForeignKey(Distributor, null=True, blank=True, on_delete=models.CASCADE)
    # If of type restaurant must have a restaurant
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.CASCADE)
    # If of type customer must have a customer
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)

    account_created = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BottleServiceUserManager()

    def __str__(self):
        return f'{self.email} - {self.account_type} - {'Active' if self.is_active else "Inactive"}'


class BottleServiceJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BottleServiceUser):
            return {
                'account_type': self.account_type,
                'email': self.email,
                'is_active': self.is_active,
                'account_created': self.account_created
            }
        return super().default(obj)


json.JSONEncoder = BottleServiceJSONEncoder
