from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SellerSignUpForm,SellerLoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate

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