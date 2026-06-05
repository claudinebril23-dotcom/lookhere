"""
Booking Procedures - Django Integration
========================================
This module provides Python wrappers for PostgreSQL stored procedures and triggers
that manage booking schedules without requiring immediate payment.

Key Features:
- Confirm bookings while enforcing daily limits
- Prevent double bookings automatically
- Check booking availability
- Get daily booking statistics
"""

from django.db import connection
from typing import Dict, List, Tuple, Optional
from datetime import date, time as time_type


def confirm_booking_slot(booking_id: int) -> Dict[str, any]:
    """
    Confirm a pending booking if daily limit is not exceeded.
    
    This function calls the PostgreSQL stored procedure `confirm_booking_slot`
    which implements "over-enrollment" logic similar to course registration systems.
    
    Args:
        booking_id (int): The ID of the booking to confirm
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'booking_ref': str or None
        }
    
    Example:
        >>> result = confirm_booking_slot(123)
        >>> if result['success']:
        >>>     print(f"Booking {result['booking_ref']} confirmed!")
        >>> else:
        >>>     print(f"Error: {result['message']}")
    
    Note:
        - Only 'pending' bookings can be confirmed
        - Checks against max_daily_bookings from site settings
        - Does NOT affect Google Calendar (calendar events created separately)
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM confirm_booking_slot(%s)", [booking_id])
        result = cursor.fetchone()
        
        if result:
            return {
                'success': result[0],
                'message': result[1],
                'booking_ref': result[2]
            }
        
        return {
            'success': False,
            'message': 'Unexpected error calling stored procedure',
            'booking_ref': None
        }


def get_daily_booking_status(booking_date: date) -> Dict[str, any]:
    """
    Get booking statistics for a specific date.
    
    Args:
        booking_date (date): The date to check
    
    Returns:
        dict: {
            'date': date,
            'confirmed_count': int,
            'pending_count': int,
            'max_bookings': int,
            'available_slots': int,
            'is_full': bool
        }
    
    Example:
        >>> from datetime import date
        >>> status = get_daily_booking_status(date(2026, 5, 20))
        >>> print(f"Available slots: {status['available_slots']}")
        >>> if status['is_full']:
        >>>     print("This date is fully booked!")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_daily_booking_status(%s)", [booking_date])
        result = cursor.fetchone()
        
        if result:
            return {
                'date': result[0],
                'confirmed_count': result[1],
                'pending_count': result[2],
                'max_bookings': result[3],
                'available_slots': result[4],
                'is_full': result[5]
            }
        
        return None


def get_available_time_slots(booking_date: date) -> List[Dict[str, any]]:
    """
    Get all time slots and their availability for a specific date.
    
    Args:
        booking_date (date): The date to check
    
    Returns:
        list: List of dicts with:
            {
                'time': time,
                'is_available': bool,
                'status': str,
                'customer_name': str or None
            }
    
    Example:
        >>> from datetime import date
        >>> slots = get_available_time_slots(date(2026, 5, 20))
        >>> for slot in slots:
        >>>     if slot['is_available']:
        >>>         print(f"{slot['time']} - Available")
        >>>     else:
        >>>         print(f"{slot['time']} - Booked by {slot['customer_name']}")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_available_time_slots(%s)", [booking_date])
        results = cursor.fetchall()
        
        return [
            {
                'time': row[0],
                'is_available': row[1],
                'status': row[2],
                'customer_name': row[3]
            }
            for row in results
        ]


def check_time_slot_available(booking_date: date, booking_time: time_type) -> bool:
    """
    Check if a specific time slot is available (not confirmed).
    
    Args:
        booking_date (date): The date to check
        booking_time (time): The time to check
    
    Returns:
        bool: True if available, False if already confirmed
    
    Example:
        >>> from datetime import date, time
        >>> if check_time_slot_available(date(2026, 5, 20), time(10, 0)):
        >>>     print("Time slot is available!")
        >>> else:
        >>>     print("Time slot is already booked")
    """
    from bookings.models import Booking
    
    return not Booking.objects.filter(
        date=booking_date,
        time=booking_time,
        status='confirmed'
    ).exists()


def get_booking_summary(start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, any]:
    """
    Get a summary of bookings for a date range.
    
    Args:
        start_date (date, optional): Start date (defaults to today)
        end_date (date, optional): End date (defaults to start_date)
    
    Returns:
        dict: Summary statistics
    
    Example:
        >>> from datetime import date, timedelta
        >>> today = date.today()
        >>> week_later = today + timedelta(days=7)
        >>> summary = get_booking_summary(today, week_later)
        >>> print(f"Total bookings: {summary['total_bookings']}")
    """
    from bookings.models import Booking
    from datetime import date as date_class
    
    if start_date is None:
        start_date = date_class.today()
    if end_date is None:
        end_date = start_date
    
    bookings = Booking.objects.filter(date__range=[start_date, end_date])
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'paid_bookings': bookings.filter(status='paid').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
    }


# ============================================================================
# TRIGGER INFORMATION
# ============================================================================
"""
AUTOMATIC DOUBLE BOOKING PREVENTION
====================================

A PostgreSQL trigger `trg_prevent_double_booking` automatically prevents
double bookings when:

1. Inserting a new booking with status='confirmed'
2. Updating an existing booking to status='confirmed'

The trigger checks if another CONFIRMED booking exists at the same date/time.
If found, it raises an exception and prevents the operation.

Example Error Message:
    DOUBLE_BOOKING_ERROR: Time slot 10:00:00 on 2026-05-20 is already confirmed
    (Booking: LOOKHERE-ABC123, Customer: John Doe). Please choose a different time slot.

This happens AUTOMATICALLY - no Python code needed!

IMPORTANT: This does NOT affect Google Calendar integration.
Calendar events are created separately when bookings are paid/confirmed.
"""

# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example 1: Confirm a pending booking
-------------------------------------
from bookings.booking_procedures import confirm_booking_slot
from bookings.models import Booking

# Get a pending booking
booking = Booking.objects.filter(status='pending').first()

# Try to confirm it
result = confirm_booking_slot(booking.id)

if result['success']:
    print(f"✅ {result['message']}")
    # Refresh from database to see updated status
    booking.refresh_from_db()
    print(f"New status: {booking.status}")
else:
    print(f"❌ {result['message']}")


Example 2: Check daily availability
------------------------------------
from bookings.booking_procedures import get_daily_booking_status
from datetime import date

status = get_daily_booking_status(date(2026, 5, 20))

print(f"Date: {status['date']}")
print(f"Confirmed: {status['confirmed_count']}/{status['max_bookings']}")
print(f"Available: {status['available_slots']} slots")

if status['is_full']:
    print("⚠️ This date is fully booked!")


Example 3: Show available time slots
-------------------------------------
from bookings.booking_procedures import get_available_time_slots
from datetime import date

slots = get_available_time_slots(date(2026, 5, 20))

print("Available time slots:")
for slot in slots:
    status_icon = "✅" if slot['is_available'] else "❌"
    print(f"{status_icon} {slot['time']} - {slot['status']}")


Example 4: Try to create double booking (will fail)
----------------------------------------------------
from bookings.models import Booking
from datetime import date, time

try:
    # This will fail if a confirmed booking exists at this time
    booking = Booking.objects.create(
        date=date(2026, 5, 20),
        time=time(10, 0),
        status='confirmed',  # Trigger fires when status is 'confirmed'
        customer_name='Test User',
        email='test@test.com',
        phone='1234567890',
        package_id=1,
        total_price=299.00,
        reference_code='TEST-123'
    )
    print("Booking created")
except Exception as e:
    if 'DOUBLE_BOOKING_ERROR' in str(e):
        print("❌ Double booking prevented by trigger!")
    else:
        print(f"Error: {e}")
"""
