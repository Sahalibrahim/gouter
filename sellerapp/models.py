from django.db import models
from django.contrib.auth.models import User

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    table_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.restaurant_name
