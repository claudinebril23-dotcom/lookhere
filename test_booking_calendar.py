"""
Test script to verify booking calendar integration.
"""

import os
import django
from datetime import date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking, Package, Backdrop
from bookings.google_calendar import create_calendar_event

def test_booking_calendar():
    """Test creating a calendar event for a booking."""
    
    print("=" * 60)
    print("BOOKING CALENDAR INTEGRATION TEST")
    print("=" * 60)
    
    # Get a package
    print("\n1. Getting test package...")
    try:
        package = Package.objects.first()
        if not package:
            print("   ❌ No packages found in database")
            return
        print(f"   ✅ Using package: {package.name}")
    except Exception as e:
        print(f"   ❌ Error getting package: {e}")
        return
    
    # Get a backdrop
    print("\n2. Getting test backdrop...")
    try:
        backdrop = Backdrop.objects.first()
        if backdrop:
            print(f"   ✅ Using backdrop: {backdrop.name}")
        else:
            print("   ⚠️  No backdrops found, will use None")
    except Exception as e:
        print(f"   ⚠️  Error getting backdrop: {e}")
        backdrop = None
    
    # Create a test booking
    print("\n3. Creating test booking...")
    try:
        booking = Booking.objects.create(
            reference_code='TEST-12345',
            date=date(2026, 5, 15),
            time=time(14, 0),
            customer_name='Test Customer',
            email='test@example.com',
            phone='09123456789',
            package=package,
            backdrop=backdrop,
            total_price=package.base_price,
            status='pending',
        )
        print(f"   ✅ Booking created: {booking.reference_code}")
        print(f"   Calendar Event ID: {booking.google_calendar_event_id or 'Not set'}")
    except Exception as e:
        print(f"   ❌ Error creating booking: {e}")
        return
    
    # Check if calendar event was created
    print("\n4. Checking calendar event...")
    if booking.google_calendar_event_id:
        print(f"   ✅ Calendar event created: {booking.google_calendar_event_id}")
    else:
        print(f"   ❌ No calendar event ID saved")
        print(f"   Trying to create manually...")
        event_id = create_calendar_event(booking)
        if event_id:
            print(f"   ✅ Manual creation successful: {event_id}")
        else:
            print(f"   ❌ Manual creation failed")
    
    # Clean up
    print("\n5. Cleaning up test booking...")
    try:
        booking.delete()
        print(f"   ✅ Test booking deleted")
    except Exception as e:
        print(f"   ⚠️  Error deleting booking: {e}")
    
    print("\n" + "=" * 60)
    if booking.google_calendar_event_id:
        print("✅ BOOKING CALENDAR INTEGRATION WORKING!")
    else:
        print("⚠️  BOOKING CREATED BUT NO CALENDAR EVENT")
        print("\nPossible issues:")
        print("- Signals might not be firing")
        print("- Check Django console for error messages")
    print("=" * 60)

if __name__ == '__main__':
    test_booking_calendar()
