from django.db import models

class CustomAdmin(models.Model):
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100,default='admin')

    def __str__(self):
        return self.username