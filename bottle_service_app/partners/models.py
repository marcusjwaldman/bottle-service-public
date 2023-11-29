from django.db import models
from django.db.models import CheckConstraint, Q

from distributor.models import Distributor, LocomotionType
from restaurant.models import Restaurant


class PartnerStatus(models.Choices):
    MATCHED = 'matched'
    PENDING_DISTRIBUTOR_APPROVAL = 'pending_distributor'
    PENDING_RESTAURANT_APPROVAL = 'pending_restaurant'
    APPROVED = 'approved'
    REJECTED_BY_DISTRIBUTOR = 'rejected_by_distributor'
    REJECTED_BY_RESTAURANT = 'rejected_by_restaurant'


class Partners(models.Model):
    id = models.AutoField(primary_key=True)
    distributor = models.OneToOneField(Distributor, on_delete=models.CASCADE)
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=PartnerStatus.choices, default=PartnerStatus.MATCHED)
    locomotion = models.CharField(max_length=20, choices=LocomotionType.choices)
    minutes_distance = models.IntegerField()

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(minutes_distance__gt=0),
                name='partner_minutes_distance_positive_constraint'
            )
        ]
