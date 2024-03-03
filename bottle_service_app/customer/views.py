from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.security import VerificationCode
from authentication.session import BottleServiceSession
from customer.forms import CustomerForm
from customer.models import Customer
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


def register_customer_email(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Exception('Restaurant does not exist')
    if request.method == 'GET':
        customer_form = CustomerForm()
        return render(request, 'customer/register_customer_email.html', {'restaurant': restaurant,
                                                                   'customer_form': customer_form})
    elif request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        email = customer_form['email'].value()
        verification_code = VerificationCode.generate()
        VerificationCode.store_code(request, verification_code, email)
        VerificationCode.notify_code(request, email, verification_code)
        initial_data = {
                'email': email
            }
        customer_form = CustomerForm(initial=initial_data)
        return render(request, 'customer/register_customer_verification.html',
                      {'restaurant': restaurant, 'customer_form': customer_form})
        # try:
        #     customer = Customer.objects.filter(email=email).first()
        # except Customer.DoesNotExist:
        #     customer = None
        #
        # if customer and customer.verified:
        #     customer_order = BottleServiceSession.get_customer_order(request, restaurant)
        #     customer_order.customer = customer
        #     customer_order.save()
        #     # TODO: Send email to with a verification link or code to verify email of verified customer
        #     return redirect(f'/cart/checkout/{restaurant_id}/')
        # else:
        #     initial_data = {
        #         'email': email
        #     }
        #     customer_form = CustomerForm(initial=initial_data)
        #     return render(request, 'customer/register_customer.html', {'restaurant': restaurant,
        #                                                                'customer_form': customer_form})


def register_customer_verification(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Exception('Restaurant does not exist')

    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        customer_form = CustomerForm(request.POST)
        email = customer_form['email'].value()
        if not VerificationCode.check_code(request, verification_code, email):
            initial_data = {
                'email': email
            }
            customer_form = CustomerForm(initial=initial_data)
            return render(request, 'customer/register_customer_verification.html',
                          {'restaurant': restaurant, 'customer_form': customer_form,
                           'error': 'Invalid verification code'})
        try:
            customer = Customer.objects.filter(email=email).first()
        except Customer.DoesNotExist:
            customer = None

        if customer and customer.verified:
            customer_order = BottleServiceSession.get_customer_order(request, restaurant)
            customer_order.customer = customer
            customer_order.save()
            # TODO: Send email to with a verification link or code to verify email of verified customer
            return redirect(f'/cart/checkout/{restaurant_id}/')
        else:
            initial_data = {
                'email': email
            }
            customer_form = CustomerForm(initial=initial_data)
            return render(request, 'customer/register_customer.html', {'restaurant': restaurant,
                                                                       'customer_form': customer_form})


def register_customer(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Exception('Restaurant does not exist')
    # if request.method == 'GET':
    #     customer_form = CustomerForm()
    #     return render(request, 'customer/register_customer.html', {'restaurant': restaurant,
    #                                                                'customer_form': customer_form})
    if request.method == 'POST':
        customer_order = BottleServiceSession.get_customer_order(request, restaurant)
        customer_form = CustomerForm(request.POST)

        email = customer_form['email'].value()
        last_name = customer_form['last_name'].value()
        first_name = customer_form['first_name'].value()
        if last_name is None or first_name is None or email is None:
            customer_form = CustomerForm()
            return render(request, 'customer/register_customer_email.html', {'restaurant': restaurant,
                                                                             'customer_form': customer_form,
                                                                             'errors': 'Missing required fields'})
        try:
            customer = Customer.objects.filter(email=email).first()
        except Customer.DoesNotExist:
            customer = None
        if customer and customer.verified:
            raise Exception('Customer already verified')
        if customer:
            customer.last_name = last_name
            customer.first_name = first_name
            customer.verified = True
            customer.save()
        else:
            customer = Customer(email=email, last_name=last_name, first_name=first_name)
            customer.verified = True
            customer.save()

        customer_order.customer = customer
        customer_order.save()
        # TODO: Send email to with a verification link or code to verify email
        return redirect(f'/cart/checkout/{restaurant_id}/')
    # Error if request is not GET or POST
    raise Exception('Invalid request')
