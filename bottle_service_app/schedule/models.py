from django.db import models
from django.db.models import CheckConstraint, Q

from distributor.models import Distributor, LocomotionType
from restaurant.models import Restaurant
from django.core.exceptions import ValidationError


# class Weekday(models.Choices):
#     MONDAY = 1
#     TUESDAY = 2
#     WEDNESDAY = 3
#     THURSDAY = 4
#     FRIDAY = 5
#     SATURDAY = 6
#     SUNDAY = 7


class DaySchedule(models.Model):
    id = models.AutoField(primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()


class WeeklySchedule(models.Model):
    id = models.AutoField(primary_key=True)
    monday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='monday')
    tuesday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='tuesday')
    wednesday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='wednesday')
    thursday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='thursday')
    friday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='friday')
    saturday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='saturday')
    sunday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='sunday')
    # Implement time zone at a later date
    # time_zone = models.CharField(max_length=100)
