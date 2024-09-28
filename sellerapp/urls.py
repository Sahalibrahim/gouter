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
    path('add-dish/',views.add_dish, name='add_dish'),
    path('seller-dishes/', views.seller_dishes, name='seller_dishes'),
    path('edit-dish/<int:id>/', views.edit_dish, name='edit_dish'),
    path('toggle-availability/<int:id>/', views.toggle_availability, name='toggle_availability'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
