from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('seller-signup/', views.seller_signup, name='seller_signup'),
    path('seller-login/', views.seller_login, name='seller_login'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path('seller_logout/', views.seller_logout, name='seller_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
