#!/usr/bin/env python
"""
Database Setup Script for Photobooth Booking System
This script helps set up PostgreSQL database and create all necessary tables
"""

import os
import sys
import django
import importlib
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    # Check psycopg2 without importing it
    try:
        importlib.import_module('psycopg2')
    except ImportError:
        missing_deps.append('psycopg2-binary')
    
    # Check dotenv
    try:
        importlib.import_module('dotenv')
    except ImportError:
        missing_deps.append('python-dotenv')
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n📦 Please install them first:")
        print(f"   pip install {' '.join(missing_deps)}")
        print("\n   Or install all requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def setup_django():
    """Setup Django environment"""
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        return False

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Import modules dynamically to avoid Pylance warnings
        psycopg2 = importlib.import_module('psycopg2')
        extensions = importlib.import_module('psycopg2.extensions')
        from django.conf import settings
        
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        db_name = settings.DATABASES['default']['NAME']
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists!")
            
        cursor.close()
        conn.close()
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Please install: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"Error creating database: {e}")
        print("\nTroubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check your .env file for correct credentials")
        print("   3. Verify PostgreSQL is installed and accessible")
        print("\nCurrent settings:")
        try:
            from django.conf import settings
            db_config = settings.DATABASES['default']
            print(f"   Host: {db_config['HOST']}")
            print(f"   Port: {db_config['PORT']}")
            print(f"   User: {db_config['USER']}")
            print(f"   Database: {db_config['NAME']}")
        except:
            print("   Could not load database settings")
        return False

def run_migrations():
    """Run Django migrations to create tables"""
    try:
        from django.core.management import execute_from_command_line
        
        print("\n🔄 Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("\n🔄 Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def create_superuser():
    """Create a superuser for admin access"""
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            print("\n👤 Creating superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@photoboothsystem.com',
                password='admin123'
            )
            print("✅ Superuser created!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change this password in production!")
        else:
            print("✅ Superuser already exists!")
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

def populate_sample_data():
    """Populate database with sample data"""
    try:
        from bookings.models import Package, Addon, Backdrop, CreativePackage
        
        print("\n📦 Creating sample data...")
        
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
            Package.objects.get_or_create(name=pkg_data['name'], defaults=pkg_data)
        
        # Create Addons
        addons_data = [
            {'name': 'Extra 30 minutes', 'price': 500.00, 'description': 'Additional 30 minutes of shooting time'},
            {'name': 'Rush Processing', 'price': 800.00, 'description': 'Get your photos in 24 hours'},
            {'name': 'Extra Backdrop', 'price': 300.00, 'description': 'Additional backdrop setup'},
            {'name': 'Props Package', 'price': 400.00, 'description': 'Fun props and accessories'},
            {'name': 'Digital Album', 'price': 1200.00, 'description': 'Professional digital photo album'},
        ]
        
        for addon_data in addons_data:
            Addon.objects.get_or_create(name=addon_data['name'], defaults=addon_data)
        
        # Create Backdrops
        backdrops_data = [
            'White Classic', 'Black Elegant', 'Blue Ocean', 'Pink Blush', 
            'Green Nature', 'Purple Royal', 'Red Passion', 'Yellow Sunshine',
            'Gray Modern', 'Beige Neutral', 'Coral Warm', 'Mint Fresh'
        ]
        
        for backdrop_name in backdrops_data:
            Backdrop.objects.get_or_create(name=backdrop_name)
        
        # Create Creative Packages
        creative_packages = [
            'Vintage Film', 'Modern Minimalist', 'Artistic Black & White',
            'Bright & Colorful', 'Moody & Dramatic', 'Natural & Soft'
        ]
        
        for cp_name in creative_packages:
            CreativePackage.objects.get_or_create(name=cp_name)
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def show_database_info():
    """Display database connection information"""
    try:
        from django.db import connection
        from django.conf import settings
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version_result = cursor.fetchone()
            version = version_result[0] if version_result else "Unknown"
            
            cursor.execute("SELECT current_database();")
            db_result = cursor.fetchone()
            db_name = db_result[0] if db_result else "Unknown"
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
        print(f"Database Information:")
        print(f"   PostgreSQL Version: {version}")
        print(f"   Database Name: {db_name}")
        print(f"   Host: {settings.DATABASES['default']['HOST']}")
        print(f"   Port: {settings.DATABASES['default']['PORT']}")
        print(f"   User: {settings.DATABASES['default']['USER']}")
        
        print(f"\nTables Created ({len(tables)}):")
        for table in tables:
            print(f"   • {table}")
            
    except Exception as e:
        print(f"❌ Error getting database info: {e}")

def main():
    """Main setup function"""
    print("Photobooth Booking System - Database Setup")
    print("=" * 50)
    
    # Step 0: Check dependencies
    if not check_dependencies():
        return
    
    # Step 1: Setup Django
    if not setup_django():
        return
    
    # Step 2: Create database
    if not create_database():
        return
    
    # Step 3: Run migrations
    if not run_migrations():
        return
    
    # Step 4: Create superuser
    create_superuser()
    
    # Step 5: Populate sample data
    populate_sample_data()
    
    # Step 6: Show database info
    show_database_info()
    
    print("\nDatabase setup completed successfully!")
    print("\nNext Steps:")
    print("   1. Update your .env file with correct database credentials")
    print("   2. Run: python manage.py runserver")
    print("   3. Visit: http://localhost:8000/admin (admin/admin123)")
    print("   4. Visit: http://localhost:8000 (main site)")

if __name__ == '__main__':
    main()