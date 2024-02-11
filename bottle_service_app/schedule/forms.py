# from django import forms
# from .models import WeeklySchedule, DaySchedule


# class DayScheduleForm(forms.ModelForm):
#     class Meta:
#         model = DaySchedule
#         fields = ['start_time', 'end_time']
#
#
# class WeeklyScheduleForm(forms.ModelForm):
#     class Meta:
#         model = WeeklySchedule
#         fields = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
#
#     # Use DayScheduleForm for each day of the week
#     monday = DayScheduleForm()
#     tuesday = DayScheduleForm()
#     wednesday = DayScheduleForm()
#     thursday = DayScheduleForm()
#     friday = DayScheduleForm()
#     saturday = DayScheduleForm()
#     sunday = DayScheduleForm()
