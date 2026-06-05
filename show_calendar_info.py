"""
Show detailed calendar information to help identify the issue.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.google_calendar import _get_service
from django.conf import settings

def show_calendar_info():
    print("=" * 70)
    print("Google Calendar Configuration")
    print("=" * 70)
    
    # Show settings
    print(f"\n📋 Configuration:")
    print(f"   GOOGLE_CALENDAR_ID: {settings.GOOGLE_CALENDAR_ID}")
    print(f"   Credentials file: {settings.GOOGLE_CALENDAR_CREDENTIALS}")
    
    # Connect to Google Calendar
    service = _get_service()
    if not service:
        print("\n❌ Could not connect to Google Calendar")
        return
    
    print(f"\n✅ Connected to Google Calendar API")
    
    # Get calendar details
    try:
        calendar = service.calendars().get(calendarId=settings.GOOGLE_CALENDAR_ID).execute()
        print(f"\n📅 Calendar Details:")
        print(f"   ID: {calendar.get('id')}")
        print(f"   Summary: {calendar.get('summary', 'N/A')}")
        print(f"   Description: {calendar.get('description', 'N/A')}")
        print(f"   Time Zone: {calendar.get('timeZone', 'N/A')}")
    except Exception as e:
        print(f"\n⚠️  Could not get calendar details: {e}")
    
    # List all calendars accessible by the service account
    print(f"\n📋 All Calendars Accessible by Service Account:")
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print("   No calendars found")
        else:
            for cal in calendars:
                cal_id = cal.get('id')
                summary = cal.get('summary', 'No name')
                primary = ' (PRIMARY)' if cal.get('primary') else ''
                selected = ' ← USING THIS ONE' if cal_id == settings.GOOGLE_CALENDAR_ID else ''
                print(f"   • {summary}{primary}{selected}")
                print(f"     ID: {cal_id}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Show recent events
    print(f"\n📅 Recent Events in Calendar ({settings.GOOGLE_CALENDAR_ID}):")
    try:
        from datetime import datetime, timedelta
        
        # Get events from 7 days ago to 30 days in future
        time_min = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
        time_max = (datetime.now() + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("   ⚠️  No events found in this calendar")
            print(f"\n   This could mean:")
            print(f"   1. Events are in a different calendar")
            print(f"   2. Events are outside the date range (last 7 days to next 30 days)")
            print(f"   3. Calendar is not shared with the service account")
        else:
            print(f"   ✅ Found {len(events)} events:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                status = event.get('status', 'unknown')
                event_id = event.get('id', 'unknown')
                print(f"\n   • {summary}")
                print(f"     Date: {start}")
                print(f"     Status: {status}")
                print(f"     Event ID: {event_id[:20]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Show direct link to calendar
    print(f"\n" + "=" * 70)
    print(f"🔗 Direct Links:")
    print(f"=" * 70)
    
    calendar_id = settings.GOOGLE_CALENDAR_ID
    
    # URL encode the calendar ID
    import urllib.parse
    encoded_id = urllib.parse.quote(calendar_id)
    
    print(f"\n1. View this specific calendar:")
    print(f"   https://calendar.google.com/calendar/u/0/r?cid={encoded_id}")
    
    print(f"\n2. View all calendars:")
    print(f"   https://calendar.google.com/calendar/u/0/r")
    
    print(f"\n3. Calendar settings:")
    print(f"   https://calendar.google.com/calendar/u/0/r/settings")
    
    print(f"\n" + "=" * 70)
    print(f"💡 Troubleshooting:")
    print(f"=" * 70)
    print(f"\n1. Make sure you're logged into: {calendar_id}")
    print(f"2. Check if the calendar is visible in the left sidebar")
    print(f"3. Click the calendar name in sidebar to show/hide events")
    print(f"4. Try the direct link above to view this specific calendar")
    print(f"5. Refresh the page (Ctrl+R or Cmd+R)")
    
    print(f"\n" + "=" * 70)

if __name__ == '__main__':
    try:
        show_calendar_info()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
