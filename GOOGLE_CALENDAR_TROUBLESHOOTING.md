# Google Calendar Integration - Troubleshooting Guide

## 📋 Overview

Your photobooth booking system automatically syncs bookings to Google Calendar. This guide helps you verify and troubleshoot the integration.

---

## ✅ How It Works

### Automatic Sync Events:

1. **New Booking Created** → Calendar event created immediately
2. **Status Changed to 'Paid'** → Calendar event updated + confirmation email sent
3. **Status Changed to 'Cancelled'** → Calendar event marked as cancelled (red)
4. **Booking Deleted** → Calendar event deleted

---

## 🔍 Quick Check: Are Bookings Syncing?

### Method 1: Run Diagnostic Script

```bash
cd c:\Users\Dens\Desktop\Photoboothsystem\lookhere
python check_calendar_sync.py
```

This script will:
- ✅ Check if Google Calendar is configured correctly
- ✅ Show which bookings have calendar events
- ✅ List upcoming events from your calendar
- ✅ Test creating a calendar event

### Method 2: Check in Django Admin

1. Go to Django Admin → Bookings
2. Open any booking
3. Look for the field: **Google Calendar Event ID**
4. If it has a value (like `abc123xyz`), the booking is synced ✅
5. If it's empty, the booking is NOT synced ❌

### Method 3: Check Google Calendar Directly

1. Go to [Google Calendar](https://calendar.google.com)
2. Sign in with: `dyienziidens353@gmail.com`
3. Look for events with format: `📸 Customer Name — Package Name`
4. Events should show:
   - Customer name
   - Package details
   - Booking reference code
   - Date and time

---

## 🛠️ Common Issues & Solutions

### Issue 1: No Events Appearing in Calendar

**Possible Causes:**
- Google Calendar credentials not configured
- Calendar ID incorrect
- Service account doesn't have access to calendar

**Solution:**
```bash
# 1. Check if credentials file exists
dir google_credentials.json

# 2. Check .env file has correct Calendar ID
# Open .env and verify:
GOOGLE_CALENDAR_ID=dyienziidens353@gmail.com

# 3. Run diagnostic script
python check_calendar_sync.py
```

### Issue 2: Events Created But Not Visible

**Possible Cause:** Service account email not shared with calendar

**Solution:**
1. Open `google_credentials.json`
2. Find the `client_email` field (looks like: `something@project.iam.gserviceaccount.com`)
3. Go to Google Calendar settings
4. Share your calendar with that email address
5. Give it "Make changes to events" permission

### Issue 3: Old Bookings Don't Have Events

**This is normal!** Calendar events are only created for:
- New bookings (created after the feature was added)
- Bookings that change status to 'paid'

**Solution:** To sync old bookings:
```bash
python check_calendar_sync.py
# Choose "y" when asked to test creating an event
# Repeat for each booking you want to sync
```

### Issue 4: Events Not Updating When Status Changes

**Check Django logs:**
```bash
# Look for these messages in your console:
# ✅ "Google Calendar: created event..."
# ✅ "Google Calendar: updated event..."
# ❌ "Google Calendar: failed to..."
```

**Solution:**
1. Make sure signals are working (check `bookings/signals.py`)
2. Verify the booking has a `google_calendar_event_id`
3. Check that the service account has write access to the calendar

---

## 📊 Current Configuration

Based on your `.env` file:

```
GOOGLE_CALENDAR_CREDENTIALS=google_credentials.json
GOOGLE_CALENDAR_ID=dyienziidens353@gmail.com
```

**Status:** ✅ Configured

---

## 🔧 Manual Sync (If Needed)

If you need to manually create a calendar event for a booking:

```python
# Open Django shell
python manage.py shell

# Import required modules
from bookings.models import Booking
from bookings.google_calendar import create_calendar_event

# Get the booking (replace with actual reference code)
booking = Booking.objects.get(reference_code='LOOKHERE-ABC12')

# Create calendar event
event_id = create_calendar_event(booking)

# Save event ID to booking
if event_id:
    booking.google_calendar_event_id = event_id
    booking.save(update_fields=['google_calendar_event_id'])
    print(f"✅ Event created: {event_id}")
else:
    print("❌ Failed to create event")
```

---

## 📝 Event Details in Calendar

Each calendar event includes:

```
Title: 📸 Customer Name — Package Name

Description:
📋 Reference: LOOKHERE-ABC12
👤 Customer: John Doe
📧 Email: john@example.com
📱 Phone: 09123456789
📦 Package: Solo Snap
🎨 Backdrop: White
✨ Add-ons: Extra Prints, Softcopy
💰 Total: ₱299.00
```

**Event Duration:** 1 hour (automatically calculated)

**Event Color:**
- 🔵 Blue = Confirmed/Paid booking
- 🔴 Red = Cancelled booking

---

## 🧪 Testing the Integration

### Test 1: Create a New Booking

1. Go to your website and create a test booking
2. Check Django console for: `✅ Google Calendar: created event...`
3. Check Google Calendar for the new event
4. Check Django Admin → Booking → Google Calendar Event ID field

### Test 2: Change Booking Status

1. Open a booking in Django Admin
2. Change status from 'pending' to 'paid'
3. Save
4. Check console for: `✅ Google Calendar: updated event...`
5. Check that customer received confirmation email
6. Check Google Calendar for updated event

### Test 3: Cancel a Booking

1. Open a booking in Django Admin
2. Change status to 'cancelled'
3. Add a cancellation reason
4. Save
5. Check console for: `✅ Google Calendar: marked event as cancelled`
6. Check Google Calendar - event should be red/crossed out

---

## 📞 Support

If you're still having issues:

1. Run the diagnostic script: `python check_calendar_sync.py`
2. Check Django console logs for error messages
3. Verify Google Calendar credentials are correct
4. Make sure service account has calendar access

---

## 🎯 Quick Checklist

- [ ] `google_credentials.json` file exists
- [ ] `.env` has `GOOGLE_CALENDAR_ID` set
- [ ] Service account email has access to calendar
- [ ] Google API packages installed
- [ ] New bookings create calendar events
- [ ] Status changes update calendar events
- [ ] Cancelled bookings show as cancelled in calendar
- [ ] Deleted bookings remove calendar events

---

**Last Updated:** 2025-05-24
**System:** Look Here Self Portrait Studio - Photobooth Booking System
