from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.models import Menu, MenuStatus
from schedule.models import WeeklySchedule, create_new_weekly_schedule, DaySchedule, TimeBlock
from schedule.utils import condense_daily_schedule, validate_times, get_daily_schedule


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
            try:
                validate_times(start_time, end_time)
            except ValueError:
                weekly_schedule = get_weekly_schedule(user)
                return render(request, 'schedule/update_schedule.html',
                              {'weekly_schedule': weekly_schedule, 'user': user, 'error': 'Invalid time range'})

            day_schedule = DaySchedule.objects.get(id=request.POST.get('day_id'))
            if day_schedule is not None:
                time_block = TimeBlock.objects.create(start_time=start_time, end_time=end_time,
                                                      day_schedule=day_schedule)

            condense_daily_schedule(day_schedule.id)

            user.refresh_from_db()
            weekly_schedule = get_weekly_schedule(user)
            return render(request, 'schedule/update_schedule.html',
                          {'weekly_schedule': weekly_schedule, 'user': user})


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def delete_time_block_schedule(request, day, time_block_id):
    user = BottleServiceSession.get_user(request)
    if user is not None:

        if request.method == 'GET':
            try:
                time_block = TimeBlock.objects.get(id=time_block_id)
            except TimeBlock.DoesNotExist:
                raise Exception('Time block does not exist')

            user_daily_schedule = user_has_access_to_time_block(user, time_block, day)

            time_block.delete()
            condense_daily_schedule(user_daily_schedule.id)
            return redirect('/schedule/update-schedule/')
        else:
            raise Exception('Invalid method type')


def user_has_access_to_time_block(user, time_block, day):
    weekly_schedule = get_weekly_schedule(user)
    if weekly_schedule is None:
        raise Exception('Weekly schedule does not exist')
    user_daily_schedule = get_daily_schedule(weekly_schedule, day)
    if user_daily_schedule is None:
        raise Exception('Daily schedule does not exist')
    requested_daily_schedule = time_block.day_schedule
    if user_daily_schedule.id != requested_daily_schedule.id:
        raise PermissionDenied('User does not have access to this time block.')
    return user_daily_schedule


def get_weekly_schedule(user):
    if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
        weekly_schedule = WeeklySchedule.objects.get(id=user.distributor.weekly_schedule.id)
    elif user.account_type == BottleServiceAccountType.RESTAURANT:
        weekly_schedule = WeeklySchedule.objects.get(id=user.restaurant.weekly_schedule.id)
    else:
        raise Exception('Invalid account type')
    return weekly_schedule
