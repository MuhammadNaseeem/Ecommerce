from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

# ------------------------
# Signup form
# ------------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# ------------------------
# Login form
# ------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'border rounded px-3 py-2 w-full',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'border rounded px-3 py-2 w-full',
        'placeholder': 'Password'
    }))

# ------------------------
# Password reset (forgot password) form
# ------------------------
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Enter your email'
        })
    )

# ------------------------
# Address form (shipping / billing)
# ------------------------
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'address_type', 'full_name', 'phone', 'street_address',
            'city', 'state', 'postal_code', 'country', 'default'
        ]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'full_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Phone'}),
            'street_address': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'placeholder': 'Country'}),
            'default': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }

