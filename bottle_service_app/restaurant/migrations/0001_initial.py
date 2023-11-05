# Generated by Django 4.2.6 on 2023-11-05 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='location.address')),
            ],
        ),
    ]
