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
    path('add_to_cart/<int:dish_id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.view_cart,name='view_cart'),
    path('cart/increment/<int:cart_id>',views.increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:cart_id>',views.decrement_quantity,name='decrement_quantity'),
    path('cart/remove/<int:cart_id>',views.remove_from_cart,name='remove_from_cart'),
    path('choose-method/', views.choose_method, name='choose_method'),  # URL for selecting booking method and time slot
    path('submit-order/', views.submit_order, name='submit_order'),  # URL for submitting the order after selecting method and time slot
    path('order/success/<int:order_id>', views.order_success, name='order_success'),  # URL to redirect to after successful order (you can implement `order_success` view for a success message)
    path('orders/',views.view_orders, name='view_orders'),
    path('orders/cancel_dish/<int:item_id>/',views.cancel_dish, name='cancel_dish'),
    path('orders/cancel_order/<int:order_id>/',views.cancel_order, name='cancel_order'),
    path('payment-callback/<int:order_id>/', views.payment_callback, name='payment_callback'),
    path('wallet-balance/',views.wallet_balance_view, name='wallet_balance'),
    path('apply-coupon/',views.apply_coupon,name='apply_coupon'),
    path('payment/', views.payment, name='payment'),
    path('ticket/<int:order_id>/',views.view_ticket,name='view_ticket'),
    path('wallet-payment/<int:order_id>/', views.wallet_payment, name='wallet_payment'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
