from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

