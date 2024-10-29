from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import SellerSignUpForm,SellerLoginForm,SellerProfileForm,DishForm,CouponForm,TimeSlotForm
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from .models import Seller,Dish,Coupon,TimeSlot
import os
from gouterapp.models import Order,OrderItem
from django.db.models import Q,Sum,Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta,datetime
from django.http import HttpResponse
import csv

def seller_signup(request):
    if request.method == 'POST':
        form = SellerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your restaurant account has been created')
            return redirect('seller_dashboard')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = SellerSignUpForm()
    return render(request, 'seller_signup.html', {'form': form})

def seller_login(request):
    if request.method == 'POST':
        form = SellerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('seller_dashboard')
                else:
                    form.add_error(None, 'Invalid email or password')
            except User.DoesNotExist:
                form.add_error(None, 'User with this email does not exist')
    else:
        form = SellerLoginForm()

    return render(request, 'seller_login.html', {'form': form})


@login_required(login_url='/login/')  # Ensure the user is logged in
def seller_dashboard(request):
    # Check if the user has an associated seller profile
    if not hasattr(request.user, 'seller'):
        return redirect('/')  # Redirect to homepage or another appropriate page

    seller = request.user.seller
    restaurant_name = seller.restaurant_name  # Replace with actual field name for restaurant name
    
    orders = Order.objects.filter(seller=seller, payment_status='Completed')  # Filter by successful orders


    # Top 10 dishes
    top_dishes = (
        OrderItem.objects.filter(seller=seller)
        .values('dish__name')
        .annotate(total_quantity=Count('dish'))
        .order_by('-total_quantity')[:10]
    )

    # Top 10 categories
    top_categories = (
        OrderItem.objects.filter(seller=seller)
        .values('dish__category__name')
        .annotate(total_quantity=Count('dish__category'))
        .order_by('-total_quantity')[:10]
    )

    # Initialize variables for sales report
    sales_by_day = sales_by_week = sales_by_month = sales_by_year = 0
    sales_by_day_before_coupon = sales_by_week_before_coupon = sales_by_month_before_coupon = sales_by_year_before_coupon = 0
    custom_sales = custom_sales_before_coupon = None
    custom_start_date = custom_end_date = None

    # Filter by day
    today = timezone.now().date()
    sales_by_day = orders.filter(created_at__date=today).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_day_before_coupon = orders.filter(created_at__date=today).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by week
    week_start = today - timedelta(days=today.weekday())  # Get start of the week (Monday)
    sales_by_week = orders.filter(created_at__date__gte=week_start).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_week_before_coupon = orders.filter(created_at__date__gte=week_start).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by month
    sales_by_month = orders.filter(created_at__year=today.year, created_at__month=today.month).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_month_before_coupon = orders.filter(created_at__year=today.year, created_at__month=today.month).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by year
    sales_by_year = orders.filter(created_at__year=today.year).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_year_before_coupon = orders.filter(created_at__year=today.year).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Custom date range
    if request.method == 'POST':
        custom_start_date = request.POST.get('start_date')
        custom_end_date = request.POST.get('end_date')

        if custom_start_date and custom_end_date:
            try:
                start_date = datetime.strptime(custom_start_date, "%Y-%m-%d")
                end_date = datetime.strptime(custom_end_date, "%Y-%m-%d")
                custom_sales = orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
                custom_sales_before_coupon = orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0
            except ValueError:
                custom_sales = "Invalid date format"

    context = {
        'restaurant_name': restaurant_name,
        'sales_by_day': sales_by_day,
        'sales_by_day_before_coupon': sales_by_day_before_coupon,
        'sales_by_week': sales_by_week,
        'sales_by_week_before_coupon': sales_by_week_before_coupon,
        'sales_by_month': sales_by_month,
        'sales_by_month_before_coupon': sales_by_month_before_coupon,
        'sales_by_year': sales_by_year,
        'sales_by_year_before_coupon': sales_by_year_before_coupon,
        'custom_sales': custom_sales,
        'custom_sales_before_coupon': custom_sales_before_coupon,
        'custom_start_date': custom_start_date,
        'custom_end_date': custom_end_date,
        'top_dishes': top_dishes,
        'top_categories': top_categories,
    }
    return render(request, 'seller_dashboard.html', context)



@login_required
def seller_profile(request):
    seller = get_object_or_404(Seller, user=request.user)  # Get the seller associated with the logged-in user

    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=seller)  # Include request.FILES for image upload
        if form.is_valid():
            if request.FILES.get('image_url'):  # Check if an image is uploaded
                seller.image_url = request.FILES['image_url']  # Update the image URL field
            form.save()  # Save the form data
            seller.save()  # Save the updated seller instance (including the image URL)
            messages.success(request, 'Your profile has been updated successfully.')  # Success message
            return redirect('seller_profile')  # Redirect to the profile page
        else:
            messages.error(request, 'Please correct the errors below.')  # Error message
    else:
        form = SellerProfileForm(instance=seller)  # Pre-fill the form with the current seller's data

    return render(request, 'seller_profile.html', {'form': form, 'seller': seller})  # Render the profile page

def seller_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def add_dish(request):
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            dish = form.save(commit=False)
            dish.restaurant = request.user.seller
            dish.save()
            return redirect('seller_dashboard')
    else:
        form = DishForm()
    return render(request, 'add_dish.html', {'form': form})

@login_required
def seller_dishes(request):
    seller = request.user.seller
    query = request.GET.get('query','')
    dishes = Dish.objects.filter(restaurant=seller)

    if query:
        dishes = dishes.filter(Q(name__icontains=query)| Q(description__icontains=query))

    paginator = Paginator(dishes,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'seller_dishes.html', {'dishes': dishes,'query':query,'page_obj':page_obj})

def toggle_availability(request, id):
    dish = get_object_or_404(Dish, id=id)
    if request.method == "POST":
        dish.is_available = not dish.is_available
        dish.save()
    return redirect('seller_dishes')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Dish  # Assuming your dish model is named `Dish`
from .forms import DishForm  # Assuming you're using a `DishForm` for this view

def edit_dish(request, dish_id):
    # Get the dish object or return a 404 if not found
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        # Bind the form with POST data and file (image)
        form = DishForm(request.POST, request.FILES, instance=dish)

        if form.is_valid():
            # Save the form if valid
            form.save()
            messages.success(request, 'Dish updated successfully!')
            return redirect('seller_dishes')  # Replace with the correct redirect

        else:
            # Print the validation errors in the console (for debugging)
            print(form.errors)
            messages.error(request, 'There were errors in the form, please correct them.')
    
    else:
        # Create the form with the current dish instance for editing
        form = DishForm(instance=dish)

    # Render the template with the dish and form
    return render(request, 'edit_dish.html', {'form': form, 'dish': dish})

def coupons_list(request):
    seller = get_object_or_404(Seller , user=request.user)
    coupons = Coupon.objects.filter(seller=seller)
    return render(request, 'coupons_list.html', {'coupons':coupons})

@login_required
def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            # Fetch the seller instance associated with the logged-in user
            seller = get_object_or_404(Seller, user=request.user)
            coupon.seller = seller  # Assign the seller instance to the coupon
            coupon.save()
            return redirect('seller_coupons')
    else:
        form = CouponForm()
    return render(request, 'create_coupon.html', {'form': form})

def edit_coupon(request, coupon_id):
    # Retrieve the seller associated with the logged-in user
    seller = get_object_or_404(Seller, email=request.user.email)
    
    # Now, query the Coupon using the Seller instance
    coupon = get_object_or_404(Coupon, id=coupon_id, seller=seller)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('seller_coupons')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'edit_coupon.html', {'form': form})

# Delete Coupon
def delete_coupon(request, coupon_id):
    seller = get_object_or_404(Seller, email=request.user.email)
    coupon = get_object_or_404(Coupon, id=coupon_id, seller=seller)
    coupon.delete()
    return redirect('seller_coupons')

@login_required
def toggle_coupon_availability(request, coupon_id):
    # Get the seller instance associated with the logged-in user
    seller = get_object_or_404(Seller, user=request.user)

    # Query the coupon based on the seller instance
    coupon = get_object_or_404(Coupon, id=coupon_id, seller=seller)

    # Toggle the availability of the coupon
    coupon.is_available = not coupon.is_available
    coupon.save()

    return redirect('seller_coupons')

@login_required
def create_time_slot(request):
    seller = get_object_or_404(Seller, user=request.user)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.seller = seller  # Associate the time slot with the seller
            time_slot.max_capacity = seller.table_number
            time_slot.save()
            messages.success(request, 'Time slot added successfully.')
            return redirect('seller_dashboard')  # Redirect to the seller dashboard or appropriate page
    else:
        form = TimeSlotForm()

    return render(request, 'create_time_slot.html', {'form': form})


@login_required
def seller_orders(request):
    seller = get_object_or_404(Seller, user=request.user)  # Get the seller associated with the logged-in user
    orders = Order.objects.filter(seller=seller).select_related('user').prefetch_related('items__dish').order_by('-order_id')

    order_data = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'item_id': item.id,
                'dish_name': item.dish.name,
                'price': item.dish.price,
                'quantity': item.quantity,  # Assuming the quantity field is in OrderItem
            })
        order_data.append({
            'order_id': order.order_id,
            'user_email': order.user.email,  # Get user email if needed
            'total_amount': order.total_amount,
            'method': order.method,
            'time_slot': order.time_slot,
            'items': items,
            'payment_status':order.payment_status
        })

    context = {
        'order_data': order_data,
        'restaurant_name': seller.restaurant_name,  # Optional: Include restaurant name in context
    }

    return render(request, 'seller_orders.html', context)  # Create a template for displaying seller orders

# ---------------------------------------------------------------------------------------------------------------------

#sales report

def sales_report(request):
    # Check if the user has an associated seller profile
    if not hasattr(request.user, 'seller'):
        return redirect('/')  # Redirect to homepage or another appropriate page

    seller = request.user.seller
    restaurant_name = seller.restaurant_name  # Replace with actual field name for restaurant name
    
    orders = Order.objects.filter(seller=seller, payment_status='Completed')  # Filter by successful orders

    top_dishes = (
        OrderItem.objects.filter(seller=seller)
        .values('dish__name')
        .annotate(total_quantity=Count('dish'))
        .order_by('-total_quantity')[:10]
    )

    # Top 10 categories
    top_categories = (
        OrderItem.objects.filter(seller=seller)
        .values('dish__category__name')
        .annotate(total_quantity=Count('dish__category'))
        .order_by('-total_quantity')[:10]
    )

    # Initialize variables for sales report
    sales_by_day = sales_by_week = sales_by_month = sales_by_year = 0
    sales_by_day_before_coupon = sales_by_week_before_coupon = sales_by_month_before_coupon = sales_by_year_before_coupon = 0
    custom_sales = custom_sales_before_coupon = None
    custom_start_date = custom_end_date = None

    # Filter by day
    today = timezone.now().date()
    sales_by_day = orders.filter(created_at__date=today).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_day_before_coupon = orders.filter(created_at__date=today).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by week
    week_start = today - timedelta(days=today.weekday())  # Get start of the week (Monday)
    sales_by_week = orders.filter(created_at__date__gte=week_start).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_week_before_coupon = orders.filter(created_at__date__gte=week_start).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by month
    sales_by_month = orders.filter(created_at__year=today.year, created_at__month=today.month).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_month_before_coupon = orders.filter(created_at__year=today.year, created_at__month=today.month).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Filter by year
    sales_by_year = orders.filter(created_at__year=today.year).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    sales_by_year_before_coupon = orders.filter(created_at__year=today.year).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0

    # Custom date range
    if request.method == 'POST':
        custom_start_date = request.POST.get('start_date')
        custom_end_date = request.POST.get('end_date')

        if custom_start_date and custom_end_date:
            try:
                start_date = datetime.strptime(custom_start_date, "%Y-%m-%d")
                end_date = datetime.strptime(custom_end_date, "%Y-%m-%d")
                custom_sales = orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
                custom_sales_before_coupon = orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(total_sales_before_coupon=Sum('total_amount_before_coupon'))['total_sales_before_coupon'] or 0
            except ValueError:
                custom_sales = "Invalid date format"

    context = {
        'restaurant_name': restaurant_name,
        'sales_by_day': sales_by_day,
        'sales_by_day_before_coupon': sales_by_day_before_coupon,
        'sales_by_week': sales_by_week,
        'sales_by_week_before_coupon': sales_by_week_before_coupon,
        'sales_by_month': sales_by_month,
        'sales_by_month_before_coupon': sales_by_month_before_coupon,
        'sales_by_year': sales_by_year,
        'sales_by_year_before_coupon': sales_by_year_before_coupon,
        'custom_sales': custom_sales,
        'custom_sales_before_coupon': custom_sales_before_coupon,
        'custom_start_date': custom_start_date,
        'custom_end_date': custom_end_date,
        'top_dishes': top_dishes,
        'top_categories': top_categories,
    }
    return render(request, 'seller_dashboard.html', context)




@login_required(login_url='/login/')
def download_sales_report(request):
    # Check if the user has an associated seller profile
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    
    seller = request.user.seller
    orders = Order.objects.filter(seller=seller, payment_status='Completed')

    # Check for custom date range filters in GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            # Parse the dates and include the whole end date by adding 1 day
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")  # End of the selected day
            
            # Filter orders by date range (assuming created_at is DateTimeField)
            orders = orders.filter(created_at__date__gte=start_date_obj, created_at__date__lte=end_date_obj)
        except ValueError:
            # Handle date parsing errors if necessary
            pass

    # Prepare response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Total Amount Before Coupon', 'Total Amount', 'Method', 'Payment Status', 'Created At'])

    for order in orders:
        writer.writerow([order.order_id, order.user.username, order.total_amount_before_coupon, order.total_amount, order.method, order.payment_status, order.created_at])

    return response