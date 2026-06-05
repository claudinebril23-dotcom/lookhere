#!/usr/bin/env python
"""
Start Django Development Server for Photobooth Booking System
"""

import os
import sys
import django
from pathlib import Path

# Set up Django
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')

print("=" * 60)
print("Photobooth Booking System - Django Server")
print("=" * 60)
print()

# Check Django
try:
    import django
    print(f"Django version: {django.get_version()}")
except ImportError:
    print("ERROR: Django is not installed!")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Setup Django
try:
    django.setup()
    print("Django setup: OK")
except Exception as e:
    print(f"ERROR: Django setup failed: {e}")
    sys.exit(1)

# Check database
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("Database connection: OK")
except Exception as e:
    print(f"ERROR: Database connection failed: {e}")
    sys.exit(1)

# Check data
try:
    from bookings.models import Package
    count = Package.objects.count()
    print(f"Database data: OK ({count} packages)")
except Exception as e:
    print(f"ERROR: Could not load data: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("Server Information:")
print("=" * 60)
print("Main site: http://localhost:8000")
print("Admin panel: http://localhost:8000/admin")
print("Admin login: admin / admin123")
print()
print("Database: photobooth_db (PostgreSQL)")
print("=" * 60)
print()

# Start server
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'runserver'])