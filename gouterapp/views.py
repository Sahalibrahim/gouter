from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout as auth_logout
from .forms import SignUpForm,LoginForm
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def welcome(request):
    return render(request,'welcome.html')

def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

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