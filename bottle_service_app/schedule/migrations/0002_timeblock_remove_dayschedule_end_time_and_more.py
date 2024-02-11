# Generated by Django 4.2.7 on 2024-02-05 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.RemoveField(
            model_name='dayschedule',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='dayschedule',
            name='start_time',
        ),
        migrations.AddField(
            model_name='dayschedule',
            name='time_blocks',
            field=models.ManyToManyField(to='schedule.timeblock'),
        ),
    ]
