from django.db import models


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