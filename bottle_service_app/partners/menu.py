from partners.models import Menu, MenuStatus, MenuItem
from restaurant.models import Restaurant


def customer_menu(restaurant):
    if restaurant is None:
        raise TypeError('restaurant cannot be None')
    if not isinstance(restaurant, Restaurant):
        raise TypeError('restaurant must be an instance of Restaurant')

    menu_list = Menu.objects.filter(restaurant=restaurant, status=MenuStatus.APPROVED)
    menu_map = dict()

    for menu in menu_list:
        menu_items = MenuItem.objects.prefetch_related('item').filter(parent_menu=menu)
        for menu_item in menu_items:
            if menu_item.item.category not in menu_map:
                menu_map[menu_item.item.category] = list()
            menu_map[menu_item.item.category].append(menu_item)
    for key, item in menu_map.items():
        item.sort(key=lambda x: x.calculated_price)

    return menu_map


def menus_containing_item(item, active_only=False):
    if active_only:
        menus = Menu.objects.filter(menuitem__item=item, status=MenuStatus.APPROVED)
    else:
        menus = Menu.objects.filter(menuitem__item=item)
    return menus


def add_in_menu_attribute(item, active_only=False):
    item.in_menu = len(menus_containing_item(item, active_only)) > 0
    return item
