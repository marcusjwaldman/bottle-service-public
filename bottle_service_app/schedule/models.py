from django.db import models
from django.db.models import CheckConstraint, Q

from distributor.models import Distributor, LocomotionType
from restaurant.models import Restaurant
from django.core.exceptions import ValidationError


class DaySchedule(models.Model):
    id = models.AutoField(primary_key=True)


class TimeBlock(models.Model):
    id = models.AutoField(primary_key=True)
    day_schedule = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='time_blocks', null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()


class WeeklySchedule(models.Model):
    id = models.AutoField(primary_key=True)
    monday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='monday', null=True)
    tuesday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='tuesday', null=True)
    wednesday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='wednesday', null=True)
    thursday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='thursday', null=True)
    friday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='friday', null=True)
    saturday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='saturday', null=True)
    sunday = models.ForeignKey(DaySchedule, on_delete=models.CASCADE, related_name='sunday', null=True)
    # Implement time zone at a later date
    # time_zone = models.CharField(max_length=100)


def create_new_weekly_schedule():
    monday = DaySchedule.objects.create()
    tuesday = DaySchedule.objects.create()
    wednesday = DaySchedule.objects.create()
    thursday = DaySchedule.objects.create()
    friday = DaySchedule.objects.create()
    saturday = DaySchedule.objects.create()
    sunday = DaySchedule.objects.create()
    weekly_schedule = WeeklySchedule.objects.create(
        monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday,
        sunday=sunday)
    return weekly_schedule