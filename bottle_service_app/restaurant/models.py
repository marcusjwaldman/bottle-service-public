from django.db import models
from django.db.models import CheckConstraint, Q

from location.models import Address


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    address = models.OneToOneField(Address, null=True, on_delete=models.CASCADE)
    minutes_distance = models.IntegerField(null=True)


    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(minutes_distance__gt=0) | Q(minutes_distance__isnull=True),
                name='restaurant_minutes_distance_positive_constraint'
            )
        ]

    def __str__(self):
        return f'Restaurant - {self.id} - {self.name}'
