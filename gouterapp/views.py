import random
from django.views import View
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import login,authenticate,logout as auth_logout
from .forms import SignUpForm,LoginForm,OTPForm
from .models import Profile,Cart,Order,OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta,datetime
from sellerapp.models import Seller,Dish,TimeSlot,Coupon
from adminapp.models import Category
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import JsonResponse
import ast
from django.http import Http404 
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def welcome(request):
    return render(request,'welcome.html')



def home(request):
    query = request.GET.get('q')
    restaurant_type = request.GET.get('type', 'all')  # Default to 'all'

    # Start with approved sellers
    sellers = Seller.objects.filter(is_approved=True)

    # Filter by search query if provided
    if query:
        sellers = sellers.filter(restaurant_name__icontains=query)

    # Filter by type if a specific type is selected
    if restaurant_type == 'veg':
        sellers = sellers.filter(type='veg')
    elif restaurant_type == 'nonveg':
        sellers = sellers.filter(type='nonveg')

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
    dishes = Dish.objects.filter(restaurant__id=seller_id, is_available=True)
    categories = Category.objects.filter(dish__restaurant__id=seller_id).distinct()
    
    # Get the search query, selected category, and sort order from GET parameters
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', 'All')
    sort_order = request.GET.get('sort', 'Default')

    # Filter dishes based on search query
    if search_query:
        dishes = dishes.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Filter dishes by selected category
    if selected_category != 'All':
        dishes = dishes.filter(category__name=selected_category)

    # Sort dishes based on the selected sort order
    if sort_order == 'low_to_high':
        dishes = dishes.order_by('price')
    elif sort_order == 'high_to_low':
        dishes = dishes.order_by('-price')

    paginator = Paginator(dishes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'dishes': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'sort_order': sort_order,
        'search_query': search_query,
        'seller': seller,
        'MEDIA_URL': settings.MEDIA_URL,
        'page_obj':page_obj
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


def generate_time_slots(start_time, end_time, interval_minutes=30):
    current_time = start_time
    time_slots = []
    
    while current_time < end_time:
        next_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=interval_minutes)).time()
        time_slots.append((current_time, next_time))
        current_time = next_time
    
    return time_slots



def choose_method(request):
    cart_items = Cart.objects.filter(user_id=request.user.id)
    if not cart_items.exists():
        return redirect('view_dishes')

    seller_id = cart_items.first().dish.restaurant.id
    seller = get_object_or_404(Seller, id=seller_id)

    # Assuming seller's operating hours are defined, e.g., from 9 AM to 10 PM
    seller_start_time = datetime.strptime("09:00", "%H:%M").time()
    seller_end_time = datetime.strptime("22:00", "%H:%M").time()

    # Generate time slots based on seller's hours
    time_slot_ranges = generate_time_slots(seller_start_time, seller_end_time)

    # Check availability
    available_slots = []
    for start, end in time_slot_ranges:
        # Check if this slot is already booked
        is_booked = TimeSlot.objects.filter(seller=seller, start_time=start).exists()
        available_slots.append({
            'start_time': start,
            'end_time': end,
            'is_available': not is_booked  # Assume if exists, it's booked
        })

        # Ensure you create TimeSlot instances based on the generated slots
        TimeSlot.objects.get_or_create(
            seller=seller,
            start_time=start,
            defaults={
                'end_time': end,
                'bookings_count': 0 , # Set to the initial booking count
                'max_capacity': seller.table_number,
            }
        )

    return render(request, 'choose_method.html', {'time_slots': available_slots})



client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


def submit_order(request):
    if request.method == 'POST':
        selected_method = request.POST.get('method')
        selected_time = request.POST.get('time_slot')

        # Convert selected_time from "10:00 AM" format to a time object
        try:
            formatted_time = datetime.strptime(selected_time, "%I:%M %p").time()
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('choose_method')

        # Fetch seller ID from user's cart and calculate total amount
        cart_items = Cart.objects.filter(user_id=request.user.id)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_dishes',seller_id=seller_id)

        seller_id = cart_items.first().dish.restaurant.id
        seller = get_object_or_404(Seller, id=seller_id)
        total_amount = sum(item.dish.price * item.quantity for item in cart_items)

        #fetch coupons for the seller
        coupons = Coupon.objects.filter(seller=seller, is_available=True)

        # Find the corresponding time slot
        try:
            time_slot = get_object_or_404(TimeSlot, start_time=formatted_time, seller=seller)
        except Http404:
            messages.error(request, "No TimeSlot matches the given query.")
            return redirect('choose_method')

        # Check if the time slot is available
        if time_slot.bookings_count < seller.table_number:
            # Update TimeSlot booking count
            time_slot.bookings_count += 1
            time_slot.save()

            # Create Razorpay Order
            razorpay_order = client.order.create({
                'amount': int(total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            # Create Order record
            order = Order.objects.create(
                seller=seller,
                user=request.user,
                total_amount_before_coupon=total_amount,
                total_amount=total_amount,
                method=selected_method,
                time_slot=f"{time_slot.start_time} - {time_slot.end_time}",
                payment_status="Failed",
                razorpay_order_id=razorpay_order['id'],
                coupon_usage='unused',
            )

            # Create OrderItems for each cart item
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    seller=seller,
                    user=request.user,
                    dish=item.dish,
                    quantity=item.quantity
                )

            #save order ID in session for coupon usage
            request.session['order_id'] = order.order_id

            # Prepare context for Razorpay checkout in payment.html
            context = {
                'submit_order': {
                    'key_id': settings.RAZORPAY_API_KEY,
                    'amount': int(total_amount * 100),  # Amount in paise
                    'display_amount': total_amount,  # Amount in rupees for display
                    'restaurant_name': seller.restaurant_name,
                    'order_id': order.order_id,
                    'razorpay_order_id': razorpay_order['id'],
                    'restaurant_logo': seller.image_url,
                    'method': selected_method,
                    'time_slot': f"{time_slot.start_time} - {time_slot.end_time}",
                },
                'coupons': coupons,
                'user': request.user,
                'callback_url': reverse('payment_callback', kwargs={'order_id': order.order_id})
            }

            return render(request, 'payment.html', context)
        else:
            messages.error(request, "The selected time slot is no longer available.")
            return redirect('choose_method')
        


# ----------------------------------------------------------------------------------------

@csrf_exempt
def payment_callback(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, order_id=order_id)
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        # Verify the payment
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature                                             #just added this
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            order.payment_status = 'Completed'
            order.save()

            # Transfer money to seller wallet
            with transaction.atomic():
                order.seller.wallet_balance += order.total_amount
                order.seller.save()

            Cart.objects.filter(user_id=request.user.id).delete() 
            
            return redirect('order_success', order_id=order_id)
        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'Failed'
            messages.error(request, "Payment failed.")
            print("3")
            return redirect('view_cart')



# ---------------------------------------------------------------------------------------

        
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    context = {
        'restaurant_name': order.seller.restaurant_name,
        'order_id': order.order_id,
        'time_slot': order.time_slot,
        'method': order.method,
        'total_amount': order.total_amount,
        'payment_status': order.payment_status,
        'order_items':order_items
    }
    return render(request, 'ticket.html', context)


@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).select_related('seller').prefetch_related('items__dish').order_by('-order_id')
    order_data = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'item_id': item.id,
                'dish_name': item.dish.name,
                'price': item.dish.price,
                'quantity': item.quantity,
            })
        order_data.append({
            'order_id': order.order_id,
            'restaurant_name': order.seller.restaurant_name,
            'total_amount': order.total_amount,
            'method': order.method,
            'time_slot': order.time_slot,
            'payment_status': order.payment_status,
            'items': items,
        })

    context = {
        'order_data' : order_data
    }

    return render(request, 'view_order.html', context)

# -----------------------------------------------------------------------------------------------------

@login_required
def cancel_dish(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, user=request.user)
    item_total = order_item.dish.price * order_item.quantity

    # Transfer item amount from seller to user
    order_item.order.seller.wallet_balance -= item_total
    request.user.profile.wallet_balance += item_total
    order_item.order.seller.save()
    request.user.profile.save()

    order_item.delete()
    messages.success(request, 'Dish has been canceled and amount refunded.')
    return redirect(reverse('view_orders'))


# -----------------------------------------------------------------------------------------------------


@login_required
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    total_amount = order.total_amount
    seller = order.seller

    # Transfer total amount from seller's wallet balance to user's profile
    seller.wallet_balance -= total_amount
    request.user.profile.wallet_balance += total_amount
    seller.save()
    request.user.profile.save()

    # Retrieve and update the bookings count for the time slot
    time_slot_str = order.time_slot  # e.g., "11:00:00 - 11:30:00"
    if time_slot_str and seller:
        try:
            start_time_str = time_slot_str.split(" - ")[0]  # Extracts "11:00:00"
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()  # Converts to time object
        except (ValueError, IndexError):
            messages.error(request, "Invalid time slot format.")
            return redirect(reverse('view_orders'))

        # Retrieve the specific TimeSlot instance using start_time
        time_slot_instance = TimeSlot.objects.filter(
            seller=seller,
            start_time=start_time
        ).first()
        
        if time_slot_instance and time_slot_instance.bookings_count > 0:
            time_slot_instance.bookings_count -= 1
            time_slot_instance.save()

    # Delete the order
    order.delete()
    messages.success(request, 'Entire order has been canceled, and amount refunded.')

    return redirect(reverse('view_orders'))

# ----------------------------------------------------------------------------------------------

#wallet balance of the user

def wallet_balance_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'wallet_balance.html',{
        'wallet_balance':profile.wallet_balance
    })


# -----------------------------------------------------------------------------------------------

#coupons
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        order_id = request.session.get('order_id')  # Assuming you stored the order_id in the session

        # Fetch the order
        order = get_object_or_404(Order, order_id=order_id)

        try:
            # Fetch the coupon
            coupon = Coupon.objects.get(code=coupon_code, seller=order.seller, is_available=True)

            # Check if coupon is expired
            if coupon.expiry_date < datetime.now().date():
                messages.error(request, "This coupon has expired.")
                return redirect('payment')

            # Apply discount to the total amount
            discount_amount = (coupon.discount / 100) * order.total_amount
            new_total = order.total_amount - discount_amount

            # Update the order total amount
            order.total_amount = new_total
            order.coupon_usage='used'
            order.save()

            # Pass new total amount to session
            request.session['coupon_applied'] = True
            request.session['discounted_total'] = int(new_total)  # Store the discounted total in the session

            messages.success(request, f"Coupon applied! New total is ₹{new_total:.2f}")
            return redirect('payment')

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code or not available for this seller.")
            return redirect('payment')
        




client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def payment(request):
    # Assuming the order_id is stored in the session
    order_id = request.session.get('order_id')
    
    if not order_id:
        return render(request, 'error.html', {'message': 'No order found.'})
    
    # Fetch the order
    order = get_object_or_404(Order, pk=order_id)
    cart_items = Cart.objects.filter(user_id=request.user.id)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_dishes', seller_id=seller_id)
    
    # Get seller information
    seller_id = cart_items.first().dish.restaurant.id
    seller = get_object_or_404(Seller, id=seller_id)
    
    # Check if coupon is applied
    coupon_applied = request.session.get('coupon_applied', False)

    # Use discounted total if coupon is applied, otherwise use original total
    total_amount = request.session.get('discounted_total', order.total_amount)
    total_amount_in_paise = int(total_amount * 100)
    
    # Create a Razorpay order
    try:
        razorpay_order = client.order.create({
            'amount': total_amount_in_paise,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'  # Auto-capture payment
        })
    except Exception as e:
        messages.error(request, f"Error creating Razorpay order: {str(e)}")
        return redirect('payment')  # Redirect back to the payment page in case of error

    # Prepare context for template
    context = {
        'submit_order': {
            'key_id': settings.RAZORPAY_API_KEY,
            'order_id': order.order_id,
            'display_amount': total_amount,  # Total amount after applying coupon if any
            'method': order.method,  # Dine-In or Take-out
            'time_slot': order.time_slot,
            'restaurant_name': order.seller.restaurant_name,  # Seller/Restaurant name
            'razorpay_order_id': razorpay_order['id']  # Actual Razorpay order ID
        },
        'coupon_applied': coupon_applied,
        'coupons': order.seller.coupon_set.filter(is_available=True)  # Fetch available coupons for the seller
    }
    
    return render(request, 'payment.html', context)

def view_ticket(request,order_id):
    try:
        order = Order.objects.get(order_id=order_id,user=request.user)
    except order.DoesNotExist:
        return redirect('view_orders')
    except Order.MultipleObjectsReturned:
        return redirect('view_orders')
    
    order_items=OrderItem.objects.filter(order=order)
    
    context = {
        'restaurant_name':order.seller.restaurant_name,
        'order_id':order.order_id,
        'time_slot':order.time_slot,
        'method':order.method,
        'total_amount':order.total_amount,
        'payment_status':order.payment_status,
        'order_items':order_items
    }
    return render(request,'ticket.html',context)


# --------------------------------------------------------------------------------------------------
#wallet-payment

@login_required
def wallet_payment(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    # Get the user's profile to access the wallet balance
    user_profile = request.user.profile

    # Check if the user has enough balance in their wallet
    if user_profile.wallet_balance < order.total_amount:
        messages.error(request, "Insufficient wallet balance.")
        return redirect('payment', order_id=order_id)

    # If balance is sufficient, deduct from wallet and complete the order
    with transaction.atomic():
        user_profile.wallet_balance -= order.total_amount
        user_profile.save()

        # Update the order status to completed
        order.payment_status = 'Completed'
        order.save()

        # Transfer money to the seller's wallet
        order.seller.wallet_balance += order.total_amount
        order.seller.save()

    # Clear the user's cart
    Cart.objects.filter(user=request.user).delete()

    # Redirect to success page
    return redirect('order_success', order_id=order_id)


def retry_pay(request,order_id):
    order = get_object_or_404(Order, pk=order_id)
    total_amount = order.total_amount
    total_amount_in_paise = int(total_amount * 100)

    if order.coupon_usage == 'used':
        coupon_applied = True
    else:
        coupon_applied = False
    

    # Create a Razorpay order
    try:
        razorpay_order = client.order.create({
            'amount': total_amount_in_paise,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'  # Auto-capture payment
        })
    except Exception as e:
        messages.error(request, f"Error creating Razorpay order: {str(e)}")
        return redirect('payment')  # Redirect back to the payment page in case of error
    
    context = {
        'submit_order': {
            'key_id': settings.RAZORPAY_API_KEY,
            'order_id': order.order_id,
            'display_amount': total_amount,  # Total amount after applying coupon if any
            'method': order.method,  # Dine-In or Take-out
            'time_slot': order.time_slot,
            'restaurant_name': order.seller.restaurant_name,  # Seller/Restaurant name
            'razorpay_order_id': razorpay_order['id']  # Actual Razorpay order ID
        },
        'coupon_applied': coupon_applied,
        'coupons': order.seller.coupon_set.filter(is_available=True)  # Fetch available coupons for the seller
    }
    
    return render(request, 'payment.html', context)
