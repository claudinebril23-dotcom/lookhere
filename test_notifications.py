"""
Test script to check notification system
Run with: python manage.py shell < test_notifications.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Notification, Booking

print("\n" + "="*60)
print("NOTIFICATION SYSTEM TEST")
print("="*60)

# Check if notifications exist
notifications = Notification.objects.all().order_by('-created_at')
print(f"\nTotal notifications in database: {notifications.count()}")

if notifications.exists():
    print("\nLast 5 notifications:")
    for notif in notifications[:5]:
        print(f"  - [{notif.id}] {notif.title}")
        print(f"    Message: {notif.message}")
        print(f"    Read: {notif.is_read}")
        print(f"    Created: {notif.created_at}")
        print()
else:
    print("\n⚠️  No notifications found in database!")
    print("Creating a test notification...")
    
    # Create a test notification
    test_notif = Notification.objects.create(
        notification_type='new_booking',
        title='Test Notification',
        message='This is a test notification to verify the system is working.',
        reference_code='TEST-001',
        is_read=False
    )
    print(f"✅ Test notification created with ID: {test_notif.id}")

# Check recent bookings
recent_bookings = Booking.objects.all().order_by('-created_at')[:3]
print(f"\nRecent bookings: {recent_bookings.count()}")
for booking in recent_bookings:
    print(f"  - {booking.reference_code}: {booking.customer_name} ({booking.status})")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
