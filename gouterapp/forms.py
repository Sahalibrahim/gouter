from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# class SignUpForm(UserCreationForm):
#     first_name = forms.CharField(max_length=30, required=True, help_text='Required')
#     last_name = forms.CharField(max_length=30, required=True, help_text='Required')
#     email = forms.EmailField(max_length=200, help_text='Required')
#     # phone_number = forms.CharField(max_length=15, required=True, help_text='Required')  # Custom field

#     class Meta:
#         model = User
#         # Include password1 and password2 here along with the custom fields
#         fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
#     def save(self, commit=True):
#         user = super(SignUpForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
        
#         # Automatically generate a unique username
#         base_username = f"{user.first_name}_{user.last_name}".lower()
#         username = base_username
#         # counter = 1
#         while User.objects.filter(username=username).exists():
#             username = f"{base_username}{counter}"
#             counter += 1

#         user.username = username

#         if commit:
#             user.save()
#         return user

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Automatically generate a unique username
        base_username = f"{user.first_name}_{user.last_name}".lower()
        username = base_username
        counter = 1  # Initialize the counter

        # Check for username uniqueness
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user.username = username

        if commit:
            user.save()
        return user

    
class LoginForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'id': 'email',
        'type': 'email',
        'required': '',
    }),
    required=True
    )
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'id': 'password',
        'type': 'password',
        'required': ''
    }), 
    required=True
    )

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter OTP',
    }), required=True)