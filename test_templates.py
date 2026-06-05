"""
Quick test to verify admin templates are being loaded
"""
import os
from django.conf import settings

print("\n" + "="*60)
print("TEMPLATE CONFIGURATION TEST")
print("="*60)

# Check if bookings app is in INSTALLED_APPS
print("\n1. Checking INSTALLED_APPS:")
if 'bookings' in settings.INSTALLED_APPS:
    print("   ✓ 'bookings' app is installed")
else:
    print("   ✗ 'bookings' app is NOT installed")

# Check template directories
print("\n2. Checking TEMPLATES configuration:")
for template_config in settings.TEMPLATES:
    print(f"   Backend: {template_config['BACKEND']}")
    print(f"   DIRS: {template_config['DIRS']}")
    print(f"   APP_DIRS: {template_config['APP_DIRS']}")

# Check if admin templates exist
print("\n3. Checking admin template files:")
base_dir = settings.BASE_DIR
admin_template_dir = os.path.join(base_dir, 'bookings', 'templates', 'admin')

if os.path.exists(admin_template_dir):
    print(f"   ✓ Admin template directory exists: {admin_template_dir}")
    
    templates = ['base_site.html', 'index.html', 'login.html', 'reports.html']
    for template in templates:
        template_path = os.path.join(admin_template_dir, template)
        if os.path.exists(template_path):
            size = os.path.getsize(template_path)
            print(f"   ✓ {template} exists ({size} bytes)")
        else:
            print(f"   ✗ {template} NOT FOUND")
else:
    print(f"   ✗ Admin template directory NOT FOUND: {admin_template_dir}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
