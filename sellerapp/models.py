from django.db import models
from django.contrib.auth.models import User
import os

class Seller(models.Model):
    # restaurant_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='dish_images/', blank=True, null=True)
    restaurant = models.ForeignKey(Seller, on_delete=models.CASCADE)


    def __str__(self):
        return self.name