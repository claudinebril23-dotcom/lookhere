#!/usr/bin/env python
"""
SQLite Database Setup Script for Photobooth Booking System
This script creates the database using SQLite and populates it with sample data
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings module to development settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings_dev')

def setup_django():
    """Setup Django environment"""
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"Error setting up Django: {e}")
        return False

def run_migrations():
    """Run Django migrations to create tables"""
    try:
        from django.core.management import execute_from_command_line
        
        print("\nCreating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'bookings'])
        
        print("\nApplying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False

def create_superuser():
    """Create a superuser for admin access"""
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            print("\nCreating superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@photoboothsystem.com',
                password='admin123'
            )
            print("Superuser created!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   WARNING: Please change this password in production!")
        else:
            print("Superuser already exists!")
            
    except Exception as e:
        print(f"Error creating superuser: {e}")

def populate_sample_data():
    """Populate database with comprehensive sample data"""
    try:
        from bookings.models import Package, Addon, Backdrop, CreativePackage, GalleryImage, GalleryImageFile
        
        print("\nCreating sample data...")
        
        # Create Packages with detailed descriptions
        packages_data = [
            {
                'name': 'Basic Portrait Session',
                'tier': 'Basic',
                'duration': 30,
                'base_price': 1500.00,
                'processing_time': '1-2 days',
                'description': 'Perfect for individual portraits and headshots. Includes 30 minutes of shooting time with professional lighting, one backdrop of your choice, and basic photo editing. Great for social media profiles, professional headshots, or personal keepsakes.'
            },
            {
                'name': 'Standard Family Package',
                'tier': 'Standard',
                'duration': 60,
                'base_price': 2500.00,
                'processing_time': '2-3 days',
                'description': 'Ideal for family photos and small groups (2-4 people). Includes 60 minutes of shooting time, multiple backdrop options, professional lighting setup, and enhanced photo editing. Perfect for family portraits, couple photos, or small group celebrations.'
            },
            {
                'name': 'Premium Event Package',
                'tier': 'Premium',
                'duration': 120,
                'base_price': 4500.00,
                'processing_time': '3-5 days',
                'description': 'Complete premium experience with 2 hours of shooting time, unlimited backdrop changes, professional lighting and equipment, advanced photo retouching, and priority processing. Perfect for special events, professional portfolios, or comprehensive photo sessions.'
            },
            {
                'name': 'Quick Selfie Session',
                'tier': 'Basic',
                'duration': 15,
                'base_price': 800.00,
                'processing_time': '1 day',
                'description': 'Quick and affordable selfie session perfect for social media content. Includes 15 minutes of shooting time, one backdrop, and basic editing. Great for Instagram posts, profile pictures, or quick photo updates.'
            },
            {
                'name': 'Couple Romance Package',
                'tier': 'Standard',
                'duration': 90,
                'base_price': 3200.00,
                'processing_time': '2-3 days',
                'description': 'Romantic photo session designed for couples. Includes 90 minutes of shooting time, romantic lighting setup, multiple backdrop options, and enhanced editing with soft romantic filters. Perfect for anniversaries, engagements, or date memories.'
            }
        ]
        
        for pkg_data in packages_data:
            package, created = Package.objects.get_or_create(name=pkg_data['name'], defaults=pkg_data)
            if created:
                print(f"   Created package: {package.name}")
        
        # Create comprehensive Add-ons
        addons_data = [
            {'name': 'Extra 30 minutes', 'price': 500.00, 'description': 'Additional 30 minutes of shooting time for more poses and outfit changes'},
            {'name': 'Rush Processing (24hrs)', 'price': 800.00, 'description': 'Get your edited photos delivered within 24 hours'},
            {'name': 'Extra Backdrop Setup', 'price': 300.00, 'description': 'Additional backdrop setup during your session'},
            {'name': 'Props Package', 'price': 400.00, 'description': 'Fun props and accessories including hats, glasses, signs, and decorative items'},
            {'name': 'Digital Album', 'price': 1200.00, 'description': 'Professional digital photo album with custom layout and design'},
            {'name': 'Print Package (5x7)', 'price': 600.00, 'description': '10 high-quality printed photos in 5x7 size with matte finish'},
            {'name': 'Print Package (8x10)', 'price': 900.00, 'description': '5 premium printed photos in 8x10 size with glossy finish'},
            {'name': 'USB Drive with All Photos', 'price': 300.00, 'description': 'All edited photos delivered on a branded USB drive'},
            {'name': 'Social Media Package', 'price': 450.00, 'description': 'Photos optimized for social media platforms with square crops and filters'},
            {'name': 'Professional Retouching', 'price': 200.00, 'description': 'Advanced photo retouching per image including skin smoothing and color correction'},
            {'name': 'Outfit Change', 'price': 250.00, 'description': 'Additional time and setup for outfit changes during session'},
            {'name': 'Makeup Touch-up', 'price': 350.00, 'description': 'Professional makeup touch-up service during the session'}
        ]
        
        for addon_data in addons_data:
            addon, created = Addon.objects.get_or_create(name=addon_data['name'], defaults=addon_data)
            if created:
                print(f"   Created addon: {addon.name}")
        
        # Create diverse Backdrops
        backdrops_data = [
            'White Classic', 'Black Elegant', 'Blue Ocean', 'Pink Blush', 
            'Green Nature', 'Purple Royal', 'Red Passion', 'Yellow Sunshine',
            'Gray Modern', 'Beige Neutral', 'Coral Warm', 'Mint Fresh',
            'Navy Professional', 'Cream Vintage', 'Teal Modern', 'Rose Gold',
            'Burgundy Rich', 'Forest Green', 'Sky Blue', 'Lavender Dream',
            'Charcoal Professional', 'Ivory Soft', 'Turquoise Bright', 'Peach Gentle'
        ]
        
        for backdrop_name in backdrops_data:
            backdrop, created = Backdrop.objects.get_or_create(name=backdrop_name)
            if created:
                print(f"   Created backdrop: {backdrop.name}")
        
        # Create Creative Packages with variety
        creative_packages = [
            'Vintage Film', 'Modern Minimalist', 'Artistic Black & White',
            'Bright & Colorful', 'Moody & Dramatic', 'Natural & Soft',
            'High Fashion', 'Retro Pop', 'Classic Portrait', 'Urban Street',
            'Romantic Soft', 'Professional Corporate', 'Creative Artistic'
        ]
        
        for cp_name in creative_packages:
            cp, created = CreativePackage.objects.get_or_create(name=cp_name)
            if created:
                print(f"   Created creative package: {cp.name}")
        
        # Create sample Gallery Images
        gallery_data = [
            {'title': 'Professional Headshots Collection', 'category': 'portrait'},
            {'title': 'Happy Family Moments', 'category': 'family'},
            {'title': 'Romantic Couple Session', 'category': 'portrait'},
            {'title': 'Creative Self Portraits', 'category': 'self_portrait'},
            {'title': 'Studio Setup Showcase', 'category': 'studio'},
            {'title': 'Event Photography Highlights', 'category': 'event'}
        ]
        
        for gallery_item in gallery_data:
            gallery, created = GalleryImage.objects.get_or_create(
                title=gallery_item['title'], 
                defaults={'category': gallery_item['category']}
            )
            if created:
                print(f"   Created gallery set: {gallery.title}")
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

def show_database_info():
    """Display comprehensive database information"""
    try:
        from django.db import connection
        from bookings.models import Package, Addon, Backdrop, CreativePackage, GalleryImage
        
        print(f"\nDatabase Information:")
        print(f"   Database Engine: {connection.vendor}")
        print(f"   Database File: {connection.settings_dict['NAME']}")
        
        # Count records
        packages_count = Package.objects.count()
        addons_count = Addon.objects.count()
        backdrops_count = Backdrop.objects.count()
        creative_count = CreativePackage.objects.count()
        gallery_count = GalleryImage.objects.count()
        
        print(f"\nData Summary:")
        print(f"   Packages: {packages_count}")
        print(f"   Add-ons: {addons_count}")
        print(f"   Backdrops: {backdrops_count}")
        print(f"   Creative Packages: {creative_count}")
        print(f"   Gallery Sets: {gallery_count}")
        
        # Show package details
        print(f"\nPackage Details:")
        for package in Package.objects.all():
            print(f"   • {package.name} ({package.tier}) - ₱{package.base_price} - {package.duration}min")
            
    except Exception as e:
        print(f"Error getting database info: {e}")

def main():
    """Main setup function"""
    print("Photobooth Booking System - SQLite Database Setup")
    print("=" * 55)
    
    # Step 1: Setup Django
    print("Setting up Django environment...")
    if not setup_django():
        return
    
    # Step 2: Run migrations
    if not run_migrations():
        return
    
    # Step 3: Create superuser
    create_superuser()
    
    # Step 4: Populate sample data
    populate_sample_data()
    
    # Step 5: Show database info
    show_database_info()
    
    print("\nDatabase setup completed successfully!")
    print("\nNext Steps:")
    print("   1. Run: python manage.py runserver --settings=narrativestudio.settings_dev")
    print("   2. Visit: http://localhost:8000/admin (admin/admin123)")
    print("   3. Visit: http://localhost:8000 (main site)")
    print("\nUseful Commands:")
    print("   • View database: python manage.py show_db --settings=narrativestudio.settings_dev")
    print("   • Create admin user: python manage.py createsuperuser --settings=narrativestudio.settings_dev")
    print("   • Run server: python manage.py runserver --settings=narrativestudio.settings_dev")

if __name__ == '__main__':
    main()