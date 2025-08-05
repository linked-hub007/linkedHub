# shop/otp_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp import match_token
from django.contrib.auth import login
from django_otp.util import random_hex
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.template.loader import get_template
import os
from django.http import HttpResponse

@login_required
def send_otp(request):
    """
    Entry point after login - determines if user needs OTP setup or verification
    """
    # Check if user has OTP device
    device = EmailDevice.objects.filter(user=request.user, name='email').first()
    
    if not device or not device.confirmed:
        # New user or unconfirmed device - setup OTP
        return redirect('setup_otp')
    else:
        # Existing user - verify OTP
        if request.method == 'POST':
            # Send OTP for verification
            token = device.generate_challenge()
            messages.success(request, f'OTP sent to your email: {request.user.email}')
            return redirect('verify_otp')
            
        # Show form to request OTP
        return render(request, 'shop/send_otp.html')  # Updated path

@login_required
def setup_otp(request):
    """Setup OTP for new users"""
    device, created = EmailDevice.objects.get_or_create(
        user=request.user,
        name='email',
        defaults={'confirmed': False}
    )
    
    if request.method == 'POST':
        # Send OTP to user's email for first-time setup
        token = device.generate_challenge()
        messages.success(request, f'OTP sent to your email: {request.user.email}')
        # Store in session that this is initial setup
        request.session['otp_setup'] = True
        return redirect('verify_otp')
    
    return render(request, 'shop/setup_otp.html')  # Updated path

@login_required
def verify_otp(request):
    """Verify OTP token"""
    if request.method == 'POST':
        token = request.POST.get('token')
        device = EmailDevice.objects.filter(user=request.user, name='email').first()
        
        if device and device.verify_token(token):
            # Confirm the device if it's initial setup
            if not device.confirmed:
                device.confirmed = True
                device.save()
                messages.success(request, 'OTP setup completed successfully!')
            else:
                messages.success(request, 'OTP verified successfully!')
                
            # Clear session flag
            request.session.pop('otp_setup', None)
            
            # Always redirect to profile after successful verification
            return redirect('profile')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'shop/verify_otp.html')  # Updated path

