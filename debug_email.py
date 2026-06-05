import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*70)
print("DEBUG: Environment Variables Check")
print("="*70)

# Load .env manually
from dotenv import load_dotenv
env_path = project_root / '.env'
print(f"\n.env file location: {env_path}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env file loaded")
else:
    print("❌ .env file NOT found!")

print("\n" + "-"*70)
print("Environment Variables:")
print("-"*70)

email_user = os.getenv('EMAIL_HOST_USER')
email_pass = os.getenv('EMAIL_HOST_PASSWORD')

print(f"EMAIL_HOST_USER = {email_user}")
print(f"EMAIL_HOST_PASSWORD = {email_pass}")

if not email_user:
    print("\n❌ EMAIL_HOST_USER is empty or not set!")
if not email_pass:
    print("\n❌ EMAIL_HOST_PASSWORD is empty or not set!")

print("\n" + "-"*70)
print("Django Settings Check:")
print("-"*70)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
import django
django.setup()

from django.conf import settings

print(f"EMAIL_BACKEND = {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST = {settings.EMAIL_HOST}")
print(f"EMAIL_PORT = {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS = {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER = {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD = {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL = {settings.DEFAULT_FROM_EMAIL}")

print("\n" + "="*70)

if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
    print("✅ Configuration looks good!")
    print("\nNow testing email send...")
    print("-"*70)
    
    from django.core.mail import send_mail
    
    try:
        send_mail(
            subject='Test Email - Configuration Debug',
            message='If you receive this, your email configuration is working!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print(f"Check inbox: {settings.DEFAULT_FROM_EMAIL}")
    except Exception as e:
        print(f"❌ Email send failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Configuration incomplete!")
    print("Please check your .env file")

print("="*70)
