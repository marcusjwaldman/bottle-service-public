from django.shortcuts import render, redirect
from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from location.tools import GeoLocation
from partners.forms import MenuItemForm
from partners.matches import PartnerMatch
from partners.models import Partners, Menu, PartnerStatus, MenuItem
from .forms import AddressForm, DistributorForm
from .models import Distributor


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_home(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        distributor = user.distributor
        if distributor is not None:
            partner_list = Partners.objects.filter(distributor=distributor)
            return render(request, 'distributor/distributor_home.html', {'distributor': distributor,
                                                                         'user': user, 'partner_list': partner_list})
    return render(request, 'distributor/distributor_home.html')


# myapp/views.py


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
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

            Partners.objects.filter(distributor=distributor).delete()
            partner_match = PartnerMatch()
            partner_list = partner_match.match_distributor(distributor)

            return redirect('/distributor')
    else:
        if distributor is not None:
            address_form = AddressForm(instance=distributor.address)
            distributor_form = DistributorForm(instance=distributor)
        else:
            address_form = AddressForm()
            distributor_form = DistributorForm()

    return render(request, 'distributor/distributor_profile.html',
                  {'address_form': address_form, 'distributor_form': distributor_form})


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_menus(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        if request.method == 'GET':
            distributor = user.distributor

            menu_list = Menu.objects.filter(distributor=distributor)
            partners = Partners.objects.filter(distributor=distributor, status=PartnerStatus.APPROVED)
            return render(request, 'distributor/distributor_menus.html', {'user': user,
                                                                          'menu_list': menu_list, 'partners': partners})


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_add_menu(request):
    user = BottleServiceSession.get_user(request)
    if user is not None:
        distributor = user.distributor

        if request.method == 'POST':
            partner_id = request.POST.get('partner')
            delivery_minutes = request.POST.get('delivery_minutes')
            partner = Partners.objects.get(id=partner_id)
            try:
                delivery_minutes = int(delivery_minutes)
                if delivery_minutes < partner.minutes_distance:
                    menu_list = Menu.objects.filter(distributor=distributor)
                    partners = Partners.objects.filter(distributor=distributor, status=PartnerStatus.APPROVED)
                    context = {'error': f'Delivery minutes can not be less than the minimum travel time'
                                        f' between partners of {partner.minutes_distance}', 'user': user,
                               'menu_list': menu_list, 'partners': partners}
                    return render(request, 'distributor/distributor_menus.html', context)
            except (ValueError, TypeError):
                menu_list = Menu.objects.filter(distributor=distributor)
                partners = Partners.objects.filter(distributor=distributor, status=PartnerStatus.APPROVED)
                context = {'error': 'Delivery minutes must be a number', 'user': user,
                           'menu_list': menu_list, 'partners': partners}
                return render(request, 'distributor/distributor_menus.html', context)
            Menu.objects.create(distributor=distributor, restaurant=partner.restaurant,
                                delivery_minutes=delivery_minutes)

    return redirect('/distributor/distributor-menus')


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_edit_menu(request, menu_id):
    user = BottleServiceSession.get_user(request)
    if user is not None:

        if request.method == 'GET':
            menu = Menu.objects.get(id=menu_id)
            menu_items = MenuItem.objects.filter(parent_menu=menu)
            menu_item_form = MenuItemForm()

            return render(request, 'distributor/distributor_edit_menu.html', {'menu': menu,
                                                                              'menu_items': menu_items,
                                                                              'menu_item_form': menu_item_form})

        if request.method == 'POST':
            menu = Menu.objects.get(id=menu_id)
            action = request.POST.get('action')
            if action == 'DELETE':
                menu_item = MenuItem.objects.get(id=request.POST.get('menu_item_id'))
                if menu_item is not None:
                    menu_item.delete()
            else:
                menu_item_form = MenuItemForm(request.POST)
                menu_item = menu_item_form.save(commit=False)
                menu_item.parent_menu = menu
                menu_item.save()

            menu_item_form = MenuItemForm()
            menu_items = MenuItem.objects.filter(parent_menu=menu)
            return render(request, 'distributor/distributor_edit_menu.html', {'menu': menu,
                                                                              'menu_items': menu_items,
                                                                              'menu_item_form': menu_item_form})

    return redirect('/distributor/distributor-menus')
