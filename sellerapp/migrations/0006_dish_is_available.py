# Generated by Django 5.1.1 on 2024-09-28 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellerapp', '0005_alter_dish_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]