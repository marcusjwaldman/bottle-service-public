# Generated by Django 4.2.7 on 2024-02-19 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerorder',
            name='menu',
        ),
    ]
