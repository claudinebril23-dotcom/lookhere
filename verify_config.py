#!/usr/bin/env python
"""Quick verification of email configuration"""
import os
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / '.env'
print(f"Reading .env from: {env_file}")
print()

if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if 'EMAIL' in line or 'PASSWORD' in line:
                    print(f"✓ {line}")
else:
    print("❌ .env file not found!")

print()
print("="*60)
print("Configuration Status:")
print("="*60)

# Check environment variables
email_user = os.getenv('EMAIL_HOST_USER', '')
email_pass = os.getenv('EMAIL_HOST_PASSWORD', '')

if email_user:
    print(f"✅ EMAIL_HOST_USER is set: {email_user}")
else:
    print(f"❌ EMAIL_HOST_USER is NOT set")

if email_pass:
    print(f"✅ EMAIL_HOST_PASSWORD is set: {email_pass[:4]}...{email_pass[-4:]}")
else:
    print(f"❌ EMAIL_HOST_PASSWORD is NOT set")

print()
print("Ready to send emails!" if (email_user and email_pass) else "Configuration incomplete!")
