# Generated by Django 5.1.1 on 2024-11-25 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_alter_payroll_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='employee_banner/'),
        ),
    ]
