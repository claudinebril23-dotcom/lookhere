"""
Google Calendar Sync Diagnostic Tool
=====================================
This script checks if bookings are properly syncing to Google Calendar.
Run this to diagnose any calendar integration issues.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking
from bookings.google_calendar import _get_service, create_calendar_event
from django.conf import settings
from datetime import datetime, timedelta


def check_google_calendar_setup():
    """Check if Google Calendar is properly configured."""
    print("\n" + "="*70)
    print("GOOGLE CALENDAR CONFIGURATION CHECK")
    print("="*70 + "\n")
    
    # Check 1: Credentials file
    print("1. Checking credentials file...")
    creds_path = settings.GOOGLE_CALENDAR_CREDENTIALS
    if os.path.exists(creds_path):
        print(f"   ✅ Credentials file found: {creds_path}")
    else:
        print(f"   ❌ Credentials file NOT found: {creds_path}")
        print(f"   → Download from Google Cloud Console and place it here")
        return False
    
    # Check 2: Calendar ID
    print("\n2. Checking Calendar ID...")
    calendar_id = settings.GOOGLE_CALENDAR_ID
    if calendar_id:
        print(f"   ✅ Calendar ID configured: {calendar_id}")
    else:
        print(f"   ❌ Calendar ID NOT configured")
        print(f"   → Add GOOGLE_CALENDAR_ID to your .env file")
        return False
    
    # Check 3: Google API packages
    print("\n3. Checking Google API packages...")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        print(f"   ✅ Google API packages installed")
    except ImportError as e:
        print(f"   ❌ Google API packages NOT installed")
        print(f"   → Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    
    # Check 4: Service connection
    print("\n4. Testing Google Calendar service connection...")
    service = _get_service()
    if service:
        print(f"   ✅ Successfully connected to Google Calendar API")
        
        # Try to fetch calendar info
        try:
            calendar = service.calendars().get(calendarId=calendar_id).execute()
            print(f"   ✅ Calendar accessible: {calendar.get('summary', 'Unknown')}")
        except Exception as e:
            print(f"   ⚠️  Calendar accessible but got error: {e}")
            print(f"   → Make sure the service account has access to this calendar")
            print(f"   → Share calendar with: (check email in google_credentials.json)")
    else:
        print(f"   ❌ Failed to connect to Google Calendar API")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED - Google Calendar is properly configured!")
    print("="*70 + "\n")
    return True


def check_bookings_sync():
    """Check which bookings have calendar events."""
    print("\n" + "="*70)
    print("BOOKINGS SYNC STATUS")
    print("="*70 + "\n")
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=30)
    ).order_by('-created_at')[:20]
    
    if not recent_bookings:
        print("No bookings found in the last 30 days.\n")
        return
    
    print(f"Checking {recent_bookings.count()} recent bookings...\n")
    
    synced_count = 0
    not_synced_count = 0
    
    for booking in recent_bookings:
        has_event = bool(booking.google_calendar_event_id)
        status_icon = "✅" if has_event else "❌"
        
        print(f"{status_icon} {booking.reference_code} | {booking.status.upper()} | {booking.date} {booking.time}")
        print(f"   Customer: {booking.customer_name}")
        print(f"   Package: {booking.package.name}")
        
        if has_event:
            print(f"   Calendar Event ID: {booking.google_calendar_event_id}")
            synced_count += 1
        else:
            print(f"   ⚠️  No calendar event ID found")
            not_synced_count += 1
        
        print()
    
    print("="*70)
    print(f"SUMMARY: {synced_count} synced | {not_synced_count} not synced")
    print("="*70 + "\n")


def list_calendar_events():
    """List events from Google Calendar."""
    print("\n" + "="*70)
    print("GOOGLE CALENDAR EVENTS")
    print("="*70 + "\n")
    
    service = _get_service()
    if not service:
        print("❌ Cannot connect to Google Calendar\n")
        return
    
    try:
        # Get events from today onwards
        now = datetime.utcnow().isoformat() + 'Z'
        
        print("Fetching events from Google Calendar...\n")
        
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("No upcoming events found in Google Calendar.\n")
            return
        
        print(f"Found {len(events)} upcoming events:\n")
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            event_id = event.get('id')
            status = event.get('status', 'confirmed')
            
            status_icon = "✅" if status == 'confirmed' else "❌"
            
            print(f"{status_icon} {start} | {summary}")
            print(f"   Event ID: {event_id}")
            print(f"   Status: {status}")
            print()
        
    except Exception as e:
        print(f"❌ Error fetching calendar events: {e}\n")
        import traceback
        traceback.print_exc()


def test_create_event():
    """Test creating a calendar event for a booking."""
    print("\n" + "="*70)
    print("TEST: CREATE CALENDAR EVENT")
    print("="*70 + "\n")
    
    # Find a booking without a calendar event
    booking = Booking.objects.filter(
        google_calendar_event_id__isnull=True,
        status__in=['confirmed', 'paid']
    ).first()
    
    if not booking:
        print("No bookings found without calendar events.\n")
        print("All bookings are already synced! ✅\n")
        return
    
    print(f"Testing with booking: {booking.reference_code}")
    print(f"Customer: {booking.customer_name}")
    print(f"Date: {booking.date} {booking.time}")
    print(f"Package: {booking.package.name}")
    print()
    
    response = input("Create calendar event for this booking? (y/n): ")
    
    if response.lower() == 'y':
        print("\nCreating calendar event...")
        event_id = create_calendar_event(booking)
        
        if event_id:
            # Save the event ID
            booking.google_calendar_event_id = event_id
            booking.save(update_fields=['google_calendar_event_id'])
            
            print(f"\n✅ SUCCESS! Calendar event created: {event_id}")
            print(f"✅ Event ID saved to booking\n")
        else:
            print(f"\n❌ Failed to create calendar event\n")
    else:
        print("\nSkipped.\n")


def main():
    """Main diagnostic function."""
    print("\n" + "="*70)
    print("GOOGLE CALENDAR SYNC DIAGNOSTIC TOOL")
    print("Look Here Self Portrait Studio - Photobooth Booking System")
    print("="*70)
    
    # Step 1: Check configuration
    if not check_google_calendar_setup():
        print("\n⚠️  Please fix the configuration issues above before proceeding.\n")
        return
    
    # Step 2: Check bookings sync status
    check_bookings_sync()
    
    # Step 3: List calendar events
    list_calendar_events()
    
    # Step 4: Offer to test creating an event
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70 + "\n")
    
    response = input("Would you like to test creating a calendar event? (y/n): ")
    if response.lower() == 'y':
        test_create_event()
    
    print("\n" + "="*70)
    print("TIPS:")
    print("="*70)
    print("1. Make sure the service account email has access to the calendar")
    print("2. Check that GOOGLE_CALENDAR_ID in .env matches your calendar")
    print("3. Bookings should automatically create calendar events when created")
    print("4. Status changes (pending → paid) should update calendar events")
    print("5. Check Django logs for any error messages")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
