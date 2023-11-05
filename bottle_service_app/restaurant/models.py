from django.db import models
from location.models import Address


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    address = models.OneToOneField(Address, null=True, on_delete=models.CASCADE)
