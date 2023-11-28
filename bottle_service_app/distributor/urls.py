from django.urls import path
from .views import distributor_home, distributor_profile

urlpatterns = [
    path('', distributor_home, name='distributor_home'),
    path('distributor-profile/', distributor_profile, name='distributor_profile'),
]
