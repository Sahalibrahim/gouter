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
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
