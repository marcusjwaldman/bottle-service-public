# Generated by Django 4.2.7 on 2023-12-05 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0012_alter_menu_unique_together_menu_created_at_and_more'),
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
        migrations.CreateModel(
            name='MenuItemCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='partners.menuitemcategory')),
            ],
        ),
        migrations.AddField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='partners.menuitemcategory'),
        ),
    ]
