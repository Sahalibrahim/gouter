from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'owner_name', 'is_approved')
    list_filter = ('is_approved',)