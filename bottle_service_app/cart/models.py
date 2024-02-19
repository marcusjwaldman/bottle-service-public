from django.db import models

from customer.models import Customer
from distributor.models import Distributor
from partners.models import Menu, Item
from restaurant.models import Restaurant


class OrderStatus(models.Choices):
    EMPTY = 'empty'
    SHOPPING = 'shopping'
    PAYMENT_APPROVED = 'payment-approved'
    PAYMENT_DENIED = 'payment-denied'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


# Create your models here.
class CustomerOrder(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    # menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, null=True)
    order_status = models.CharField(max_length=100, null=True)
    restaurant_additional_info = models.TextField(null=True)
    customer_notes = models.TextField(null=True)
    items = models.ManyToManyField(Item, through='OrderItem')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

