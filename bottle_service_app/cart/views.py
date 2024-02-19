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

    order_item = OrderItem.objects.create(order=customer_order, item=item, customer_price=menu_item.calculated_price)
    customer_order.total_cost += order_item.customer_price
    customer_order.save()

    return redirect(f'/customer/customer-restaurant-menu/{customer_order.restaurant.id}/')


# def remove_from_cart(request, cart_item_id):
#     cart_item = CartItem.objects.get(pk=cart_item_id)
#     cart_item.delete()
#     return redirect('cart')
#
def cart(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise Http404(f"Restaurant {restaurant_id} does not exist")
    customer_order = BottleServiceSession.get_customer_order(request, restaurant)
    items = customer_order.items.all()
    order_items = OrderItem.objects.filter(order=customer_order)
    return render(request, 'cart/cart.html', {'cart_items': order_items})

# def checkout(request):
#     cart = Cart.objects.get(user=request.user)
#     cart_items = cart.cartitem_set.all()
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     # Implement your checkout logic here
#     return render(request, 'checkout.html', {'total_price': total_price})
