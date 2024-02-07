from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.models import Menu, MenuStatus
from schedule.models import WeeklySchedule, create_new_weekly_schedule, DaySchedule, TimeBlock


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def update_schedule(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if user.distributor.weekly_schedule is None:
                    user.distributor.weekly_schedule = create_new_weekly_schedule()
                    user.distributor.save()
                weekly_schedule = user.distributor.weekly_schedule
            elif user.account_type == BottleServiceAccountType.RESTAURANT:
                if user.restaurant.weekly_schedule is None:
                    user.restaurant.weekly_schedule = create_new_weekly_schedule()
                    user.restaurant.save()
                weekly_schedule = user.restaurant.weekly_schedule
            else:
                raise Exception('Invalid account type')

            return render(request, 'schedule/update_schedule.html',
                          {'weekly_schedule': weekly_schedule, 'user': user})

        elif request.method == 'POST':
            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if user.distributor.weekly_schedule is None:
                    user.distributor.weekly_schedule = create_new_weekly_schedule()
                    user.distributor.save()
            elif user.account_type == BottleServiceAccountType.RESTAURANT:
                if user.restaurant.weekly_schedule is None:
                    user.restaurant.weekly_schedule = create_new_weekly_schedule()
                    user.restaurant.save()
            else:
                raise Exception('Invalid account type')

            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            day_schedule = DaySchedule.objects.get(id=request.POST.get('day_id'))
            if day_schedule is not None:
                time_block = TimeBlock.objects.create(start_time=start_time, end_time=end_time,
                                                      day_schedule=day_schedule)
            user.refresh_from_db()
            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                weekly_schedule = WeeklySchedule.objects.get(id=user.distributor.weekly_schedule.id)
            elif user.account_type == BottleServiceAccountType.RESTAURANT:
                weekly_schedule = WeeklySchedule.objects.get(id=user.restaurant.weekly_schedule.id)
            else:
                raise Exception('Invalid account type')
            return render(request, 'schedule/update_schedule.html',
                          {'weekly_schedule': weekly_schedule, 'user': user})
