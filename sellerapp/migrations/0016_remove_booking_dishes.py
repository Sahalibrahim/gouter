# Generated by Django 5.1.1 on 2024-10-05 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sellerapp', '0015_remove_booking_dish'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='dishes',
        ),
    ]