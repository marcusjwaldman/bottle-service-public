# Generated by Django 4.2.7 on 2024-02-05 22:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_timeblock_remove_dayschedule_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dayschedule',
            name='time_blocks',
        ),
        migrations.AddField(
            model_name='timeblock',
            name='day_schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_blocks', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='friday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='monday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='saturday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='saturday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='sunday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sunday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='thursday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='thursday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='tuesday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tuesday', to='schedule.dayschedule'),
        ),
        migrations.AlterField(
            model_name='weeklyschedule',
            name='wednesday',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wednesday', to='schedule.dayschedule'),
        ),
    ]
