import base64
import os

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from customer.views import customer_restaurant_menu
from distributor.forms import AddressForm
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.menu import customer_menu
from partners.models import Partners, Menu, MenuItem, MenuStatus
from restaurant.forms import RestaurantForm
import qrcode
from io import BytesIO
from django.template import TemplateSyntaxError, VariableDoesNotExist
from django.utils.encoding import force_str
from django import template


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

            return redirect('/restaurant/')
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
            return render(request, 'restaurant/restaurant_customer_menu.html',
                          {'restaurant': user.restaurant, 'menu_map': menu_map})
    else:
        return redirect('/restaurant/')


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def generate_restaurant_menu_qrcode(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        restaurant_id = user.restaurant.id

        base_name = "qrcode_restaurant_" + str(restaurant_id)
        qrcode_image_name = f'{base_name}.png'
        media_root = settings.MEDIA_ROOT + "/"
        full_file_name = media_root + qrcode_image_name
        url_to_embed = request.build_absolute_uri(reverse(customer_restaurant_menu, args=[restaurant_id]))
        if not os.path.isfile(full_file_name):
            print("Generating QR code for restaurant " + str(restaurant_id))
            # Replace 'YOUR_URL_HERE' with the actual URL you want to embed

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url_to_embed)
            qr.make(fit=True)

            # Create an image from the QR code
            img = qr.make_image(fill_color="black", back_color="white")

            # Create a BytesIO buffer
            img.save(full_file_name)

        # Pass the binary data to the template
        context = {'qrcode_image': qrcode_image_name, 'menu_url': url_to_embed, 'restaurant': user.restaurant}
        return render(request, 'restaurant/restaurant_menu_qrcode.html', context)
