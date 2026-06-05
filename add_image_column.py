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
        cursor.execute("ALTER TABLE bookings_backdrop ADD COLUMN image VARCHAR(100) DEFAULT '';")
        print("Image column added to backdrop table")
except Exception as e:
    print(f"Column might already exist: {e}")

print("Done!")