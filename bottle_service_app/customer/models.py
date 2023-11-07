from django.db import models


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
