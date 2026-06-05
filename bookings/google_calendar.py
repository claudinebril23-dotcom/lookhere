"""
Google Calendar integration for Look Here Self Portrait Studio.
Creates, updates, and deletes calendar events when bookings change.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Check if Google Calendar packages are installed
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_PACKAGES_AVAILABLE = True
except ImportError:
    GOOGLE_PACKAGES_AVAILABLE = False
    logger.warning(
        "Google Calendar packages not installed. "
        "Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )


def _get_service():
    """Build and return an authenticated Google Calendar service.
    
    Supports two ways to provide credentials:
    1. GOOGLE_CREDENTIALS_JSON env var — full JSON string (used on Railway)
    2. google_credentials.json file on disk (used locally)
    """
    if not GOOGLE_PACKAGES_AVAILABLE:
        print("Google Calendar: ❌ Required packages not installed")
        print("   Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None

    import os, json

    try:
        # Option 1: credentials from environment variable (Railway)
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
        if creds_json:
            info = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=['https://www.googleapis.com/auth/calendar'],
            )
        else:
            # Option 2: credentials from file (local development)
            credentials = service_account.Credentials.from_service_account_file(
                str(settings.GOOGLE_CALENDAR_CREDENTIALS),
                scopes=['https://www.googleapis.com/auth/calendar'],
            )

        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        return service

    except FileNotFoundError:
        print(f"Google Calendar: ❌ Credentials file not found: {settings.GOOGLE_CALENDAR_CREDENTIALS}")
        logger.error(f"Google Calendar: credentials file not found — {settings.GOOGLE_CALENDAR_CREDENTIALS}")
        return None
    except Exception as e:
        print(f"Google Calendar: ❌ Failed to build service — {e}")
        logger.error(f"Google Calendar: failed to build service — {e}")
        return None


def _event_body(booking):
    """Build the Google Calendar event dict from a Booking instance."""
    date_str = booking.date.strftime('%Y-%m-%d')
    hour = booking.time.hour
    minute = booking.time.minute
    # Session is 1 hour (60 minutes)
    total_minutes = hour * 60 + minute + 60
    end_hour = total_minutes // 60
    end_minute = total_minutes % 60

    try:
        addons = ', '.join([a.name for a in booking.addons.all()]) or 'None'
    except Exception:
        addons = 'None'
    backdrop = booking.backdrop.name if booking.backdrop else 'Not selected'

    description = (
        f"📋 Reference: {booking.reference_code}\n"
        f"👤 Customer: {booking.customer_name}\n"
        f"📧 Email: {booking.email}\n"
        f"📱 Phone: {booking.phone}\n"
        f"📦 Package: {booking.package.name}\n"
        f"🎨 Backdrop: {backdrop}\n"
        f"✨ Add-ons: {addons}\n"
        f"💰 Total: ₱{booking.total_price:,.2f}\n"
        f"📊 Status: {booking.get_status_display()}\n"
    )

    # Set color based on status: Blue (9) for confirmed, Green (10) for paid
    color_id = '10' if booking.status == 'paid' else '9'

    return {
        'summary': f"📸 {booking.customer_name} — {booking.package.name}",
        'description': description,
        'start': {
            'dateTime': f"{date_str}T{hour:02d}:{minute:02d}:00",
            'timeZone': 'Asia/Manila',
        },
        'end': {
            'dateTime': f"{date_str}T{end_hour:02d}:{end_minute:02d}:00",
            'timeZone': 'Asia/Manila',
        },
        'colorId': color_id,
    }


def create_calendar_event(booking):
    """Create a Google Calendar event for a new booking. Returns the event ID."""
    if not settings.GOOGLE_CALENDAR_ID:
        print("Google Calendar: ⚠️  GOOGLE_CALENDAR_ID not set in .env — skipping")
        print("   Add this to your .env file: GOOGLE_CALENDAR_ID=primary")
        return None

    service = _get_service()
    if not service:
        print("Google Calendar: ⚠️  Could not build service — skipping")
        return None

    try:
        event = service.events().insert(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            body=_event_body(booking),
        ).execute()
        event_id = event.get('id')
        print(f"Google Calendar: ✅ Created event {event_id} for {booking.reference_code}")
        logger.info(f"Google Calendar: created event {event_id} for {booking.reference_code}")
        return event_id
    except Exception as e:
        print(f"Google Calendar: ❌ Failed to create event for {booking.reference_code}")
        print(f"   Error: {e}")
        print(f"   Calendar ID: {settings.GOOGLE_CALENDAR_ID}")
        print(f"   Possible fixes:")
        print(f"   1. Make sure Calendar ID is correct (try 'primary')")
        print(f"   2. Share calendar with service account email from google_credentials.json")
        logger.error(f"Google Calendar: failed to create event for {booking.reference_code} — {e}")
        return None


def update_calendar_event(booking, event_id):
    """Update an existing Google Calendar event (e.g. status changed to Paid)."""
    if not settings.GOOGLE_CALENDAR_ID or not event_id:
        return False

    service = _get_service()
    if not service:
        return False

    try:
        service.events().update(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event_id,
            body=_event_body(booking),
        ).execute()
        logger.info(f"Google Calendar: updated event {event_id} for booking {booking.reference_code}")
        return True
    except Exception as e:
        logger.error(f"Google Calendar: failed to update event {event_id} — {e}")
        return False


def cancel_calendar_event(booking, event_id):
    """Mark a Google Calendar event as cancelled (instead of deleting it)."""
    if not settings.GOOGLE_CALENDAR_ID or not event_id:
        print(f"Google Calendar: ⚠️ Cannot cancel event - missing calendar ID or event ID")
        return False

    service = _get_service()
    if not service:
        print(f"Google Calendar: ⚠️ Cannot cancel event - service not available")
        return False

    try:
        print(f"Google Calendar: 🔄 Fetching event {event_id} to mark as cancelled...")
        
        # Get the current event
        event = service.events().get(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event_id,
        ).execute()
        
        print(f"Google Calendar: ✅ Event fetched, updating to cancelled status...")
        
        # Update the event to mark it as cancelled
        event['summary'] = f"❌ CANCELLED - {booking.customer_name} — {booking.package.name}"
        event['status'] = 'cancelled'
        event['colorId'] = '11'  # Red color for cancelled events
        
        # Add cancellation note to description
        cancellation_note = f"\n\n🚫 CANCELLED\nReason: {booking.cancellation_reason or 'Not specified'}"
        event['description'] = event.get('description', '') + cancellation_note
        
        # Update the event
        service.events().update(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event_id,
            body=event,
        ).execute()
        
        print(f"Google Calendar: ✅ Event {event_id} marked as CANCELLED for booking {booking.reference_code}")
        logger.info(f"Google Calendar: marked event {event_id} as cancelled for booking {booking.reference_code}")
        return True
    except Exception as e:
        logger.error(f"Google Calendar: failed to cancel event {event_id} — {e}")
        print(f"Google Calendar: ⚠️ failed to cancel event {event_id} — {e}")
        return False


def delete_calendar_event(event_id):
    """Delete a Google Calendar event when a booking is permanently deleted."""
    if not settings.GOOGLE_CALENDAR_ID or not event_id:
        print(f"Google Calendar: ⚠️ Cannot delete event - missing calendar ID or event ID")
        return False

    service = _get_service()
    if not service:
        print(f"Google Calendar: ⚠️ Cannot delete event - service not available")
        return False

    try:
        print(f"Google Calendar: 🗑️ Deleting event {event_id} from calendar...")
        
        service.events().delete(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event_id,
        ).execute()
        
        print(f"Google Calendar: ✅ Successfully deleted event {event_id}")
        logger.info(f"Google Calendar: deleted event {event_id}")
        return True
    except Exception as e:
        logger.error(f"Google Calendar: failed to delete event {event_id} — {e}")
        print(f"Google Calendar: ❌ Failed to delete event {event_id} — {e}")
        import traceback
        traceback.print_exc()
        return False
