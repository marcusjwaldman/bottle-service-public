from django.urls import path
from .views import update_schedule

urlpatterns = [
    path('update-schedule/', update_schedule, name='update_schedule'),
]
