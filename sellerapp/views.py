from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import SellerSignUpForm,SellerLoginForm,SellerProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from .models import Seller

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

def seller_dashboard(request):
    return render(request, 'seller_dashboard.html')


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