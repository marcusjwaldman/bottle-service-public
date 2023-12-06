# Generated by Django 4.2.7 on 2023-12-05 14:09

from django.db import migrations, models
import django.db.models.deletion

from partners.models import MenuItemCategory


def load_initial_data(apps, schema_editor):
    MenuItemCategory.objects.create(name='Other', description='Not a beverage')


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0015_alter_menu_status_alter_partners_status'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]