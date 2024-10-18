# Generated by Django 5.1.1 on 2024-10-17 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gouterapp', '0007_orderitem_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wallet_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]