# Generated by Django 4.2.7 on 2023-12-03 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0008_alter_menu_status_alter_partners_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='paused',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='distributor_notes',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='out_of_stock',
            field=models.BooleanField(default=False),
        ),
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
