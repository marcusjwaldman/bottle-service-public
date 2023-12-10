from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from partners.models import Partners, Menu


def update_status(user, request_type, partner_id):
    partner = Partners.objects.get(id=partner_id)
    current_status = partner.status
    if user is not None:
        if user.account_type == BottleServiceAccountType.RESTAURANT:
            if user.restaurant.id != partner.restaurant.id:
                raise Exception("You are not authorized to update this partner")
        if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
            if user.distributor.id != partner.distributor.id:
                raise Exception("You are not authorized to update this partner")

        if request_type == 'match':
            if user.account_type == BottleServiceAccountType.RESTAURANT:
                if current_status == 'matched':
                    partner.status = 'pending_distributor'
                    partner.save()
                else:
                    raise Exception("Partners must be in matched status to be matched")
            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if current_status == 'matched':
                    partner.status = 'pending_restaurant'
                    partner.save()
                else:
                    raise Exception("Partners must be in matched status to be matched")

        if request_type == 'reject':
            if user.account_type == BottleServiceAccountType.RESTAURANT:
                if current_status == 'matched' or current_status == 'pending_restaurant':
                    partner.status = 'rejected_by_restaurant'
                    partner.save()
                else:
                    raise Exception("Partners must be in matched or pending status to be rejected")

            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if current_status == 'matched' or current_status == 'pending_distributor':
                    partner.status = 'rejected_by_distributor'
                    partner.save()
                else:
                    raise Exception("Partners must be in matched or pending status to be rejected")

        if request_type == 'dissolve':
            if current_status == 'approved':
                partner.status = 'matched'
                partner.save()
            else:
                raise Exception("Partners must be in approved status to be dissolved")

        if request_type == 'accept':
            if user.account_type == BottleServiceAccountType.RESTAURANT:
                if current_status == 'pending_restaurant':
                    partner.status = 'approved'
                    partner.save()
                else:
                    raise Exception("Matched must have been requested to by partner to be accepted")

            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if current_status == 'pending_distributor':
                    partner.status = 'approved'
                    partner.save()
                else:
                    raise Exception("Matched must have been requested to by partner to be accepted")

        if request_type == 'cancel':
            if user.account_type == BottleServiceAccountType.RESTAURANT:
                if current_status == 'pending_distributor':
                    partner.status = 'matched'
                    partner.save()
                else:
                    raise Exception("Matched must have been requested to cancel request")

            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if current_status == 'pending_restaurant':
                    partner.status = 'matched'
                    partner.save()
                else:
                    raise Exception("Matched must have been requested to cancel request")

        if request_type == 'reopen':
            if user.account_type == BottleServiceAccountType.RESTAURANT:
                if current_status == 'rejected_by_restaurant':
                    partner.status = 'matched'
                    partner.save()
                else:
                    raise Exception("Matched can only be reopened if rejected by partner")

            if user.account_type == BottleServiceAccountType.DISTRIBUTOR:
                if current_status == 'rejected_by_distributor':
                    partner.status = 'matched'
                    partner.save()
                else:
                    raise Exception("Matched can only be reopened if rejected by partner")


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def partner_update_status(request, request_type, partner_id):
    user = BottleServiceSession.get_user(request)

    update_status(user, request_type, partner_id)

    referring_page = request.META.get('HTTP_REFERER')

    # Redirect back to the referring page or to a default URL if not available
    return redirect(referring_page or 'default_url')


def update_menu_status(user, request_type, menu_id):
    menu = Menu.objects.get(id=menu_id)
    partner = Partners.objects.get(distributor=menu.distributor, restaurant=menu.restaurant)
    if partner is None:
        raise Exception("Partner not found")
    elif partner.status != 'approved':
        raise Exception("Partner not approved")

    current_status = menu.status
    if user is not None:
        user_type = user.account_type
        if request_type == 'submit':
            if user_type == BottleServiceAccountType.DISTRIBUTOR:
                if user.distributor.id != menu.distributor.id:
                    raise Exception("Distributor must own the menu to submit")
                if current_status == 'draft':
                    menu.status = 'pending_restaurant'
                    menu.save()
                else:
                    raise Exception("Menu must be in draft status to be submitted")
            else:
                raise Exception("Users must be distributors to submit a menu")
        if request_type == 'approve':
            if user_type == BottleServiceAccountType.RESTAURANT:
                if user.restaurant.id != menu.restaurant.id:
                    raise Exception("Restaurant must be attached to the menu to submitted to approve")
                if current_status == 'pending_restaurant':
                    menu.status = 'approved'
                    menu.save()
                else:
                    raise Exception("Menu must be pending approval to be approved")
            else:
                raise Exception("Users must be restaurant to approve a menu")
        if request_type == 'reject':
            if user_type == BottleServiceAccountType.RESTAURANT:
                if user.restaurant.id != menu.restaurant.id:
                    raise Exception("Restaurant must be attached to the menu to submitted to reject")
                if current_status == 'pending_restaurant':
                    menu.status = 'rejected_by_restaurant'
                    menu.save()
                else:
                    raise Exception("Menu must be pending approval to be rejected")
            else:
                raise Exception("Users must be restaurant to reject a menu")
        # Menu can be archived by both restaurant and distributor from any status
        if request_type == 'archive':
            account_id = None
            if user_type == BottleServiceAccountType.RESTAURANT:
                account_id = user.restaurant.id
            elif user_type == BottleServiceAccountType.DISTRIBUTOR:
                account_id = user.distributor.id
            if account_id is None or account_id not in [menu.restaurant.id, menu.distributor.id]:
                raise Exception("Restaurant must be attached to the menu to archive a menu")
            menu.status = 'archived'
            menu.save()
        if request_type == 'reopen':
            if user_type == BottleServiceAccountType.DISTRIBUTOR:
                if user.distributor.id != menu.distributor.id:
                    raise Exception("Distributor must be attached to the menu to reopen a menu")
                if current_status != 'draft':
                    menu.status = 'draft'
                    menu.save()
                else:
                    raise Exception("Menu does not need to be reopened when in draft status")
            else:
                raise Exception("Users must be distributor to reopen a menu")


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def menu_update_status(request, request_type, menu_id):
    user = BottleServiceSession.get_user(request)

    update_menu_status(user, request_type, menu_id)

    referring_page = request.META.get('HTTP_REFERER')
    # Redirect back to the referring page or to a default URL if not available
    return redirect(referring_page or 'default_url')

