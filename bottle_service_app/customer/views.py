from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType


@bottle_service_auth(roles=[BottleServiceAccountType.CUSTOMER])
def customer_home(request):
    return render(request, 'customer/customer_home.html')