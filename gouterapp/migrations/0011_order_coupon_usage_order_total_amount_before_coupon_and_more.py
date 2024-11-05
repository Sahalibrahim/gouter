# Generated by Django 5.1.1 on 2024-10-21 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gouterapp', '0010_alter_order_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_usage',
            field=models.CharField(default='unused', max_length=10),
        ),
        migrations.AddField(
            model_name='order',
            name='total_amount_before_coupon',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]