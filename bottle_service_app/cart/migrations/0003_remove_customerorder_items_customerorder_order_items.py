# Generated by Django 4.2.7 on 2024-02-23 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_remove_customerorder_menu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerorder',
            name='items',
        ),
        migrations.AddField(
            model_name='customerorder',
            name='order_items',
            field=models.ManyToManyField(to='cart.orderitem'),
        ),
    ]
