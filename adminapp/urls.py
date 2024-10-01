from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),  
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('view-sellers/', views.view_sellers, name='view_sellers'),
    path('block-seller/<int:seller_id>/', views.block_seller, name='block_seller'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
]