from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from distributor.forms import AddressForm
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.menu import customer_menu
from partners.models import Partners, Menu, MenuItem, MenuStatus
from restaurant.forms import RestaurantForm


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_home(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        restaurant = user.restaurant
        if restaurant is not None:
            partner_list = Partners.objects.filter(restaurant=restaurant)
            return render(request, 'restaurant/restaurant_home.html', {'restaurant': restaurant,
                                                                         'user': user, 'partner_list': partner_list})
    return render(request, 'restaurant/restaurant_home.html')


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_profile(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        restaurant = user.restaurant

    if request.method == 'POST':
        if restaurant is not None:
            address_form = AddressForm(request.POST, instance=restaurant.address)
            restaurant_form = RestaurantForm(request.POST, instance=restaurant)
        else:
            address_form = AddressForm(request.POST)
            restaurant_form = RestaurantForm(request.POST)

        if address_form.is_valid() and restaurant_form.is_valid():
            address = address_form.save(commit=False)
            geoLocation = GeoLocation()
            latitude, longitude = geoLocation.generate_from_address(address)
            address.latitude = latitude
            address.longitude = longitude
            address.save()
            restaurant = restaurant_form.save(commit=False)
            restaurant.address = address
            restaurant.save()

            Partners.objects.filter(restaurant=restaurant).delete()
            partner_match = PartnerMatch()
            partner_list = partner_match.match_restaurant(restaurant)

            return redirect('/restaurant')
    else:
        if restaurant is not None:
            address_form = AddressForm(instance=restaurant.address)
            restaurant_form = RestaurantForm(instance=restaurant)
        else:
            address_form = AddressForm()
            restaurant_form = RestaurantForm()

    return render(request, 'restaurant/restaurant_profile.html',
                  {'address_form': address_form, 'restaurant_form': restaurant_form})


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_menus(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            restaurant = user.restaurant

            menu_list = Menu.objects.filter(restaurant=restaurant, status__in=[MenuStatus.PENDING_RESTAURANT_APPROVAL,
                                                                                MenuStatus.APPROVED])
            return render(request, 'restaurant/restaurant_menus.html', {'user': user,
                                                                          'menu_list': menu_list})


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_view_menu(request, menu_id):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            menu = Menu.objects.get(id=menu_id)
            if menu.restaurant == user.restaurant:
                menu_items = MenuItem.objects.filter(parent_menu=menu)

                return render(request, 'restaurant/restaurant_view_menu.html', {'menu': menu,
                                                                              'menu_items': menu_items})
            else:
                raise Exception('You are not authorized to view this menu')


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_customer_menu(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            menu_map = customer_menu(user.restaurant)
            # menu_list = Menu.objects.filter(restaurant=user.restaurant, status=MenuStatus.APPROVED)
            # menu_map = dict()
            #
            # for menu in menu_list:
            #     menu_items = MenuItem.objects.filter(parent_menu=menu)
            #     for menu_item in menu_items:
            #         if menu_item.category not in menu_map:
            #             menu_map[menu_item.category] = list()
            #         menu_map[menu_item.category].append(menu_item)
            # for key, item in menu_map.items():
            #     item.sort(key=lambda x: x.price)
            return render(request, 'restaurant/restaurant_customer_menu.html',
                          {'restaurant': user.restaurant, 'menu_map': menu_map})
