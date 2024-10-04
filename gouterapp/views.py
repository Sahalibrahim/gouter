import random
from django.views import View
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import login,authenticate,logout as auth_logout
from .forms import SignUpForm,LoginForm,OTPForm
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from sellerapp.models import Seller,Dish,Booking
from django.conf import settings
from django.shortcuts import render, get_object_or_404

# Create your views here.
def welcome(request):
    return render(request,'welcome.html')

def home(request):
    sellers = Seller.objects.filter(is_approved=True)
    return render(request, 'home.html', {'sellers': sellers, 'MEDIA_URL': settings.MEDIA_URL})


def generate_otp():
    return str(random.randint(100000, 999999))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user.is_active = False
            # user.save()
            otp = generate_otp()
            Profile.objects.create(user=user, otp=otp)
            request.session['user_id'] = user.id

            send_mail(
                'Your OTP Code for Verification',
                f'Hello {user.first_name},\n\nYour OTP code for verifying your email is {otp}.\nPlease enter this code to complete the signup process.\n\nThank you!',
                'gouter580@gmail.com',
                [user.email],
                fail_silently=False
            )

            messages.success(request, 'Account created successfully! Please check your email for the OTP.')
            return redirect('otp_verification') 
    else:
        form = SignUpForm()
    return render(request,'signup.html', {'form': form})



def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
                else:
                    form.add_error(None, "Invalid email or password")
            except User.DoesNotExist:
                form.add_error(None, "Invalid email or password")
        else:
            messages.error(request, "Form is not valid")

    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    return render(request,'profile.html')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')

# def verify_otp(request):
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             otp = form.cleaned_data.get('otp').strip()
#             user_id = request.session.get('user_id')
#             if not user_id:
#                 form.add_error(None, "Session expired. please try signup again")
#                 return render(request, 'verify_otp.html', {'form': form})
#             try:
#                 profile = Profile.objects.get(user_id=user_id, otp=otp)
#                 if profile and profile.otp_created_at >= timezone.now() - timedelta(minutes=5):
#                     profile.user.is_active = True
#                     profile.user.save()
#                     profile.is_verified = True
#                     profile.save()
#                     login(request, profile.user)
#                     messages.success(request, 'Account created successfully!')
#                     return redirect('home')
#                 else:
#                     form.add_error(None, "Invalid or expired OTP.")
#             except Profile.DoesNotExist:
#                 form.add_error(None, "Invalid OTP.")
#     else:
#         form = OTPForm()

#     return render(request, 'verify_otp.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp').strip()
            user_id = request.session.get('user_id')

            if not user_id:
                form.add_error(None, "Session expired. Please try signup again.")
                return render(request, 'verify_otp.html', {'form': form})

            try:
                profile = Profile.objects.get(user_id=user_id, otp=otp)

                if profile and profile.otp_created_at >= timezone.now() - timedelta(minutes=5):
                    # Activate the user's account
                    profile.user.is_active = True
                    profile.user.save()
                    profile.is_verified = True
                    profile.save()

                    # Log the user in with the allauth backend
                    login(request, profile.user, backend='allauth.account.auth_backends.AuthenticationBackend')

                    messages.success(request, 'Account created successfully!')
                    return redirect('home')

                else:
                    form.add_error(None, "Invalid or expired OTP.")
            except Profile.DoesNotExist:
                form.add_error(None, "Invalid OTP.")
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})

def resend_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please try signing up again.')
        return redirect('signup')
    try:
        profile = Profile.objects.get(user_id=user_id)
        otp = generate_otp()
        profile.otp = otp
        profile.otp_created_at = timezone.now()
        profile.save()

        send_mail(
            'Resend OTP Code',
            f'Your new OTP code is {otp}',
            'gouter580@gmail.com',
            [profile.user.email],
            fail_silently=False,
        )

        messages.success(request, 'A new OTP has been sent to your email.')
    except Profile.DoesNotExist:
        messages.error(request, 'Error resending OTP.')
    return redirect('otp_verification')

# def view_dishes(request, restaurant_id):
#     seller = get_object_or_404(Seller, pk=restaurant_id)
#     dishes = Dish.objects.filter(restaurant=seller)
#     context = {
#         'seller': seller,
#         'dishes': dishes,
#         'MEDIA_URL': settings.MEDIA_URL,
#     }
#     return render(request, 'view_dishes.html', context)

# def view_dishes(request, seller_id):
#     seller = get_object_or_404(Seller, pk=seller_id)
#     selected_category = request.GET.get('category', 'All')
    
#     if selected_category == 'All':
#         dishes = Dish.objects.filter(restaurant=seller)
#     else:
#         dishes = Dish.objects.filter(restaurant=seller, category=selected_category)
    
#     categories = Dish.objects.values_list('category', flat=True).distinct()
    
#     context = {
#         'seller': seller,
#         'dishes': dishes,
#         'categories': categories,
#         'selected_category': selected_category,
#         'MEDIA_URL': settings.MEDIA_URL,
#     }
#     return render(request, 'view_dishes.html', context)

def view_dishes(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    selected_category = request.GET.get('category', 'All')

    # Filter dishes based on availability and category
    if selected_category == 'All':
        dishes = Dish.objects.filter(restaurant=seller, is_available=True)
    else:
        dishes = Dish.objects.filter(restaurant=seller, category=selected_category, is_available=True)
    
    # Get distinct categories from available dishes only
    categories = Dish.objects.filter(restaurant=seller, is_available=True).values_list('category', flat=True).distinct()

    context = {
        'seller': seller,
        'dishes': dishes,
        'categories': categories,
        'selected_category': selected_category,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'view_dishes.html', context)

# def add_to_cart(request, dish_id):
#     dish = get_object_or_404(Dish, id=dish_id)

#     # Check if the cart exists in the session
#     cart = request.session.get('cart', {})
    
#     # Add or update the dish in the cart
#     if str(dish_id) in cart:
#         cart[str(dish_id)]['quantity'] += 1  # Increment quantity if already in the cart
#     else:
#         cart[str(dish_id)] = {
#             'name': dish.name,
#             'price': float(dish.price),
#             'quantity': 1,
#             'image': dish.image.url
#         }
    
#     # Update the session with the new cart data
#     request.session['cart'] = cart
#     messages.success(request, f"{dish.name} added to cart!")
#     seller_id = dish.restaurant.id
#     return redirect('view_dishes',seller_id=seller_id) 

def add_to_cart(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    # Check if the cart exists in the session
    cart = request.session.get('cart', {})
    
    # Add or update the dish in the cart
    if str(dish_id) in cart:
        cart[str(dish_id)]['quantity'] += 1  # Increment quantity if already in the cart
    else:
        cart[str(dish_id)] = {
            'name': dish.name,
            'price': float(dish.price),
            'quantity': 1,
            'image': dish.image.url,
            'restaurant_id': dish.restaurant.id  # Add the seller's ID here
        }
    
    # Update the session with the new cart data
    request.session['cart'] = cart
    messages.success(request, f"{dish.name} added to cart!")
    
    # Redirect to the seller's dish view with the seller's ID
    return redirect('view_dishes', seller_id=dish.restaurant.id)


def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Check if there is at least one item in the cart to extract the seller ID
    if cart:
        first_item = next(iter(cart.values()))  # Get the first item in the cart
        seller_id = first_item.get('restaurant_id')  # Get the 'restaurant_id' key
    else:
        seller_id = None  # No seller ID if the cart is empty

    # Ensure the seller_id is passed to the template if it's available
    return render(request, 'cart.html', {
        'cart': cart,
        'total_price': total_price,
        'seller_id': seller_id
    })

# def view_cart(request):
#         cart = request.session.get('cart', {})
#         total_price = sum(item['price'] * item['quantity'] for item in cart.values())
#         return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

@login_required
def update_cart(request, item_id):
    cart = request.session.get('cart', {})

    # Get the item from the cart
    if str(item_id) in cart:
        if request.POST.get('action') == 'increase':
            cart[str(item_id)]['quantity'] += 1
        elif request.POST.get('action') == 'decrease' and cart[str(item_id)]['quantity'] > 1:
            cart[str(item_id)]['quantity'] -= 1

        # Update session with modified cart
        request.session['cart'] = cart

    return redirect('view_cart') 

def remove_from_cart(request, item_id):
    # Logic to remove the item from the cart
    cart = request.session.get('cart', {})
    cart.pop(item_id, None)  # Remove the item from the cart
    request.session['cart'] = cart  # Update the session
    return redirect('view_cart')  # Redirect back to the cart page


def choose_method(request):
    seller_id = request.GET.get('seller_id')  # Fetch from query parameter

    if not seller_id:
        return HttpResponse("Seller ID not found in session", status=400)

    context = {
        'seller_id': seller_id
    }
    
    return render(request, 'choose_method.html', context)




def time_slot(request, seller_id):
    # Safely get the Seller instance
    seller = get_object_or_404(Seller, pk=seller_id)
    booking_method = request.GET.get('method','Unknown')
    
    # List of time slots
    available_time_slots = [
        '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM',
        '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM',
        '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM', '8:00 PM', '8:30 PM',
        '9:00 PM', '9:30 PM', '10:00 PM'
    ]
    
    # Initialize time slots with availability count
    time_slots = {}
    
    for slot in available_time_slots:
        # Get the number of bookings for each time slot
        time_slots[slot] = Booking.objects.filter(seller=seller, time_slot=slot).count()
    
    # Context to pass to the template
    context = {
        'seller': seller,  # Include seller information
        'time_slots': time_slots,
        'table_number': seller.table_number,  # Table number if needed
        'booking_method': booking_method
    }
    
    return render(request, 'time_slot.html', context)