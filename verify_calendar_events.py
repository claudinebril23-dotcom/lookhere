"""
Verify that events are actually in Google Calendar.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking
from bookings.google_calendar import _get_service
from django.conf import settings
from datetime import datetime, timedelta

def verify_calendar_events():
    print("=" * 70)
    print("Verify Calendar Events")
    print("=" * 70)
    
    # Get Google Calendar service
    service = _get_service()
    if not service:
        print("\n❌ Could not connect to Google Calendar")
        return
    
    print(f"\n✅ Connected to Google Calendar")
    print(f"   Calendar ID: {settings.GOOGLE_CALENDAR_ID}")
    
    # Get all bookings with event IDs
    bookings_with_events = Booking.objects.exclude(
        google_calendar_event_id=''
    ).exclude(
        google_calendar_event_id__isnull=True
    ).order_by('-created_at')
    
    print(f"\n📊 Bookings with calendar event IDs: {bookings_with_events.count()}")
    
    if not bookings_with_events.exists():
        print("\n⚠️  No bookings have calendar event IDs")
        return
    
    print("\n" + "=" * 70)
    print("Checking each event in Google Calendar...")
    print("=" * 70)
    
    found_count = 0
    missing_count = 0
    
    for booking in bookings_with_events[:10]:  # Check first 10
        event_id = booking.google_calendar_event_id
        print(f"\n📋 Booking: {booking.reference_code}")
        print(f"   Customer: {booking.customer_name}")
        print(f"   Status: {booking.status}")
        print(f"   Date: {booking.date} {booking.time}")
        print(f"   Event ID: {event_id}")
        
        try:
            # Try to get the event from Google Calendar
            event = service.events().get(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                eventId=event_id
            ).execute()
            
            print(f"   ✅ FOUND in Google Calendar!")
            print(f"      Title: {event.get('summary', 'N/A')}")
            print(f"      Start: {event.get('start', {}).get('dateTime', 'N/A')}")
            print(f"      Status: {event.get('status', 'N/A')}")
            
            # Check if it's visible
            if event.get('status') == 'cancelled':
                print(f"      ⚠️  Event is CANCELLED (still in calendar but marked cancelled)")
            else:
                print(f"      ✅ Event is ACTIVE and visible")
            
            found_count += 1
            
        except Exception as e:
            print(f"   ❌ NOT FOUND in Google Calendar")
            print(f"      Error: {e}")
            missing_count += 1
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"   Events found in calendar: {found_count}")
    print(f"   Events missing from calendar: {missing_count}")
    
    if found_count > 0:
        print(f"\n✅ Events ARE in Google Calendar!")
        print(f"\n💡 If you don't see them in the calendar view:")
        print(f"   1. Make sure you're viewing the correct calendar:")
        print(f"      {settings.GOOGLE_CALENDAR_ID}")
        print(f"   2. Refresh the calendar page (Ctrl+R or Cmd+R)")
        print(f"   3. Check the date range - events might be on different dates")
        print(f"   4. Check if calendar is hidden in the sidebar")
        print(f"   5. Try viewing 'Month' or 'Week' view instead of 'Day'")
    
    # Get upcoming events from calendar
    print("\n" + "=" * 70)
    print("Upcoming Events in Google Calendar")
    print("=" * 70)
    
    try:
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("\n⚠️  No upcoming events found in calendar")
        else:
            print(f"\n✅ Found {len(events)} upcoming events:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                status = event.get('status', 'unknown')
                print(f"   • {start}: {summary} (status: {status})")
    
    except Exception as e:
        print(f"\n❌ Error fetching upcoming events: {e}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    try:
        verify_calendar_events()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
