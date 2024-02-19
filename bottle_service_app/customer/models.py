from django.db import models
from django.utils import timezone


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)


