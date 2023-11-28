from django.shortcuts import render, redirect
from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from location.tools import GeoLocation
from .forms import AddressForm, DistributorForm
from .models import Distributor


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_home(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        distributor = user.distributor
        if distributor is not None:
            return render(request, 'distributor/distributor_home.html', {'distributor': distributor,
                                                                         'user': user})
    return render(request, 'distributor/distributor_home.html')


# myapp/views.py


def distributor_profile(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        distributor = user.distributor

    if request.method == 'POST':
        if distributor is not None:
            address_form = AddressForm(request.POST, instance=distributor.address)
            distributor_form = DistributorForm(request.POST, instance=distributor)
        else:
            address_form = AddressForm(request.POST)
            distributor_form = DistributorForm(request.POST)

        if address_form.is_valid() and distributor_form.is_valid():
            address = address_form.save(commit=False)
            geoLocation = GeoLocation()
            latitude, longitude = geoLocation.generate_from_address(address)
            address.latitude = latitude
            address.longitude = longitude
            address.save()
            distributor = distributor_form.save(commit=False)
            distributor.address = address
            distributor.save()

            return redirect('/distributor')
    else:
        if distributor is not None:
            address_form = AddressForm(instance=distributor.address)
            distributor_form = DistributorForm(instance=distributor)
        else:
            address_form = AddressForm()
            distributor_form = DistributorForm()

    return render(request, 'distributor/distributor_profile.html', {'address_form': address_form, 'distributor_form': distributor_form})
