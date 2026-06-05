"""
Test script to verify Google Calendar connection and list available calendars.
Run this to find your correct Calendar ID.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_calendar_connection():
    """Test Google Calendar API connection and list calendars."""
    
    print("=" * 60)
    print("GOOGLE CALENDAR CONNECTION TEST")
    print("=" * 60)
    
    # Check settings
    print(f"\n1. Checking settings...")
    print(f"   Credentials file: {settings.GOOGLE_CALENDAR_CREDENTIALS}")
    print(f"   Calendar ID: {settings.GOOGLE_CALENDAR_ID}")
    
    # Check if credentials file exists
    if not os.path.exists(settings.GOOGLE_CALENDAR_CREDENTIALS):
        print(f"\n❌ ERROR: Credentials file not found!")
        print(f"   Expected location: {settings.GOOGLE_CALENDAR_CREDENTIALS}")
        return
    
    print(f"   ✅ Credentials file exists")
    
    # Try to authenticate
    print(f"\n2. Authenticating with Google...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(settings.GOOGLE_CALENDAR_CREDENTIALS),
            scopes=['https://www.googleapis.com/auth/calendar'],
        )
        print(f"   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return
    
    # Build service
    print(f"\n3. Building Calendar service...")
    try:
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        print(f"   ✅ Service built successfully")
    except Exception as e:
        print(f"   ❌ Failed to build service: {e}")
        return
    
    # List calendars
    print(f"\n4. Listing available calendars...")
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print(f"   ⚠️  No calendars found")
        else:
            print(f"   ✅ Found {len(calendars)} calendar(s):\n")
            for i, calendar in enumerate(calendars, 1):
                print(f"   {i}. {calendar['summary']}")
                print(f"      ID: {calendar['id']}")
                print(f"      Access Role: {calendar.get('accessRole', 'N/A')}")
                if calendar['id'] == settings.GOOGLE_CALENDAR_ID:
                    print(f"      👉 THIS IS YOUR CONFIGURED CALENDAR")
                print()
    except Exception as e:
        print(f"   ❌ Failed to list calendars: {e}")
        return
    
    # Test creating an event
    print(f"\n5. Testing event creation on configured calendar...")
    if not settings.GOOGLE_CALENDAR_ID:
        print(f"   ⚠️  GOOGLE_CALENDAR_ID is not set in .env")
        return
    
    try:
        test_event = {
            'summary': '🧪 Test Event - Look Here Studio',
            'description': 'This is a test event. You can delete it.',
            'start': {
                'dateTime': '2026-05-10T10:00:00',
                'timeZone': 'Asia/Manila',
            },
            'end': {
                'dateTime': '2026-05-10T11:00:00',
                'timeZone': 'Asia/Manila',
            },
            'colorId': '3',
        }
        
        event = service.events().insert(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            body=test_event
        ).execute()
        
        print(f"   ✅ Test event created successfully!")
        print(f"   Event ID: {event['id']}")
        print(f"   Event Link: {event.get('htmlLink', 'N/A')}")
        
        # Delete the test event
        print(f"\n6. Cleaning up test event...")
        service.events().delete(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event['id']
        ).execute()
        print(f"   ✅ Test event deleted")
        
    except Exception as e:
        print(f"   ❌ Failed to create test event: {e}")
        print(f"\n   Possible issues:")
        print(f"   - Calendar ID might be incorrect")
        print(f"   - Service account doesn't have access to this calendar")
        print(f"   - Calendar doesn't exist")
        return
    
    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS PASSED - Google Calendar is working!")
    print(f"=" * 60)

if __name__ == '__main__':
    test_calendar_connection()
