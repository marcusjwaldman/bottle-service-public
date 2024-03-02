from django.urls import path
from .views import distributor_home, distributor_profile, distributor_menus, distributor_add_menu, \
    distributor_edit_menu, distributor_view_menu, distributor_delete_menu_item, distributor_delete_item, \
    distributor_edit_items, distributor_edit_item, distributor_stock_item, distributor_view_orders, \
    distributor_update_order

urlpatterns = [
    path('', distributor_home, name='distributor_home'),
    path('distributor-profile/', distributor_profile, name='distributor_profile'),
    path('distributor-menus/', distributor_menus, name='distributor_menus'),
    path('distributor-add-menu/', distributor_add_menu, name='distributor_add_menu'),
    path('distributor-edit-menu/<int:menu_id>/', distributor_edit_menu, name='distributor_edit_menu'),
    path('distributor-view-menu/<int:menu_id>/', distributor_view_menu, name='distributor_view_menu'),
    path('distributor-delete-menu-item/<int:menu_id>/<int:menu_item_id>/', distributor_delete_menu_item,
         name='distributor_delete_menu_item'),
    path('distributor-edit-items/', distributor_edit_items, name='distributor_edit_items'),
    path('distributor-edit-item/<int:item_id>/', distributor_edit_item, name='distributor_edit_item'),
    path('distributor-delete-item/<int:item_id>/', distributor_delete_item, name='distributor_delete_item'),
    path('distributor-stock-item/<int:item_id>/<str:set_stock>/', distributor_stock_item, name='distributor_stock_item'),
    path('distributor-view-orders/', distributor_view_orders,
         name='distributor_view_orders'),
    path('distributor-update-order/<int:order_id>/<str:status>/', distributor_update_order,
         name='distributor_update_order'),
]
