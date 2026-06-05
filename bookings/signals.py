from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Booking, Notification
from .views import send_booking_confirmation_email
from .google_calendar import create_calendar_event, update_calendar_event, delete_calendar_event, cancel_calendar_event

# Store the old status before save
@receiver(pre_save, sender=Booking)
def store_old_status(sender, instance, **kwargs):
    """Store the old status before saving to detect changes."""
    if instance.pk:
        try:
            old_instance = Booking.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_event_id = old_instance.google_calendar_event_id
        except Booking.DoesNotExist:
            instance._old_status = None
            instance._old_event_id = None
    else:
        instance._old_status = None
        instance._old_event_id = None


@receiver(post_save, sender=Booking)
def booking_status_changed(sender, instance, created, **kwargs):
    """
    Handle booking status changes: email + Google Calendar sync.
    - New booking (created=True): CREATE calendar event immediately
    - Status changed to 'paid': send email + update event
    - Status changed to 'cancelled': mark event as cancelled in calendar
    - other updates: update event if exists
    """

    # CREATE EVENT IMMEDIATELY for new bookings
    if created:
        print(f"Booking created: {instance.reference_code} - creating calendar event immediately")
        # Capture values in local variables
        booking_pk = instance.pk
        transaction.on_commit(lambda: _create_event_for_new_booking(booking_pk))
        transaction.on_commit(lambda: _create_booking_notification(booking_pk))
        return

    # Check if status actually changed
    old_status = getattr(instance, '_old_status', None)
    
    print(f"DEBUG: Booking {instance.reference_code} - old_status: {old_status}, new_status: {instance.status}")
    
    # Only process if status actually changed
    if old_status is not None and old_status != instance.status:
        print(f"DEBUG: Status changed from {old_status} to {instance.status}, scheduling calendar update")
        # Capture values in local variables to avoid lambda closure issues
        booking_pk = instance.pk
        old_status_val = old_status
        new_status_val = instance.status
        transaction.on_commit(lambda: _handle_status_change(booking_pk, old_status_val, new_status_val))
    else:
        print(f"DEBUG: No status change detected or old_status is None")


def _create_event_for_new_booking(booking_pk):
    """Create calendar event for a new booking (called after transaction commit)."""
    print(f"DEBUG: _create_event_for_new_booking called for booking_pk: {booking_pk}")
    
    try:
        booking = Booking.objects.get(pk=booking_pk)
        print(f"DEBUG: Creating event for new booking {booking.reference_code}")
        
        event_id = create_calendar_event(booking)
        if event_id:
            # Use update() to avoid triggering signal again
            Booking.objects.filter(pk=booking_pk).update(google_calendar_event_id=event_id)
            print(f"Google Calendar: ✅ created event {event_id} for new booking {booking.reference_code}")
        else:
            print(f"Google Calendar: ❌ Failed to create event for {booking.reference_code}")
    except Booking.DoesNotExist:
        print(f"Google Calendar: ⚠️ Booking {booking_pk} not found")
    except Exception as e:
        print(f"Google Calendar: ❌ Error in _create_event_for_new_booking: {e}")
        import traceback
        traceback.print_exc()



def _handle_status_change(booking_pk, old_status, new_status):
    """Handle status change for a booking (called after transaction commit)."""
    print(f"DEBUG: _handle_status_change called - booking_pk: {booking_pk}, old: {old_status}, new: {new_status}")

    try:
        booking = Booking.objects.select_related('package').get(pk=booking_pk)
        event_id = booking.google_calendar_event_id

        print(f"DEBUG: Booking found - {booking.reference_code}, event_id: {event_id}, status: {booking.status}")

        if new_status == 'paid':
            print(f"DEBUG: Status is 'paid', processing...")
            # Send email
            send_booking_confirmation_email(booking)

            # Create in-app notification for status change
            Notification.objects.create(
                notification_type='new_booking',
                title=f"Booking Paid – {booking.reference_code}",
                message=(
                    f"{booking.customer_name}'s booking for {booking.package.name} "
                    f"on {booking.date.strftime('%B %d, %Y')} has been marked as paid. "
                    f"Total: ₱{booking.total_price:,.2f}."
                ),
                reference_code=booking.reference_code,
            )

            if event_id:
                print(f"DEBUG: Event exists, updating...")
                update_calendar_event(booking, event_id)
                print(f"Google Calendar: ✅ updated event {event_id} for booking {booking.reference_code}")
            else:
                print(f"DEBUG: No event_id, creating new calendar event...")
                event_id = create_calendar_event(booking)
                if event_id:
                    Booking.objects.filter(pk=booking_pk).update(google_calendar_event_id=event_id)
                    print(f"Google Calendar: ✅ created event {event_id} for confirmed booking {booking.reference_code}")
                else:
                    print(f"Google Calendar: ❌ Failed to create event for {booking.reference_code}")

        elif new_status == 'cancelled':
            # Create in-app notification for cancellation
            Notification.objects.create(
                notification_type='new_booking',
                title=f"Booking Cancelled – {booking.reference_code}",
                message=(
                    f"{booking.customer_name}'s booking for {booking.package.name} "
                    f"on {booking.date.strftime('%B %d, %Y')} has been cancelled."
                ),
                reference_code=booking.reference_code,
            )

            if event_id:
                cancel_calendar_event(booking, event_id)
                print(f"Google Calendar: ✅ marked event {event_id} as cancelled")

        elif event_id:
            update_calendar_event(booking, event_id)
            print(f"Google Calendar: 🔄 updated event {event_id} on status change")

    except Booking.DoesNotExist:
        print(f"Google Calendar: ⚠️ Booking {booking_pk} not found")
    except Exception as e:
        print(f"Google Calendar: ❌ Error in _handle_status_change: {e}")
        import traceback
        traceback.print_exc()


def _create_booking_notification(booking_pk):
    """Create an in-app notification for admin/staff when a new booking is placed."""
    try:
        booking = Booking.objects.select_related('package').get(pk=booking_pk)
        date_str = booking.date.strftime('%B %d, %Y')
        time_str = booking.time.strftime('%I:%M %p').lstrip('0')
        Notification.objects.create(
            notification_type='new_booking',
            title=f"New Booking – {booking.reference_code}",
            message=(
                f"{booking.customer_name} booked {booking.package.name} "
                f"on {date_str} at {time_str}. "
                f"Total: ₱{booking.total_price:,.2f}."
            ),
            reference_code=booking.reference_code,
        )
        print(f"Notification created for booking {booking.reference_code}")
    except Exception as e:
        print(f"Failed to create notification for booking {booking_pk}: {e}")


@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    """
    Automatically delete Google Calendar event when booking is deleted from admin.
    This ensures calendar stays in sync when bookings are permanently removed.
    """
    event_id = instance.google_calendar_event_id
    
    print(f"🗑️ DEBUG: post_delete signal fired for booking {instance.reference_code}")
    print(f"🗑️ DEBUG: event_id = {event_id}")
    
    if event_id:
        print(f"🗑️ DEBUG: Calling delete_calendar_event({event_id})")
        success = delete_calendar_event(event_id)
        if success:
            print(f"Google Calendar: ✅ deleted event {event_id} for booking {instance.reference_code} (booking deleted)")
        else:
            print(f"Google Calendar: ⚠️ failed to delete event {event_id} for booking {instance.reference_code}")
    else:
        print(f"🗑️ DEBUG: No event_id found for booking {instance.reference_code}, skipping calendar deletion")
