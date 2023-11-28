from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from distributor.forms import AddressForm
from location.tools import GeoLocation
from restaurant.forms import RestaurantForm


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_home(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        restaurant = user.restaurant
        if restaurant is not None:
            return render(request, 'restaurant/restaurant_home.html', {'restaurant': restaurant,
                                                                         'user': user})
    return render(request, 'restaurant/restaurant_home.html')


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
