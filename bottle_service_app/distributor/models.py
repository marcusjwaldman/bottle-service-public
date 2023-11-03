from django.db import models
from enum import Enum
from enumfields import EnumField


class DistributorStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return str([self.address, self.city, self.state, self.zip])


class Distributor(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    status = EnumField(DistributorStatus, default=DistributorStatus.ACTIVE)

    def __str__(self):
        return self.name
