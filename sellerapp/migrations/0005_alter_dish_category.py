# Generated by Django 5.1.1 on 2024-09-28 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellerapp', '0004_dish_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='category',
            field=models.CharField(choices=[('Shakes', 'Shakes'), ('Juices', 'Juices'), ('Chinese', 'Chinese'), ('Arabic', 'Arabic'), ('Curry', 'Curry'), ('Mandhi', 'Mandhi'), ('Deserts', 'Deserts')], max_length=50),
        ),
    ]
