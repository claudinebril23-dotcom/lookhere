"""
Clean up duplicate calendar events.
This script will help identify and remove duplicate events from Google Calendar.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Booking
from bookings.google_calendar import _get_service, delete_calendar_event
from django.conf import settings
from datetime import datetime

def find_and_cleanup_duplicates():
    """Find and clean up duplicate calendar events."""
    
    print("=" * 70)
    print("Google Calendar Duplicate Event Cleanup")
    print("=" * 70)
    
    service = _get_service()
    if not service:
        print("❌ Could not connect to Google Calendar")
        return
    
    print("\n📋 Fetching all events from Google Calendar...")
    
    try:
        # Get all events from the calendar
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime',
            timeMin=datetime.utcnow().isoformat() + 'Z'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Found {len(events)} upcoming events in calendar")
        
        # Group events by customer name and time
        event_groups = {}
        for event in events:
            summary = event.get('summary', '')
            start = event.get('start', {}).get('dateTime', '')
            key = f"{summary}_{start}"
            
            if key not in event_groups:
                event_groups[key] = []
            event_groups[key].append(event)
        
        # Find duplicates
        duplicates = {k: v for k, v in event_groups.items() if len(v) > 1}
        
        if not duplicates:
            print("\n✅ No duplicate events found!")
            return
        
        print(f"\n⚠️  Found {len(duplicates)} sets of duplicate events:")
        
        for key, events_list in duplicates.items():
            print(f"\n  📅 {events_list[0].get('summary', 'Unknown')}")
            print(f"     Time: {events_list[0].get('start', {}).get('dateTime', 'Unknown')}")
            print(f"     Duplicates: {len(events_list)} events")
            
            # Show all event IDs
            for i, event in enumerate(events_list, 1):
                event_id = event.get('id', 'Unknown')
                print(f"       {i}. Event ID: {event_id}")
        
        # Ask user if they want to delete duplicates
        print("\n" + "=" * 70)
        response = input("Do you want to delete the duplicate events? (keep only the first one) [y/N]: ")
        
        if response.lower() == 'y':
            print("\n🗑️  Deleting duplicate events...")
            deleted_count = 0
            
            for key, events_list in duplicates.items():
                # Keep the first event, delete the rest
                for event in events_list[1:]:
                    event_id = event.get('id')
                    try:
                        service.events().delete(
                            calendarId=settings.GOOGLE_CALENDAR_ID,
                            eventId=event_id
                        ).execute()
                        print(f"  ✅ Deleted event: {event_id}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to delete {event_id}: {e}")
            
            print(f"\n✅ Deleted {deleted_count} duplicate events")
            print("✅ Cleanup complete!")
        else:
            print("\n❌ Cleanup cancelled")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("📝 Note: The duplicate event issue has been fixed in the code.")
    print("   Future bookings will not create duplicates.")
    print("=" * 70)


if __name__ == '__main__':
    find_and_cleanup_duplicates()
