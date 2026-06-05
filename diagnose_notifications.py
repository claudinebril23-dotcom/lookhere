"""
Diagnostic script to check notification system
Run with: python manage.py shell < diagnose_notifications.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import Notification, Booking, Package
from django.contrib.messages import get_messages
from django.test import RequestFactory

print("\n" + "="*60)
print("NOTIFICATION SYSTEM DIAGNOSTIC")
print("="*60)

# 1. Check if Notification model works
print("\n1. Testing Notification Model:")
try:
    test_notif = Notification.objects.create(
        notification_type='new_booking',
        title='Diagnostic Test',
        message='This is a diagnostic test notification',
        reference_code='DIAG-001',
        is_read=False
    )
    print(f"   ✅ Created test notification ID: {test_notif.id}")
    
    # Fetch it back
    fetched = Notification.objects.get(id=test_notif.id)
    print(f"   ✅ Successfully fetched notification: {fetched.title}")
    
    # Clean up
    test_notif.delete()
    print(f"   ✅ Cleaned up test notification")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check existing notifications
print("\n2. Existing Notifications:")
all_notifs = Notification.objects.all().order_by('-created_at')[:10]
print(f"   Total notifications in DB: {Notification.objects.count()}")
if all_notifs:
    print(f"   Last 10 notifications:")
    for n in all_notifs:
        status = "UNREAD" if not n.is_read else "read"
        print(f"   - [{n.id}] {n.title} ({status}) - {n.created_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print(f"   ⚠️  No notifications found")

# 3. Check recent bookings
print("\n3. Recent Bookings (should trigger notifications):")
recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
print(f"   Total bookings: {Booking.objects.count()}")
if recent_bookings:
    for b in recent_bookings:
        print(f"   - {b.reference_code}: {b.customer_name} ({b.status}) - {b.created_at.strftime('%Y-%m-%d %H:%M')}")
        # Check if notification exists for this booking
        notif_exists = Notification.objects.filter(reference_code=b.reference_code).exists()
        print(f"     Notification exists: {'✅ Yes' if notif_exists else '❌ No'}")
else:
    print(f"   No bookings found")

# 4. Check signals
print("\n4. Checking Signals:")
try:
    from bookings import signals
    print(f"   ✅ Signals module imported successfully")
    print(f"   Functions found:")
    print(f"   - store_old_status: {hasattr(signals, 'store_old_status')}")
    print(f"   - booking_status_changed: {hasattr(signals, 'booking_status_changed')}")
    print(f"   - _create_booking_notification: {hasattr(signals, '_create_booking_notification')}")
except Exception as e:
    print(f"   ❌ Error importing signals: {e}")

# 5. Test creating a notification manually
print("\n5. Creating Test Notification:")
try:
    notif = Notification.objects.create(
        notification_type='new_booking',
        title='🎨 Test Admin Action',
        message='Admin saved a backdrop successfully',
        reference_code='TEST-ADMIN',
        is_read=False
    )
    print(f"   ✅ Created notification ID: {notif.id}")
    print(f"   Title: {notif.title}")
    print(f"   Message: {notif.message}")
    print(f"   Is Read: {notif.is_read}")
    print(f"\n   👉 Now check the notification bell in admin panel!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Go to /admin/ and click the notification bell")
print("2. Check browser console (F12) for JavaScript errors")
print("3. Visit /notification-debug/ for interactive testing")
print("="*60 + "\n")
