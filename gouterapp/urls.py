from django.urls import path
from . import views

urlpatterns = [
    # path('',views.welcome,name='welcome'),
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('verify-otp/',views.verify_otp, name='otp_verification'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('login/',views.login_view,name='login'),
    path('profile',views.profile,name='profile'),
    path('logout/',views.logout,name='logout'),
]
