# Generated by Django 5.1.1 on 2024-10-05 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellerapp', '0011_remove_booking_table_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='dish_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='dishes',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='booking',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
