from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:menu_item_id>/', views.add_to_cart,
         name='add_to_cart'),
    path('cart/<int:restaurant_id>/', views.cart,
         name='cart'),

]
