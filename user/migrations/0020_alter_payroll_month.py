# Generated by Django 5.1.1 on 2024-11-10 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_alter_payroll_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payroll',
            name='month',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
