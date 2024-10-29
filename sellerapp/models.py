from django.db import models
from django.contrib.auth.models import User
import os
from django.db.models import JSONField
from adminapp.models import Category


class Seller(models.Model):
    # restaurant_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    restaurant_name = models.CharField(max_length=255)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    image_url = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Updated to ImageField
    is_approved = models.BooleanField(default=False)
    table_number = models.IntegerField(blank=True, null=True)
    TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='nonveg')  # Default set to 'veg'

    def __str__(self):
        return self.restaurant_name

    def save(self, *args, **kwargs):
        try:
            # Check if the seller already has an image and if a new image is being uploaded
            old_image = Seller.objects.get(pk=self.pk).image_url
        except Seller.DoesNotExist:
            # If this is a new object, no need to check for an old image
            old_image = None

        # Call the original save method to update the image
        super().save(*args, **kwargs)

        # If there was an old image and the image_url field has changed, delete the old image
        if old_image and old_image != self.image_url:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)




class Dish(models.Model):
    name = models.CharField(max_length=255)  # Increased max_length to 255
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Updated max_digits
    image = models.ImageField(upload_to='dishes/', null=True, blank=True)  # Updated upload path
    # category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Category field remains
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Updated category field
    restaurant = models.ForeignKey('Seller', on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the dish is updated

    def save(self, *args, **kwargs):
        # You can add custom logic before or after saving the model here if needed
        super().save(*args, **kwargs)  # Call the "real" save() method

    def __str__(self):
        return self.name
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateField()
    is_available = models.BooleanField(default=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self):
        return self.code
    

class TimeSlot(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.IntegerField()
    bookings_count = models.IntegerField(default=0)
    is_booked = models.BooleanField(default=False)  # Indicates if the time slot is booked

    def is_available(self):
        return self.bookings_count < self.max_capacity

    def __str__(self):
        return f"{self.seller.restaurant_name}: {self.start_time} - {self.end_time}"
