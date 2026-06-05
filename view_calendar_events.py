"""
Script to view all events in the Google Calendar.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configuration
CREDENTIALS_FILE = 'google_credentials.json'
CALENDAR_ID = 'dyienziidens353@gmail.com'

def view_calendar_events():
    """View all events in the calendar."""
    
    print("=" * 60)
    print("GOOGLE CALENDAR EVENTS")
    print("=" * 60)
    
    # Authenticate
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
    )
    
    service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
    
    # Get events from today onwards
    now = datetime.utcnow().isoformat() + 'Z'
    
    print(f"\nFetching events from {CALENDAR_ID}...\n")
    
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print('No upcoming events found.')
        else:
            print(f'Found {len(events)} upcoming event(s):\n')
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                event_id = event.get('id', 'No ID')
                
                print(f"{i}. {summary}")
                print(f"   Start: {start}")
                print(f"   Event ID: {event_id}")
                
                # Show description if it contains booking info
                description = event.get('description', '')
                if 'Reference:' in description:
                    lines = description.split('\n')
                    for line in lines[:3]:  # Show first 3 lines
                        if line.strip():
                            print(f"   {line}")
                print()
        
    except Exception as e:
        print(f"❌ Error fetching events: {e}")
    
    print("=" * 60)

if __name__ == '__main__':
    view_calendar_events()
