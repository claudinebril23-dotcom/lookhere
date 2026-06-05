import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import GalleryImage

print("Populating gallery with sample data...")
print("=" * 50)

gallery_data = [
    {'title': 'Professional Headshots Collection', 'category': 'portrait', 'is_active': True},
    {'title': 'Happy Family Moments', 'category': 'family', 'is_active': True},
    {'title': 'Romantic Couple Sessions', 'category': 'portrait', 'is_active': True},
    {'title': 'Creative Self Portraits', 'category': 'self_portrait', 'is_active': True},
    {'title': 'Studio Setup Showcase', 'category': 'studio', 'is_active': True},
    {'title': 'Event Photography Highlights', 'category': 'event', 'is_active': True},
    {'title': 'Wedding Celebrations', 'category': 'wedding', 'is_active': True},
    {'title': 'Corporate Events', 'category': 'event', 'is_active': True},
]

for item in gallery_data:
    gallery, created = GalleryImage.objects.get_or_create(
        title=item['title'],
        defaults={'category': item['category'], 'is_active': item['is_active']}
    )
    if created:
        print(f"Created: {gallery.title}")
    else:
        print(f"Already exists: {gallery.title}")

print()
print(f"Total galleries: {GalleryImage.objects.count()}")
print("Gallery populated successfully!")