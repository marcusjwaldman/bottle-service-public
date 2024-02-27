from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:menu_item_id>/', views.add_to_cart,
         name='add_to_cart'),
    path('remove-from-cart/<int:menu_item_id>/', views.remove_from_cart,
         name='remove_from_cart'),
    path('cart/<int:restaurant_id>/', views.cart,
         name='cart'),
    path('checkout/<int:restaurant_id>/', views.checkout,
         name='checkout'),
    path('clear-cart/<int:restaurant_id>/', views.clear_cart,
         name='clear_cart'),
    path('process-payment/<int:restaurant_id>/', views.process_payment,
         name='process_payment'),
    path('order-processed/<int:restaurant_id>/', views.order_processed,
         name='order_processed'),
    path('order-confirmed/<int:restaurant_id>/', views.order_confirmed,
         name='order_confirmed'),
    path('order-rejected/<int:restaurant_id>/', views.order_rejected,
         name='order_rejected'),
    path('order-completed/<int:restaurant_id>/', views.order_completed,
         name='order_completed'),

]
