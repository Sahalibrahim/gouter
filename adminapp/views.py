from django.shortcuts import render,get_object_or_404,redirect
from gouterapp.models import User
from sellerapp.models import Seller
from .forms import AdminLoginForm
from .models import CustomAdmin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control

def is_admin(user):
    return user.is_staff and user.is_superuser  

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def admin_login_view(request):
    # Redirect to dashboard if user is already logged in and is an admin
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('home')  # Redirect non-admin users to home page
    
    # Process login form submission
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            # Check if the user is authenticated and is staff
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, "Invalid credentials or you don't have admin rights")
    else:
        form = AdminLoginForm()  # Initialize an empty form for GET requests

    return render(request, 'admin_login.html', {'form': form})

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')  # Ensuring only superusers can access this view
def admin_dashboard(request):
    # Check for the search query in the request
    query = request.GET.get('q')
    
    # Filter users based on the search query and ensure both first_name and last_name are present
    if query:
        users = User.objects.filter(username__icontains=query, first_name__isnull=False, last_name__isnull=False).exclude(first_name='', last_name='')
    else:
        # Only list users who have both a first name and a last name
        users = User.objects.filter(first_name__isnull=False, last_name__isnull=False).exclude(first_name='', last_name='')
    
    return render(request, 'admin_dashboard.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active  # Toggle the active status
    user.save()
    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.save()
        return redirect('admin_dashboard')
    return render(request, 'edit_user.html', {'user': user})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def view_sellers(request):
    sellers = Seller.objects.all()
    return render(request, 'seller_list.html', {'sellers': sellers})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def block_seller(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    seller.is_approved = not seller.is_approved
    seller.save()
    return redirect('view_sellers')

def admin_logout(request):
    logout(request)
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def view_sellers(request):
    # Get the search query
    query = request.GET.get('q')
    
    # Filter sellers based on the search query
    if query:
        sellers = Seller.objects.filter(
            restaurant_name__icontains=query
        )
    else:
        sellers = Seller.objects.all()
    
    return render(request, 'seller_list.html', {'sellers': sellers})
