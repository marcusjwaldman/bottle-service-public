from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType


@bottle_service_auth(roles=[BottleServiceAccountType.RESTAURANT])
def restaurant_home(request):
    return render(request, 'restaurant/restaurant_home.html')
