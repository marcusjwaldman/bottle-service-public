from django.urls import path
from . import views

urlpatterns = [
    path('', views.distributor_home, name='distributor_home'),
]
