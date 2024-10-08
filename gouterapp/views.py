import random
from django.views import View
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import login,authenticate,logout as auth_logout
from .forms import SignUpForm,LoginForm,OTPForm
from .models import Profile,Cart
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from sellerapp.models import Seller,Dish
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import JsonResponse
import ast

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

def add_to_cart(request,dish_id):
    dish = get_object_or_404(Dish,id=dish_id)
    cart_item, created = Cart.objects.get_or_create(
        user_id = request.user.id,
        dish_id = dish_id,
        defaults={'quantity':1}
    )
    if not created:
        cart_item.quantity +=1
        cart_item.save()
    return redirect('view_dishes',seller_id = dish.restaurant_id)

def view_cart(request):
    # Fetch cart items for the logged-in user
    cart_items = Cart.objects.filter(user_id=request.user.id).select_related('dish')
    cart_details = []
    total_price = 0
    seller_id = None
    for item in cart_items:
        item_total = item.dish.price * item.quantity
        total_price += item_total
        cart_details.append({
            'dish':item.dish,
            'quantity':item.quantity,
            'item_total':item_total,
            'cart_id': item.cart_id
        })
        if not seller_id:
            seller_id = item.dish.restaurant_id


    context = {
        'cart_details':cart_details,
        'total_price': total_price,
        'seller_id': seller_id,
    }
    return render(request,'cart.html',context)

def increment_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, cart_id = cart_id, user_id = request.user.id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

def decrement_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, cart_id = cart_id, user_id = request.user.id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    # else:
    #     cart_item.delete()
    return redirect('view_cart')

def remove_from_cart(request,cart_id):
    cart_item = get_object_or_404(Cart, cart_id=cart_id,user_id = request.user.id)
    cart_item.delete()
    return redirect('view_cart')