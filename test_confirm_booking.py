"""
Test script to simulate confirming a booking and see debug output.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking

def test_confirm_booking():
    print("=" * 70)
    print("Test: Confirm Booking and Create Calendar Event")
    print("=" * 70)
    
    # Find a pending booking
    pending_bookings = Booking.objects.filter(status='pending')
    
    if not pending_bookings.exists():
        print("\n❌ No pending bookings found to test with")
        print("   Create a booking first at: http://127.0.0.1:8000/book/")
        return
    
    booking = pending_bookings.first()
    
    print(f"\n📋 Found pending booking:")
    print(f"   Reference: {booking.reference_code}")
    print(f"   Customer: {booking.customer_name}")
    print(f"   Status: {booking.status}")
    print(f"   Event ID: {booking.google_calendar_event_id or 'None'}")
    
    print(f"\n🔄 Changing status to 'paid'...")
    print("=" * 70)
    
    # Change status to paid
    booking.status = 'paid'
    booking.save()
    
    print("=" * 70)
    print(f"\n✅ Status changed to 'paid'")
    
    # Refresh from database
    booking.refresh_from_db()
    
    print(f"\n📊 After save:")
    print(f"   Status: {booking.status}")
    print(f"   Event ID: {booking.google_calendar_event_id or 'None'}")
    
    if booking.google_calendar_event_id:
        print(f"\n✅ SUCCESS: Calendar event created!")
        print(f"   Event ID: {booking.google_calendar_event_id}")
        print(f"\n   Check Google Calendar to verify the event appears")
    else:
        print(f"\n❌ FAILED: No calendar event ID saved")
        print(f"\n   Check the console output above for DEBUG messages")
        print(f"   Look for:")
        print(f"   - 'DEBUG: Status changed from pending to paid'")
        print(f"   - 'DEBUG: _handle_status_change called'")
        print(f"   - 'DEBUG: No event_id, creating new calendar event'")
        print(f"   - 'Google Calendar: ✅ created event'")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    try:
        test_confirm_booking()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
