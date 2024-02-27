from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from customer.forms import CustomerForm
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
        customer_order = BottleServiceSession.get_customer_order(request, restaurant)
        menu_map = customer_menu(restaurant)
        as_of_time = get_current_datetime()
        menu_open = is_within_operational_hours(restaurant.weekly_schedule, as_of_time)
        if menu_open:
            add_open_status_and_quantity_to_menu_item(menu_map, as_of_time, customer_order)
        return render(request, 'customer/restaurant_customer_menu.html',
                      {'restaurant': restaurant, 'menu_map': menu_map, 'menu_open': menu_open,
                       'as_of_time': as_of_time, 'customer_order': customer_order})


def add_open_status_and_quantity_to_menu_item(menu_map, as_of_time, customer_order):
    distributor_map = dict()
    for category, menu_items in menu_map.items():
        for item in menu_items:
            if item.parent_menu.distributor.id not in distributor_map:
                distributor_map[item.parent_menu.distributor.id] = is_within_operational_hours(
                    item.parent_menu.distributor.weekly_schedule, as_of_time)
            item.item_open = distributor_map[item.parent_menu.distributor.id]
            order_item = customer_order.order_item_by_item(item)
            if order_item is None:
                item.quantity = 0
            else:
                item.quantity = order_item.quantity


def register_customer(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Exception('Restaurant does not exist')
    if request.method == 'GET':
        customer_form = CustomerForm()
        return render(request, 'customer/register_customer.html', {'restaurant': restaurant,
                                                                   'customer_form': customer_form})
    elif request.method == 'POST':
        customer_order = BottleServiceSession.get_customer_order(request, restaurant)
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            customer = customer_form.save(commit=False)
            customer.save()
            customer_order.customer = customer
            customer_order.save()
            return redirect(f'/cart/checkout/{restaurant_id}/')
        else:
            return render(request, 'customer/register_customer.html', {'restaurant': restaurant,
                                                                       'customer_form': customer_form,
                                                                       'errors': customer_form.errors})
    # Error if request is not GET or POST
    raise Exception('Invalid request')
