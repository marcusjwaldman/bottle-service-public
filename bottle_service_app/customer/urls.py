from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_home, name='customer_home'),
    path('customer-restaurant-menu/<int:restaurant_id>/', views.customer_restaurant_menu,
         name='customer_restaurant_menu'),
    path('register-customer/<int:restaurant_id>/', views.register_customer,
         name='register_customer'),

]
