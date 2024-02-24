from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:menu_item_id>/', views.add_to_cart,
         name='add_to_cart'),
    path('remove-from-cart/<int:menu_item_id>/', views.remove_from_cart,
         name='remove_from_cart'),
    path('cart/<int:restaurant_id>/', views.cart,
         name='cart'),
    path('clear-cart/<int:restaurant_id>/', views.clear_cart,
         name='clear_cart'),

]
