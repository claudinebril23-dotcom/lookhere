#!/usr/bin/env python
"""
Comprehensive Gmail Configuration Test
Run this from the lookhere directory: python email_test.py
"""
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')

import django
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

print("\n" + "="*70)
print(" "*15 + "GMAIL CONFIGURATION TEST")
print("="*70)

# Step 1: Check environment variables
print("\n[STEP 1] Checking Environment Variables...")
print("-" * 70)

email_user = os.getenv('EMAIL_HOST_USER')
email_pass = os.getenv('EMAIL_HOST_PASSWORD')

if email_user:
    print(f"✅ EMAIL_HOST_USER: {email_user}")
else:
    print(f"❌ EMAIL_HOST_USER: NOT SET")
    sys.exit(1)

if email_pass:
    print(f"✅ EMAIL_HOST_PASSWORD: {email_pass[:4]}...{email_pass[-4:]}")
else:
    print(f"❌ EMAIL_HOST_PASSWORD: NOT SET")
    sys.exit(1)

# Step 2: Check Django settings
print("\n[STEP 2] Checking Django Email Settings...")
print("-" * 70)

print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if not settings.EMAIL_HOST_USER:
    print("\n❌ ERROR: EMAIL_HOST_USER not loaded in Django settings!")
    sys.exit(1)

if not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERROR: EMAIL_HOST_PASSWORD not loaded in Django settings!")
    sys.exit(1)

# Step 3: Send test email
print("\n[STEP 3] Sending Test Email...")
print("-" * 70)

test_email = settings.DEFAULT_FROM_EMAIL
print(f"Sending test email to: {test_email}")

try:
    send_mail(
        subject='Test Email - Look Here Studio Configuration',
        message='This is a test email to verify your Gmail configuration is working correctly.\n\nIf you received this email, your booking confirmation emails will work!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[test_email],
        fail_silently=False,
    )
    print(f"✅ Test email sent successfully!")
    
except Exception as e:
    print(f"❌ Failed to send test email!")
    print(f"Error: {e}")
    print(f"Error Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Success
print("\n" + "="*70)
print(" "*20 + "✅ ALL TESTS PASSED!")
print("="*70)
print("\nNext Steps:")
print("1. Check your Gmail inbox (including spam/promotions folders)")
print("2. Look for the test email from: " + settings.DEFAULT_FROM_EMAIL)
print("3. If you see it, booking confirmations will work!")
print("\nTo test booking confirmations:")
print("1. Go to http://localhost:8000/book/")
print("2. Complete a booking")
print("3. Check your email for the confirmation")
print("\n" + "="*70 + "\n")
