from django.urls import path
from . import views

urlpatterns = [
    path('seller-signup/', views.seller_signup, name='seller_signup'),
    path('seller-login/', views.seller_login, name='seller_login'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
]
