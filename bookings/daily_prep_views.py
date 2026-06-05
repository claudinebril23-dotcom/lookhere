"""
Daily Studio Preparation Views - Django Integration
====================================================
This module provides Python wrappers for PostgreSQL views that show
daily studio setup information without exposing sensitive customer data.

Key Features:
- View today's bookings for studio setup
- View tomorrow's bookings for advance preparation
- View weekly schedule for planning
- Security: No customer contact info or prices exposed
"""

from django.db import connection
from typing import List, Dict
from datetime import date


def get_today_studio_setup() -> List[Dict]:
    """
    Get today's studio setup list (what staff need to prepare).
    
    Returns list of sessions with:
    - booking_time: When the session starts
    - package_name: What package/equipment to prepare
    - session_duration: How long the session lasts
    - backdrop_name: What backdrop to set up
    - backdrop_color: Color code for visual reference
    - session_ref: Reference code to identify the session
    - booking_status: confirmed or paid
    
    Security: NO customer contact info, NO prices
    
    Example:
        >>> sessions = get_today_studio_setup()
        >>> for session in sessions:
        >>>     print(f"{session['booking_time']} - {session['package_name']}")
        >>>     print(f"  Backdrop: {session['backdrop_name']} ({session['backdrop_color']})")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_today_studio_setup")
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def get_tomorrow_studio_setup() -> List[Dict]:
    """
    Get tomorrow's studio setup list for advance preparation.
    
    Same structure as get_today_studio_setup() but for next day.
    
    Example:
        >>> sessions = get_tomorrow_studio_setup()
        >>> print(f"Tomorrow: {len(sessions)} sessions to prepare")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_tomorrow_studio_setup")
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def get_weekly_studio_schedule() -> List[Dict]:
    """
    Get this week's studio schedule for planning.
    
    Returns sessions for the entire week (Monday to Sunday).
    
    Example:
        >>> schedule = get_weekly_studio_schedule()
        >>> for session in schedule:
        >>>     print(f"{session['booking_date']} {session['booking_time']} - {session['package_name']}")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_weekly_studio_schedule")
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def get_studio_setup_summary() -> List[Dict]:
    """
    Get today's setup summary (grouped by package and backdrop).
    
    Returns:
    - booking_date: Date
    - package_name: Package type
    - backdrop_name: Backdrop needed
    - session_count: How many sessions
    - time_slots: Comma-separated list of times
    
    Useful for knowing how many times to set up each backdrop.
    
    Example:
        >>> summary = get_studio_setup_summary()
        >>> for item in summary:
        >>>     print(f"{item['package_name']} with {item['backdrop_name']}")
        >>>     print(f"  {item['session_count']} sessions at {item['time_slots']}")
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_studio_setup_summary")
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def get_backdrops_needed_today() -> List[Dict]:
    """
    Get list of unique backdrops needed today.
    
    Returns:
    - backdrop_name: Name of backdrop
    - backdrop_color: Color code
    - session_count: How many times it's used
    
    Example:
        >>> backdrops = get_backdrops_needed_today()
        >>> print("Backdrops to prepare:")
        >>> for bd in backdrops:
        >>>     print(f"  • {bd['backdrop_name']} ({bd['backdrop_color']}) - {bd['session_count']}x")
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                backdrop_name,
                backdrop_color,
                COUNT(*) as session_count
            FROM v_today_studio_setup
            WHERE backdrop_name IS NOT NULL
            GROUP BY backdrop_name, backdrop_color
            ORDER BY session_count DESC
        """)
        
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def get_packages_needed_today() -> List[Dict]:
    """
    Get list of packages needed today with counts.
    
    Returns:
    - package_name: Package type
    - session_count: How many sessions
    - total_duration: Total minutes needed
    
    Example:
        >>> packages = get_packages_needed_today()
        >>> for pkg in packages:
        >>>     print(f"{pkg['package_name']}: {pkg['session_count']} sessions")
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                package_name,
                COUNT(*) as session_count,
                SUM(session_duration) as total_duration
            FROM v_today_studio_setup
            GROUP BY package_name
            ORDER BY session_count DESC
        """)
        
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        
        return [
            dict(zip(columns, row))
            for row in results
        ]


def print_daily_prep_checklist():
    """
    Print a formatted daily preparation checklist for staff.
    
    This is a convenience function that displays all the information
    staff need in a readable format.
    
    Example:
        >>> print_daily_prep_checklist()
    """
    from datetime import date as date_class
    
    print("\n" + "="*70)
    print(f"STUDIO PREPARATION CHECKLIST - {date_class.today().strftime('%A, %B %d, %Y')}")
    print("="*70 + "\n")
    
    # Today's sessions
    sessions = get_today_studio_setup()
    
    if not sessions:
        print("✅ No sessions scheduled for today\n")
        return
    
    print(f"📅 TODAY'S SESSIONS: {len(sessions)}")
    print("-" * 70)
    
    for session in sessions:
        time = session['booking_time']
        package = session['package_name']
        duration = session['session_duration']
        backdrop = session['backdrop_name'] or 'No backdrop'
        color = session['backdrop_color'] or ''
        ref = session['session_ref']
        status = session['booking_status']
        
        status_icon = "✅" if status == 'paid' else "⏳"
        backdrop_info = f"{backdrop} ({color})" if color else backdrop
        
        print(f"\n{status_icon} {time} - {package} ({duration} min)")
        print(f"   Backdrop: {backdrop_info}")
        print(f"   Ref: {ref}")
    
    # Backdrops needed
    print("\n" + "-" * 70)
    print("🎨 BACKDROPS TO PREPARE:")
    print("-" * 70)
    
    backdrops = get_backdrops_needed_today()
    if backdrops:
        for bd in backdrops:
            print(f"  • {bd['backdrop_name']} ({bd['backdrop_color']}) - {bd['session_count']}x")
    else:
        print("  • No backdrops needed")
    
    # Packages summary
    print("\n" + "-" * 70)
    print("📦 EQUIPMENT TO PREPARE:")
    print("-" * 70)
    
    packages = get_packages_needed_today()
    for pkg in packages:
        print(f"  • {pkg['package_name']}: {pkg['session_count']} session(s)")
    
    print("\n" + "="*70 + "\n")


# ============================================================================
# SECURITY NOTES
# ============================================================================
"""
WHAT'S EXCLUDED (Sensitive Data):
- customer_name (privacy)
- email (privacy)
- phone (privacy)
- total_price (business data)
- payment_method (business data)
- payment_proof (business data)
- birthday (privacy)
- voucher_code (business data)

WHAT'S INCLUDED (Setup Information Only):
- booking_time (when to prepare)
- package_name (what equipment needed)
- session_duration (how long to allocate)
- backdrop_name (what backdrop to set up)
- backdrop_color (visual reference)
- session_ref (to identify the session)
- booking_status (confirmed vs paid)

This ensures staff can prepare the studio without accessing
sensitive customer or business information.
"""


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Example 1: Morning preparation routine
---------------------------------------
from bookings.daily_prep_views import print_daily_prep_checklist

# Print today's checklist
print_daily_prep_checklist()


Example 2: Get today's sessions programmatically
-------------------------------------------------
from bookings.daily_prep_views import get_today_studio_setup

sessions = get_today_studio_setup()

for session in sessions:
    print(f"Time: {session['booking_time']}")
    print(f"Package: {session['package_name']}")
    print(f"Backdrop: {session['backdrop_name']}")
    print()


Example 3: Check what backdrops are needed
-------------------------------------------
from bookings.daily_prep_views import get_backdrops_needed_today

backdrops = get_backdrops_needed_today()

print("Backdrops to set up:")
for bd in backdrops:
    print(f"  {bd['backdrop_name']} - needed {bd['session_count']} times")


Example 4: View tomorrow's schedule
------------------------------------
from bookings.daily_prep_views import get_tomorrow_studio_setup

tomorrow = get_tomorrow_studio_setup()
print(f"Tomorrow: {len(tomorrow)} sessions scheduled")


Example 5: Weekly planning
---------------------------
from bookings.daily_prep_views import get_weekly_studio_schedule

schedule = get_weekly_studio_schedule()

for session in schedule:
    print(f"{session['booking_date']} {session['booking_time']} - {session['package_name']}")


Example 6: Create a staff dashboard view
-----------------------------------------
from django.shortcuts import render
from bookings.daily_prep_views import get_today_studio_setup, get_backdrops_needed_today

def staff_dashboard(request):
    context = {
        'sessions': get_today_studio_setup(),
        'backdrops': get_backdrops_needed_today(),
    }
    return render(request, 'staff/dashboard.html', context)
"""
