"""
Script to create calendar events for existing bookings that don't have them.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking
from bookings.google_calendar import create_calendar_event

def fix_existing_bookings():
    """Create calendar events for bookings that don't have them."""
    
    print("=" * 60)
    print("FIXING EXISTING BOOKINGS")
    print("=" * 60)
    
    # Find bookings without calendar events
    bookings_without_events = Booking.objects.filter(
        google_calendar_event_id__isnull=True
    ) | Booking.objects.filter(
        google_calendar_event_id=''
    )
    
    # Exclude cancelled bookings
    bookings_without_events = bookings_without_events.exclude(status='cancelled')
    
    count = bookings_without_events.count()
    
    if count == 0:
        print("\n✅ All bookings already have calendar events!")
        print("=" * 60)
        return
    
    print(f"\nFound {count} booking(s) without calendar events")
    print("\nCreating calendar events...\n")
    
    success_count = 0
    fail_count = 0
    
    for booking in bookings_without_events:
        print(f"Processing: {booking.reference_code} - {booking.customer_name}")
        print(f"  Date: {booking.date} {booking.time}")
        print(f"  Status: {booking.status}")
        
        event_id = create_calendar_event(booking)
        
        if event_id:
            booking.google_calendar_event_id = event_id
            booking.save(update_fields=['google_calendar_event_id'])
            print(f"  ✅ Calendar event created: {event_id}\n")
            success_count += 1
        else:
            print(f"  ❌ Failed to create calendar event\n")
            fail_count += 1
    
    print("=" * 60)
    print(f"SUMMARY:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    print(f"  📊 Total: {count}")
    print("=" * 60)

if __name__ == '__main__':
    fix_existing_bookings()
