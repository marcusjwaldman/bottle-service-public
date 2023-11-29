# Generated by Django 4.2.7 on 2023-11-29 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0004_distributor_minutes_distance_positive_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributor',
            name='locomotion',
            field=models.CharField(choices=[('walking', 'Walk'), ('bicycling', 'Bicycle'), ('driving', 'Car')], max_length=20, null=True),
        ),
    ]
