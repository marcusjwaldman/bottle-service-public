# Generated by Django 4.2.7 on 2024-02-19 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0007_alter_menu_status_alter_partners_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_restaurant', 'Pending Restaurant Approval'), ('approved', 'Approved'), ('rejected_by_restaurant', 'Rejected By Restaurant'), ('archived', 'Archived')], default='draft', max_length=30),
        ),
        migrations.AlterField(
            model_name='partners',
            name='status',
            field=models.CharField(choices=[('matched', 'Matched'), ('pending_distributor', 'Pending Distributor Approval'), ('pending_restaurant', 'Pending Restaurant Approval'), ('approved', 'Approved'), ('rejected_by_distributor', 'Rejected By Distributor'), ('rejected_by_restaurant', 'Rejected By Restaurant')], default='matched', max_length=30),
        ),
    ]
