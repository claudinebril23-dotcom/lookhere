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
        # Create GalleryImage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings_galleryimage (
                id BIGINT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL
            );
        """)
        print("Created bookings_galleryimage table")
        
        # Create GalleryImageFile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings_galleryimagefile (
                id BIGINT PRIMARY KEY,
                gallery_id BIGINT NOT NULL,
                image VARCHAR(100) NOT NULL,
                "order" INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (gallery_id) REFERENCES bookings_galleryimage(id)
            );
        """)
        print("Created bookings_galleryimagefile table")
        
except Exception as e:
    print(f"Error: {e}")

print("Done!")