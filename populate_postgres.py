#!/usr/bin/env python
"""
Populate PostgreSQL Database with Sample Data
"""

import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')

django.setup()

from bookings.models import Package, Addon, Backdrop, CreativePackage

print("Populating PostgreSQL database with sample data...")
print("=" * 50)

# Create Packages
packages_data = [
    {
        'name': 'Basic Portrait Session',
        'tier': 'Basic',
        'duration': 30,
        'base_price': 1500.00,
        'processing_time': '1-2 days',
        'description': 'Perfect for individual portraits and headshots'
    },
    {
        'name': 'Standard Family Package',
        'tier': 'Standard',
        'duration': 60,
        'base_price': 2500.00,
        'processing_time': '2-3 days',
        'description': 'Great for family photos and small groups'
    },
    {
        'name': 'Premium Event Package',
        'tier': 'Premium',
        'duration': 120,
        'base_price': 4500.00,
        'processing_time': '3-5 days',
        'description': 'Complete event coverage with professional editing'
    }
]

for pkg_data in packages_data:
    package, created = Package.objects.get_or_create(name=pkg_data['name'], defaults=pkg_data)
    if created:
        print(f"Created package: {package.name}")

# Create Addons
addons_data = [
    {'name': 'Extra 30 minutes', 'price': 500.00, 'description': 'Additional 30 minutes of shooting time'},
    {'name': 'Rush Processing', 'price': 800.00, 'description': 'Get your photos in 24 hours'},
    {'name': 'Extra Backdrop', 'price': 300.00, 'description': 'Additional backdrop setup'},
    {'name': 'Props Package', 'price': 400.00, 'description': 'Fun props and accessories'},
    {'name': 'Digital Album', 'price': 1200.00, 'description': 'Professional digital photo album'},
]

for addon_data in addons_data:
    addon, created = Addon.objects.get_or_create(name=addon_data['name'], defaults=addon_data)
    if created:
        print(f"Created addon: {addon.name}")

# Create Backdrops
backdrops_data = [
    'White Classic', 'Black Elegant', 'Blue Ocean', 'Pink Blush', 
    'Green Nature', 'Purple Royal', 'Red Passion', 'Yellow Sunshine',
    'Gray Modern', 'Beige Neutral', 'Coral Warm', 'Mint Fresh'
]

for backdrop_name in backdrops_data:
    try:
        backdrop, created = Backdrop.objects.get_or_create(name=backdrop_name)
        if created:
            print(f"Created backdrop: {backdrop.name}")
    except Exception as e:
        print(f"Error creating backdrop {backdrop_name}: {e}")

# Create Creative Packages
creative_packages = [
    'Vintage Film', 'Modern Minimalist', 'Artistic Black & White',
    'Bright & Colorful', 'Moody & Dramatic', 'Natural & Soft'
]

for cp_name in creative_packages:
    cp, created = CreativePackage.objects.get_or_create(name=cp_name)
    if created:
        print(f"Created creative package: {cp.name}")

print("\nDatabase populated successfully!")
print(f"Packages: {Package.objects.count()}")
print(f"Addons: {Addon.objects.count()}")
print(f"Backdrops: {Backdrop.objects.count()}")
print(f"Creative Packages: {CreativePackage.objects.count()}")