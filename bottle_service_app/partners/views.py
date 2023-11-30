from django.shortcuts import render, redirect

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from distributor.forms import AddressForm
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.models import Partners
from restaurant.forms import RestaurantForm


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT, BottleServiceAccountType.DISTRIBUTOR])
def partner_update_status(request, request_type, partner_id):
    user = BottleServiceSession.get_user(request)
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

    referring_page = request.META.get('HTTP_REFERER')

    # Redirect back to the referring page or to a default URL if not available
    return redirect(referring_page or 'default_url')
