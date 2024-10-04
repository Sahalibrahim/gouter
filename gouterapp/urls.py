from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',views.welcome,name='welcome'),
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('verify-otp/',views.verify_otp, name='otp_verification'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('login/',views.login_view,name='login'),
    path('profile',views.profile,name='profile'),
    path('logout/',views.logout,name='logout'),
    path('restaurant/<int:seller_id>/dishes',views.view_dishes, name='view_dishes'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('choose-method/',views.choose_method,name='choose_method'),
    path('time_slot/<int:seller_id>/', views.time_slot, name='time_slot'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
