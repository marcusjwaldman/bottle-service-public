# Generated by Django 4.2.7 on 2024-02-27 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_remove_customerorder_items_customerorder_order_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerorder',
            name='confirmation_code',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
