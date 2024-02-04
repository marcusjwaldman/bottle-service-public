from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.models import Menu, MenuStatus
from schedule.forms import WeeklyScheduleForm


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def update_schedule(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                weekly_schedule = user.distributor.weekly_schedule
            elif user.account_type == BottleServiceAccountType.RESTAURANT:
                weekly_schedule = user.restaurant.weekly_schedule
            else:
                raise Exception('Invalid account type')

            weekly_schedule_form = WeeklyScheduleForm(request.POST, instance=weekly_schedule)
            return render(request, 'schedule/update_schedule.html',
                          {'weekly_schedule_form': weekly_schedule_form, user: user})

