"""
Script to update existing gallery categories to match the new category system.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import GalleryImage

def update_categories():
    """Update gallery categories from old to new format."""
    
    print("=" * 60)
    print("UPDATING GALLERY CATEGORIES")
    print("=" * 60)
    
    # Mapping from old categories to new ones
    category_mapping = {
        'solo_snap': 'solo',
        'twinning_moments': 'couple',
        'group_vibes': 'group',
        'academic_solo': 'academic',
        'academic_group': 'academic',
        'super_party': 'family',
    }
    
    galleries = GalleryImage.objects.all()
    
    if not galleries.exists():
        print("\n✅ No gallery images found. Nothing to update.")
        print("=" * 60)
        return
    
    print(f"\nFound {galleries.count()} gallery set(s)")
    print("\nUpdating categories...\n")
    
    updated_count = 0
    
    for gallery in galleries:
        old_category = gallery.category
        
        if old_category in category_mapping:
            new_category = category_mapping[old_category]
            gallery.category = new_category
            gallery.save(update_fields=['category'])
            
            print(f"✅ {gallery.title}")
            print(f"   {old_category} → {new_category}\n")
            updated_count += 1
        else:
            # Already using new format or unknown category
            if old_category in ['solo', 'couple', 'group', 'family', 'academic']:
                print(f"✓ {gallery.title} - Already using new format ({old_category})\n")
            else:
                print(f"⚠️  {gallery.title} - Unknown category: {old_category}")
                print(f"   Setting to 'solo' as default\n")
                gallery.category = 'solo'
                gallery.save(update_fields=['category'])
                updated_count += 1
    
    print("=" * 60)
    print(f"SUMMARY:")
    print(f"  Updated: {updated_count}")
    print(f"  Total: {galleries.count()}")
    print("=" * 60)

if __name__ == '__main__':
    update_categories()
