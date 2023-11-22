from django.shortcuts import render

from authentication.decorators import bottle_service_auth
from authentication.enums import BottleServiceAccountType


@bottle_service_auth(roles=[BottleServiceAccountType.DISTRIBUTOR])
def distributor_home(request):
    return render(request, 'distributor/distributor_home.html')
