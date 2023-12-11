from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_home, name='restaurant_home'),
    path('restaurant-profile', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant-menus', views.restaurant_menus, name='restaurant_menus'),
    path('restaurant-view-menu/<int:menu_id>/', views.restaurant_view_menu, name='restaurant_view_menu'),
    path('restaurant-customer-menu', views.restaurant_customer_menu, name='restaurant_customer_menu'),
]
