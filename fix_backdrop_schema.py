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
        # Add type column if it doesn't exist
        cursor.execute("ALTER TABLE bookings_backdrop ADD COLUMN type VARCHAR(50) DEFAULT 'standard';")
        print("Type column added")
except Exception as e:
    print(f"Type column might already exist: {e}")

print("Done!")