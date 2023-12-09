from django.urls import path
from .views import distributor_home, distributor_profile, distributor_menus, distributor_add_menu, \
    distributor_edit_menu, distributor_view_menu

urlpatterns = [
    path('', distributor_home, name='distributor_home'),
    path('distributor-profile/', distributor_profile, name='distributor_profile'),
    path('distributor-menus/', distributor_menus, name='distributor_menus'),
    path('distributor-add-menu/', distributor_add_menu, name='distributor_add_menu'),
    path('distributor-edit-menu/<int:menu_id>/', distributor_edit_menu, name='distributor_edit_menu'),
    path('distributor-view-menu/<int:menu_id>/', distributor_view_menu, name='distributor_view_menu'),
]
