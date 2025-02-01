# Generated by Django 5.1.1 on 2024-10-16 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_attendance_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerletter',
            name='file',
            field=models.FileField(default='offer_letters/default_offer_letter.pdf', upload_to='offer_letters/'),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='uploaded_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='payroll',
            name='file',
            field=models.FileField(default='payslips/default_payslip.pdf', upload_to='payslips/'),
        ),
        migrations.AddField(
            model_name='payroll',
            name='month',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='payroll',
            name='uploaded_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='payroll',
            name='year',
            field=models.CharField(max_length=4, null=True),
        ),
    ]
