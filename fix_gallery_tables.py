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
        # Drop and recreate the table with proper sequence
        cursor.execute("DROP TABLE IF EXISTS bookings_galleryimagefile CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS bookings_galleryimage CASCADE;")
        
        # Create sequence
        cursor.execute("CREATE SEQUENCE bookings_galleryimage_id_seq START 1;")
        
        # Create GalleryImage table with proper ID
        cursor.execute("""
            CREATE TABLE bookings_galleryimage (
                id BIGINT PRIMARY KEY DEFAULT nextval('bookings_galleryimage_id_seq'),
                title VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Created bookings_galleryimage table with sequence")
        
        # Create sequence for GalleryImageFile
        cursor.execute("CREATE SEQUENCE bookings_galleryimagefile_id_seq START 1;")
        
        # Create GalleryImageFile table
        cursor.execute("""
            CREATE TABLE bookings_galleryimagefile (
                id BIGINT PRIMARY KEY DEFAULT nextval('bookings_galleryimagefile_id_seq'),
                gallery_id BIGINT NOT NULL,
                image VARCHAR(100) NOT NULL,
                "order" INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gallery_id) REFERENCES bookings_galleryimage(id) ON DELETE CASCADE
            );
        """)
        print("Created bookings_galleryimagefile table with sequence")
        
except Exception as e:
    print(f"Error: {e}")

print("Done!")