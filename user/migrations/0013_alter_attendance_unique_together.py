# Generated by Django 5.1.1 on 2024-10-16 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_remove_offerletter_file_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('employee', 'date')},
        ),
    ]
