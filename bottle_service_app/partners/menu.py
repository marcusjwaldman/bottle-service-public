from partners.models import Menu, MenuStatus, MenuItem


def customer_menu(restaurant):
    menu_list = Menu.objects.filter(restaurant=restaurant, status=MenuStatus.APPROVED)
    menu_map = dict()

    for menu in menu_list:
        menu_items = MenuItem.objects.filter(parent_menu=menu)
        for menu_item in menu_items:
            if menu_item.category not in menu_map:
                menu_map[menu_item.category] = list()
            menu_map[menu_item.category].append(menu_item)
    for key, item in menu_map.items():
        item.sort(key=lambda x: x.price)

    return menu_map
