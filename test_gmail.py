#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

print("\n" + "="*60)
print("GMAIL CONFIGURATION TEST")
print("="*60)

print(f"\nEmail Configuration:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if not settings.EMAIL_HOST_USER or settings.EMAIL_HOST_USER == '':
    print("\n❌ ERROR: EMAIL_HOST_USER is not configured!")
    sys.exit(1)

if not settings.EMAIL_HOST_PASSWORD or settings.EMAIL_HOST_PASSWORD == 'your_app_password':
    print("\n❌ ERROR: EMAIL_HOST_PASSWORD is not configured!")
    print("   Please set EMAIL_HOST_PASSWORD in .env file")
    sys.exit(1)

print("\n" + "-"*60)
print("Attempting to send test email...")
print("-"*60)

try:
    send_mail(
        'Test Email from Look Here Studio',
        'This is a test email to verify your Gmail configuration is working correctly.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )
    print("\n✅ TEST EMAIL SENT SUCCESSFULLY!")
    print(f"   Sent to: {settings.DEFAULT_FROM_EMAIL}")
    print("\n   Check your Gmail inbox (including spam folder)")
    
except Exception as e:
    print(f"\n❌ FAILED TO SEND TEST EMAIL")
    print(f"   Error: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
