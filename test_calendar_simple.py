"""
Simple test script to verify Google Calendar connection.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
CREDENTIALS_FILE = 'google_credentials.json'
CALENDAR_ID = 'dyienziidens353@gmail.com'

def test_calendar():
    """Test Google Calendar API connection."""
    
    print("=" * 60)
    print("GOOGLE CALENDAR CONNECTION TEST")
    print("=" * 60)
    
    # Check if credentials file exists
    print(f"\n1. Checking credentials file...")
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"   ❌ ERROR: {CREDENTIALS_FILE} not found!")
        return
    print(f"   ✅ Credentials file exists")
    
    # Authenticate
    print(f"\n2. Authenticating...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
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
                if calendar['id'] == CALENDAR_ID:
                    print(f"      👉 THIS IS YOUR CONFIGURED CALENDAR")
                print()
    except Exception as e:
        print(f"   ❌ Failed to list calendars: {e}")
        return
    
    # Test creating an event
    print(f"\n5. Testing event creation...")
    print(f"   Using Calendar ID: {CALENDAR_ID}")
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
            calendarId=CALENDAR_ID,
            body=test_event
        ).execute()
        
        print(f"   ✅ Test event created successfully!")
        print(f"   Event ID: {event['id']}")
        print(f"   Event Link: {event.get('htmlLink', 'N/A')}")
        
        # Delete the test event
        print(f"\n6. Cleaning up test event...")
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event['id']
        ).execute()
        print(f"   ✅ Test event deleted")
        
    except Exception as e:
        print(f"   ❌ Failed to create test event: {e}")
        print(f"\n   Possible issues:")
        print(f"   - Calendar ID might be incorrect")
        print(f"   - Service account doesn't have access to this calendar")
        print(f"   - You need to share the calendar with the service account email")
        return
    
    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS PASSED - Google Calendar is working!")
    print(f"=" * 60)

if __name__ == '__main__':
    test_calendar()
