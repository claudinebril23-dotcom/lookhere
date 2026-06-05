import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Update existing null type values
        cursor.execute("UPDATE bookings_backdrop SET type = 'standard' WHERE type IS NULL;")
        print("Updated null type values")
        
        # Alter column to have default
        cursor.execute("ALTER TABLE bookings_backdrop ALTER COLUMN type SET DEFAULT 'standard';")
        print("Set default value for type column")
except Exception as e:
    print(f"Error: {e}")

print("Done!")