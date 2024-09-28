from django import forms
from django.contrib.auth.models import User
from .models import Seller,Dish

class SellerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    restaurant_name = forms.CharField(max_length=255, label="Restaurant Name")
    owner_name = forms.CharField(max_length=255, label="Owner's Name")
    email = forms.EmailField(label="Email Address")
    address = forms.CharField(widget=forms.Textarea, label="Address")

    class Meta:
        model = Seller
        fields = ['restaurant_name', 'owner_name', 'email', 'address', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        seller = super().save(commit=False)
        # Create a User instance for this seller
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        seller.user = user
        if commit:
            seller.save()
        return seller



class SellerLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = [
            'restaurant_name', 'owner_name', 'email', 'phone_number', 
            'password', 'address', 'description', 'table_number','image_url'
        ]
        widgets = {
            'password': forms.PasswordInput(render_value=True),  # Allows displaying a password placeholder
        }

# class DishForm(forms.ModelForm):
#     class Meta:
#         model = Dish
#         fields = ['name', 'description', 'price', 'image']

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'image', 'category','is_available'] 

