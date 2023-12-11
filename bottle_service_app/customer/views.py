from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.menu import customer_menu
from restaurant.models import Restaurant


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
        return render(request, 'restaurant/restaurant_customer_menu.html',
                      {'restaurant': restaurant, 'menu_map': menu_map})
