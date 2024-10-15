from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from sellerapp.models import Dish,Seller
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # phone_number = models.CharField(max_length=15, blank=True)  
    # address = models.CharField(max_length=255, blank=True)       
    # profile_picture = models.ImageField(upload_to='profile_pics', blank=True) 
    otp = models.CharField(max_length=6,blank=True,null=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.cart_id} - User {self.user} - Dish {self.dish.name}"
    
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=[('Dine-In', 'Dine-In'), ('Take-Out', 'Take-Out')])
    payment_status = models.CharField(max_length=20, default='Pending')  # Options could be 'Pending', 'Completed', etc.
    time_slot = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)  # Adds created_at field

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} in Order {self.order.order_id}"

