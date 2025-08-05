# shop/forms.py
from allauth.account.forms import SignupForm
from django import forms
from django.core.validators import RegexValidator
from .models import CustomUser  # Import your custom user model

class CustomSignupForm(SignupForm):
    # Phone number field with proper validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+919876543210'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to existing fields
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            # Remove any whitespace and keep only digits and + sign
            cleaned_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Check if phone number already exists using your CustomUser model
            if CustomUser.objects.filter(phone_number=cleaned_phone).exists():
                raise forms.ValidationError("A user with this phone number already exists.")
            
            return cleaned_phone
        
        return phone_number
    
    def save(self, request):
        user = super().save(request)
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user
    
#-------------------------------------------------------------------------------------------------------------------------------
