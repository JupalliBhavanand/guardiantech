# Generated by Django 5.1.1 on 2024-12-06 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_alter_attendance_check_out_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='check_in_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='check_out_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
