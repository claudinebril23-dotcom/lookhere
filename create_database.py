#!/usr/bin/env python
"""
Simple Database Creation Script for Photobooth Booking System
This script creates the database using SQLite and populates it with sample data
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')

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
        execute_from_command_line(['manage.py', 'makemigrations'])
        
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
    """Populate database with sample data"""
    try:
        from bookings.models import Package, Addon, Backdrop, CreativePackage
        
        print("\nCreating sample data...")
        
        # Create Packages
        packages_data = [
            {
                'name': 'Basic Portrait Session',
                'tier': 'Basic',
                'duration': 30,
                'base_price': 1500.00,
                'processing_time': '1-2 days',
                'description': 'Perfect for individual portraits and headshots. Includes 30 minutes of shooting time with professional lighting and one backdrop of your choice.'
            },
            {
                'name': 'Standard Family Package',
                'tier': 'Standard',
                'duration': 60,
                'base_price': 2500.00,
                'processing_time': '2-3 days',
                'description': 'Great for family photos and small groups. Includes 60 minutes of shooting time, multiple backdrop options, and basic photo editing.'
            },
            {
                'name': 'Premium Event Package',
                'tier': 'Premium',
                'duration': 120,
                'base_price': 4500.00,
                'processing_time': '3-5 days',
                'description': 'Complete event coverage with professional editing. Includes 2 hours of shooting time, unlimited backdrops, and advanced photo retouching.'
            }
        ]
        
        for pkg_data in packages_data:
            package, created = Package.objects.get_or_create(name=pkg_data['name'], defaults=pkg_data)
            if created:
                print(f"   Created package: {package.name}")
        
        # Create Addons
        addons_data = [
            {'name': 'Extra 30 minutes', 'price': 500.00, 'description': 'Additional 30 minutes of shooting time'},
            {'name': 'Rush Processing', 'price': 800.00, 'description': 'Get your photos in 24 hours'},
            {'name': 'Extra Backdrop', 'price': 300.00, 'description': 'Additional backdrop setup'},
            {'name': 'Props Package', 'price': 400.00, 'description': 'Fun props and accessories'},
            {'name': 'Digital Album', 'price': 1200.00, 'description': 'Professional digital photo album'},
            {'name': 'Print Package (5x7)', 'price': 600.00, 'description': '10 printed photos in 5x7 size'},
            {'name': 'Print Package (8x10)', 'price': 900.00, 'description': '5 printed photos in 8x10 size'},
            {'name': 'USB Drive', 'price': 300.00, 'description': 'All edited photos on USB drive'},
        ]
        
        for addon_data in addons_data:
            addon, created = Addon.objects.get_or_create(name=addon_data['name'], defaults=addon_data)
            if created:
                print(f"   Created addon: {addon.name}")
        
        # Create Backdrops
        backdrops_data = [
            'White Classic', 'Black Elegant', 'Blue Ocean', 'Pink Blush', 
            'Green Nature', 'Purple Royal', 'Red Passion', 'Yellow Sunshine',
            'Gray Modern', 'Beige Neutral', 'Coral Warm', 'Mint Fresh',
            'Navy Professional', 'Cream Vintage', 'Teal Modern', 'Rose Gold'
        ]
        
        for backdrop_name in backdrops_data:
            backdrop, created = Backdrop.objects.get_or_create(name=backdrop_name)
            if created:
                print(f"   Created backdrop: {backdrop.name}")
        
        # Create Creative Packages
        creative_packages = [
            'Vintage Film', 'Modern Minimalist', 'Artistic Black & White',
            'Bright & Colorful', 'Moody & Dramatic', 'Natural & Soft',
            'High Fashion', 'Retro Pop', 'Classic Portrait'
        ]
        
        for cp_name in creative_packages:
            cp, created = CreativePackage.objects.get_or_create(name=cp_name)
            if created:
                print(f"   Created creative package: {cp.name}")
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

def show_database_info():
    """Display database information"""
    try:
        from django.db import connection
        from bookings.models import Package, Addon, Backdrop, CreativePackage
        
        print(f"\nDatabase Information:")
        print(f"   Database Engine: {connection.vendor}")
        print(f"   Database Name: {connection.settings_dict['NAME']}")
        
        # Count records
        packages_count = Package.objects.count()
        addons_count = Addon.objects.count()
        backdrops_count = Backdrop.objects.count()
        creative_count = CreativePackage.objects.count()
        
        print(f"\nData Summary:")
        print(f"   Packages: {packages_count}")
        print(f"   Add-ons: {addons_count}")
        print(f"   Backdrops: {backdrops_count}")
        print(f"   Creative Packages: {creative_count}")
            
    except Exception as e:
        print(f"Error getting database info: {e}")

def main():
    """Main setup function"""
    print("Photobooth Booking System - Database Creation")
    print("=" * 50)
    
    # Step 1: Setup Django
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
    print("   1. Run: python manage.py runserver")
    print("   2. Visit: http://localhost:8000/admin (admin/admin123)")
    print("   3. Visit: http://localhost:8000 (main site)")
    print("\nUseful Commands:")
    print("   • View database: python manage.py show_db")
    print("   • Create admin user: python manage.py createsuperuser")
    print("   • Run migrations: python manage.py migrate")

if __name__ == '__main__':
    main()