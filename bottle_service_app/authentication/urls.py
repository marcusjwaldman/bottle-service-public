from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('account-creation', views.account_creation, name='account_creation'),
]