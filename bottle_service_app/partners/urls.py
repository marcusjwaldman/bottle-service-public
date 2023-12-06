from django.urls import path
from . import views

urlpatterns = [
    path('update-status/<str:request_type>/<int:partner_id>/', views.partner_update_status,
         name='partner_update_status'),
    path('menu-update-status/<str:request_type>/<int:menu_id>/', views.menu_update_status,
         name='menu_update_status'),
]