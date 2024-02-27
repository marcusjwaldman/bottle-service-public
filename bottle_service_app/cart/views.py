from django.http import Http404
from django.shortcuts import render, redirect

from authentication.session import BottleServiceSession
from cart.models import OrderItem
from partners.models import MenuItem
from restaurant.models import Restaurant


# Create your views here.
def add_to_cart(request, menu_item_id):
    try:
        menu_item = MenuItem.objects.get(pk=menu_item_id)
    except MenuItem.DoesNotExist:
        raise Http404(f"Menu item {menu_item_id} does not exist")
    customer_order = BottleServiceSession.get_customer_order(request, menu_item.parent_menu.restaurant)
    item = menu_item.item
    if customer_order.distributor is not None:
        if menu_item.item.distributor != customer_order.distributor:
            raise Http404(f"Menu item {menu_item_id} does not belong to distributor {customer_order.distributor}")
    else:
        customer_order.distributor = menu_item.item.distributor
        customer_order.save()

    order_items = customer_order.order_items.all()
    order_item = get_matching_order_item(order_items, menu_item)
    if order_item is not None:
        order_item.quantity += 1
        order_item.save()
        customer_order.total_cost += order_item.customer_price
        customer_order.save()
    else:
        order_item = OrderItem.objects.create(order=customer_order, item=item, customer_price=menu_item.calculated_price)
        customer_order.order_items.add(order_item)
        customer_order.total_cost += order_item.customer_price
        customer_order.save()

    return redirect(f'/customer/customer-restaurant-menu/{customer_order.restaurant.id}/')


def remove_from_cart(request, menu_item_id):
    try:
        menu_item = MenuItem.objects.get(pk=menu_item_id)
    except MenuItem.DoesNotExist:
        raise Http404(f"Menu item {menu_item_id} does not exist")
    customer_order = BottleServiceSession.get_customer_order(request, menu_item.parent_menu.restaurant)

    order_items = customer_order.order_items.all()
    order_item = get_matching_order_item(order_items, menu_item)
    if order_item is not None:
        customer_order.total_cost -= order_item.customer_price
        customer_order.save()
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            customer_order.order_items.remove(order_item)
            order_item.delete()
            if len(order_items) == 1:
                customer_order.distributor = None
                customer_order.total_cost = 0
                customer_order.save()
    return redirect(f'/customer/customer-restaurant-menu/{customer_order.restaurant.id}/')


def get_matching_order_item(order_items, menu_item):
    for order_item in order_items:
        if order_item.item == menu_item.item:
            return order_item
    return None

def cart(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")
    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    order_items = customer_order.order_items.all()
    return render(request, 'cart/cart.html', {'cart_items': order_items, 'restaurant': restaurant,
                                              'customer_order': customer_order})


def clear_cart(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")
    BottleServiceSession.clear_cart(request)
    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    order_items = customer_order.order_items.all()
    return render(request, 'cart/cart.html', {'cart_items': order_items, 'restaurant': restaurant,
                                              'customer_order': customer_order})


def checkout(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")

    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    customer = customer_order.customer
    if customer is None:
        return redirect(f'/customer/register-customer/{restaurant_id}/')

    if customer_order.order_status == 'shopping':
        return redirect(f'/cart/process-payment/{restaurant_id}/')
    if customer_order.order_status == 'payment-denied':
        return redirect(f'/cart/process-payment/{restaurant_id}/')
    if customer_order.order_status == 'payment-approved':
        return redirect(f'/cart/order-processed/{restaurant_id}/')
    if customer_order.order_status == 'confirmed':
        return redirect(f'/cart/order-confirmed/{restaurant_id}/')
    if customer_order.order_status == 'rejected':
        return redirect(f'/cart/order-rejected/{restaurant_id}/')
    if customer_order.order_status == 'completed':
        return redirect(f'/cart/order-completed/{restaurant_id}/')

    BottleServiceSession.clear_cart(request)
    return redirect(f'/customer/customer-restaurant-menu/{restaurant_id}/')


def process_payment(request, restaurant_id):
    # TODO: Implement payment processing
    # Stubbed for demo purposes
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")

    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    customer_order.order_status = 'payment-approved'
    customer_order.save()
    return redirect(f'/cart/checkout/{restaurant_id}/')


def order_processed(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")

    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    return render(request, 'cart/order_status.html', {'customer_order': customer_order,
                                               'restaurant': restaurant})


def order_confirmed(request, restaurant_id):
    pass


def order_rejected(request, restaurant_id):
    pass


def order_completed(request, restaurant_id):
    pass
