from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.seller_signup, name='seller_signup'),
    path('seller-login/', views.seller_login, name='seller_login'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path('seller_logout/', views.seller_logout, name='seller_logout'),
    path('add-dish/',views.add_dish, name='add_dish'),
    path('seller-dishes/', views.seller_dishes, name='seller_dishes'),
    path('edit-dish/<int:dish_id>/', views.edit_dish, name='edit_dish'),
    path('toggle-availability/<int:id>/', views.toggle_availability, name='toggle_availability'),
    path('seller/coupons/', views.coupons_list, name='seller_coupons'),
    path('seller/coupons/create/', views.create_coupon, name='create_coupon'),
    path('seller/coupons/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('seller/coupons/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('seller/coupons/toggle/<int:coupon_id>/', views.toggle_coupon_availability, name='toggle_coupon_availability'),
    path('create-time-slot/', views.create_time_slot, name='create_time_slot'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
