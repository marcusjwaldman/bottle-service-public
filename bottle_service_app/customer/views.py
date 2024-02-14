from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.menu import customer_menu
from restaurant.models import Restaurant
from schedule.utils import get_current_datetime, is_within_operational_hours


@bottle_service_auth(roles=[BottleServiceAccountType.CUSTOMER])
def customer_home(request):
    return render(request, 'customer/customer_home.html')


def customer_restaurant_menu(request, restaurant_id):
    if request.method == 'GET':
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise Exception('Restaurant does not exist')
        menu_map = customer_menu(restaurant)
        as_of_time = get_current_datetime()
        menu_open = is_within_operational_hours(restaurant.weekly_schedule, as_of_time)
        if menu_open:
            add_open_status_to_menu_item(menu_map, as_of_time)
        return render(request, 'customer/restaurant_customer_menu.html',
                      {'restaurant': restaurant, 'menu_map': menu_map, 'menu_open': menu_open,
                       'as_of_time': as_of_time})


def add_open_status_to_menu_item(menu_map, as_of_time):
    distributor_map = dict()
    for category, menu_items in menu_map.items():
        for item in menu_items:
            if item.parent_menu.distributor.id not in distributor_map:
                distributor_map[item.parent_menu.distributor.id] = is_within_operational_hours(
                    item.parent_menu.distributor.weekly_schedule, as_of_time)
            item.item_open = distributor_map[item.parent_menu.distributor.id]

