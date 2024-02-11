from django.urls import path
from .views import update_schedule, delete_time_block_schedule

urlpatterns = [
    path('update-schedule/', update_schedule, name='update_schedule'),
    path('delete-time-block-schedule/day/<int:day>/time_block_id/<int:time_block_id>/', delete_time_block_schedule,
         name='delete_time_block_schedule'),
]
