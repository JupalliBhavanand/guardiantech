# Generated by Django 5.0.7 on 2024-09-29 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_employee_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(blank=True, default='employee_photos/default_photo.jpg', null=True, upload_to='employee_photos/'),
        ),
    ]
