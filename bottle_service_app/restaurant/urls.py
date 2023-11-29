from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_home, name='restaurant_home'),
    path('restaurant-profile', views.restaurant_profile, name='restaurant_profile'),
]
