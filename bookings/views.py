from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncWeek, TruncMonth, TruncDate
from .models import Package, Addon, Backdrop, Booking, SiteSettings, GalleryPhoto, Notification
import uuid
from datetime import datetime, time, timedelta

try:
    import boto3  # type: ignore
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

def home(request):
    # Optimized: Only fetch necessary fields for packages
    packages = Package.objects.only('id', 'name', 'base_price', 'description', 'image').order_by('base_price')
    site_settings = SiteSettings.get_settings()
    # Fetch active gallery photos for homepage — up to 18 for the carousel
    gallery_photos = GalleryPhoto.objects.filter(is_active=True).order_by('order', '-created_at')[:18]
    # Most recently uploaded active photo for the "featured" spotlight
    featured_photo = GalleryPhoto.objects.filter(is_active=True).order_by('-created_at').first()
    return render(request, 'bookings/home.html', {
        'packages': packages,
        'site_settings': site_settings,
        'gallery_photos': gallery_photos,
        'featured_photo': featured_photo,
    })

def packages_view(request):
    # Optimized: Only fetch necessary fields
    packages = Package.objects.only('id', 'name', 'base_price', 'description', 'image', 'duration', 'processing_time').order_by('base_price')

    # Check booking limits so the packages page can reflect availability
    site_settings = SiteSettings.get_settings()
    bookings_enabled = site_settings.enable_bookings

    # Check if today has already hit the daily limit
    today_full = False
    if bookings_enabled and site_settings.max_daily_bookings > 0:
        from datetime import date as date_class
        today_count = Booking.objects.filter(
            date=date_class.today(),
            status__in=['confirmed', 'paid']
        ).count()
        today_full = today_count >= site_settings.max_daily_bookings

    return render(request, 'bookings/packages.html', {
        'packages': packages,
        'bookings_enabled': bookings_enabled,
        'today_full': today_full,
    })

def gallery(request):
    photos = GalleryPhoto.objects.filter(is_active=True).order_by('order', '-created_at')
    return render(request, 'bookings/gallery.html', {'photos': photos})

def about(request):
    site_settings = SiteSettings.get_settings()
    return render(request, 'bookings/about.html', {'site_settings': site_settings})

def convert_to_24h(time_str):
    """Convert 12-hour format (e.g., '12:20 PM') to 24-hour format (e.g., '12:20')"""
    try:
        parts = time_str.strip().split()
        if len(parts) != 2:
            return time_str
        
        time_part, period = parts[0], parts[1].upper()
        hour, minute = map(int, time_part.split(':'))
        
        if period == 'PM' and hour != 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    except (ValueError, IndexError):
        return time_str

def parse_time_to_object(time_str):
    """Parse 24-hour format time string to time object without using strptime"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except (ValueError, IndexError):
        return None

def send_booking_confirmation_email(booking):
    """Send booking confirmation email."""
    addons_list = ', '.join([addon.name for addon in booking.addons.all()]) if booking.addons.exists() else 'None'
    
    date_str = booking.date.strftime('%B %d, %Y') if hasattr(booking.date, 'strftime') else str(booking.date)
    time_str = booking.time.strftime('%I:%M %p') if hasattr(booking.time, 'strftime') else str(booking.time)
    
    # Determine subject and status message based on booking status and payment method
    if booking.status == 'paid':
        if booking.payment_method == 'cash':
            subject = f"Booking Confirmed - {booking.reference_code} (Cash Payment)"
            status_message = "✅ Your booking is confirmed. Please bring the exact amount when you arrive at the studio."
        else:
            subject = f"Booking Confirmed - {booking.reference_code} (Payment Verified)"
            status_message = "✅ Your booking is confirmed and your GCash payment has been verified."
        status_class = "status-confirmed"
    else:
        # Pending or under review
        subject = f"Booking Received - {booking.reference_code}"
        if booking.payment_method == 'cash':
            status_message = "📋 Your booking has been received. Please bring the exact amount when you arrive at the studio."
        else:
            status_message = "📋 Your booking has been received. We look forward to seeing you at the studio."
        status_class = "status-under-review"
    
    context = {
        'customer_name': booking.customer_name,
        'reference_code': booking.reference_code,
        'date': date_str,
        'time': time_str,
        'package': booking.package.name,
        'backdrop': booking.backdrop.name if booking.backdrop else 'Not selected',
        'addons': addons_list,
        'total_price': f"{booking.total_price:,.2f}",
        'payment_method': booking.get_payment_method_display(),
        'status_message': status_message,
        'status_class': status_class,
    }
    
    try:
        print(f"\n=== SENDING CONFIRMATION EMAIL ===")
        print(f"To: {booking.email}")
        print(f"From: {django_settings.DEFAULT_FROM_EMAIL}")
        print(f"Subject: {subject}")
        print(f"Email Host: {django_settings.EMAIL_HOST}")
        print(f"Email Port: {django_settings.EMAIL_PORT}")
        print(f"Email Use TLS: {django_settings.EMAIL_USE_TLS}")
        print(f"Email Host User: {django_settings.EMAIL_HOST_USER}")
        
        html_message = render_to_string('bookings/email_confirmation.html', context)
        email = EmailMultiAlternatives(
            subject,
            f"Booking confirmation for {booking.reference_code}",
            django_settings.DEFAULT_FROM_EMAIL,
            [booking.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Confirmation email sent successfully to {booking.email}")
        print(f"=== EMAIL SENT ===")
        return True
    except Exception as e:
        print(f"\n❌ CONFIRMATION EMAIL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"=== EMAIL FAILED ===")
        return False

def send_receipt_to_studio(booking):
    """Send booking notification to studio"""
    # Always use "Booking Received" regardless of payment method
    subject = f"Booking Received - Booking {booking.reference_code}"
    
    date_str = booking.date.strftime('%B %d, %Y') if hasattr(booking.date, 'strftime') else str(booking.date)
    time_str = booking.time.strftime('%I:%M %p') if hasattr(booking.time, 'strftime') else str(booking.time)
    
    # No payment method information in the email
    message = f"""
    New Booking Received!
    
    BOOKING DETAILS:
    Reference Code: {booking.reference_code}
    Customer Name: {booking.customer_name}
    Email: {booking.email}
    Phone: {booking.phone}
    
    SESSION DETAILS:
    Date: {date_str}
    Time: {time_str}
    Package: {booking.package.name}
    Total Amount: ₱{booking.total_price:,.2f}
    """
    
    try:
        print(f"\n=== SENDING STUDIO NOTIFICATION ===")
        print(f"To: {django_settings.DEFAULT_FROM_EMAIL}")
        print(f"From: {django_settings.DEFAULT_FROM_EMAIL}")
        print(f"Subject: {subject}")
        
        send_mail(
            subject,
            message,
            django_settings.DEFAULT_FROM_EMAIL,
            [django_settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        print(f"Studio notification sent successfully")
        print(f"=== NOTIFICATION SENT ===")
        return True
    except Exception as e:
        print(f"\nSTUDIO NOTIFICATION ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"=== NOTIFICATION FAILED ===")
        return False

def send_booking_sms(booking):
    """Send booking confirmation SMS via AWS SNS"""
    if not HAS_BOTO3:
        print("boto3 not installed - SMS notifications disabled")
        return False
    
    try:
        sns_client = boto3.client(
            'sns',
            region_name=django_settings.AWS_REGION,
            aws_access_key_id=django_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=django_settings.AWS_SECRET_ACCESS_KEY,
        )
        
        date_str = booking.date.strftime('%m/%d/%Y') if hasattr(booking.date, 'strftime') else str(booking.date)
        time_str = booking.time.strftime('%I:%M %p') if hasattr(booking.time, 'strftime') else str(booking.time)
        
        message = f"""Narrative Studios PH - Booking Confirmed!

Ref Code: {booking.reference_code}
Date: {date_str}
Time: {time_str}
Total: ₱{booking.total_price:,.2f}

Thank you!"""
        
        phone = booking.phone
        if not phone.startswith('+'):
            phone = '+63' + phone.lstrip('0')
        
        sns_client.publish(
            PhoneNumber=phone,
            Message=message,
        )
        return True
    except Exception as e:
        print(f"SMS error: {e}")
        return False

def get_booked_times(date, package_id):
    """Get list of booked times for a specific date and package - Optimized"""
    try:
        # Optimized: Only fetch time field, use values_list for better performance
        bookings = Booking.objects.filter(
            date=date,
            package_id=package_id,
            status__in=['confirmed', 'paid']
        ).values_list('time', flat=True)
        
        booked_times = [time_obj.strftime('%I:%M %p') for time_obj in bookings if time_obj]
        return booked_times
    except Exception as e:
        print(f"Error getting booked times: {e}")
        return []

def book(request):
    if request.method == 'POST':
        package_id = request.POST.get('package')
        if not package_id:
            # Optimized: Only fetch necessary fields
            return render(request, 'bookings/book.html', {
                'packages': Package.objects.only('id', 'name', 'base_price', 'image').order_by('base_price'),
                'addons': Addon.objects.only('id', 'name', 'price', 'description').all(),
                'backdrops': Backdrop.objects.only('id', 'name', 'color', 'image').all(),
                'error': 'Please select a package before booking.'
            })

        site_settings = SiteSettings.get_settings()

        # ── Booking system enabled check ──────────────────────────────────
        if not site_settings.enable_bookings:
            return render(request, 'bookings/book.html', {
                'packages': Package.objects.only('id', 'name', 'base_price', 'image').order_by('base_price'),
                'addons': Addon.objects.only('id', 'name', 'price', 'description').all(),
                'backdrops': Backdrop.objects.only('id', 'name', 'color', 'image').all(),
                'selected_package_id': package_id,
                'error': 'Online booking is currently unavailable. Please contact us directly.'
            })

        # Check if time slot is already booked (across ALL packages)
        date_obj = datetime.fromisoformat(request.POST['date']).date()
        time_24h = convert_to_24h(request.POST['time'])
        time_obj = parse_time_to_object(time_24h)
        package = Package.objects.get(id=package_id)

        # ── Advance booking days check ────────────────────────────────────
        if site_settings.booking_advance_days > 0:
            from datetime import date as date_class
            max_date = date_class.today() + timedelta(days=site_settings.booking_advance_days)
            if date_obj > max_date:
                return render(request, 'bookings/book.html', {
                    'packages': Package.objects.only('id', 'name', 'base_price', 'image').order_by('base_price'),
                    'addons': Addon.objects.only('id', 'name', 'price', 'description').all(),
                    'backdrops': Backdrop.objects.only('id', 'name', 'color', 'image').all(),
                    'selected_package_id': package_id,
                    'error': f'Bookings can only be made up to {site_settings.booking_advance_days} days in advance.'
                })

        # ── Daily booking limit check ─────────────────────────────────────
        if site_settings.max_daily_bookings > 0:
            daily_count = Booking.objects.filter(
                date=date_obj,
                status__in=['confirmed', 'paid']
            ).count()
            if daily_count >= site_settings.max_daily_bookings:
                return render(request, 'bookings/book.html', {
                    'packages': Package.objects.only('id', 'name', 'base_price', 'image').order_by('base_price'),
                    'addons': Addon.objects.only('id', 'name', 'price', 'description').all(),
                    'backdrops': Backdrop.objects.only('id', 'name', 'color', 'image').all(),
                    'selected_package_id': package_id,
                    'error': 'This date is fully booked. Please choose a different date.'
                })

        # Optimized: Use exists() instead of fetching all records
        time_booked = Booking.objects.filter(
            date=date_obj,
            time=time_obj,
            status__in=['confirmed', 'paid']
        ).exists()

        if time_booked:
            return render(request, 'bookings/book.html', {
                'packages': Package.objects.only('id', 'name', 'base_price', 'image').order_by('base_price'),
                'addons': Addon.objects.only('id', 'name', 'price', 'description').all(),
                'backdrops': Backdrop.objects.only('id', 'name', 'color', 'image').all(),
                'selected_package_id': package_id,
                'error': 'This time slot is already booked. Please choose another time.'
            })
        
        ref_code = f"LOOKHERE-{uuid.uuid4().hex[:5].upper()}"
        total = package.base_price
        addons = []
        if 'addons' in request.POST:
            addon_ids = request.POST.getlist('addons')
            addons = Addon.objects.filter(id__in=addon_ids)
            total += sum(addon.price for addon in addons)
        pets = int(request.POST.get('pets', 0))
        total += pets * 100
        backdrop = None
        if request.POST.get('backdrop'):
            backdrop = Backdrop.objects.get(id=request.POST['backdrop'])
        
        
        booking = Booking.objects.create(
            reference_code=ref_code,
            date=date_obj,
            time=time_obj,
            customer_name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            birthday=request.POST.get('birthday') or None,
            voucher_code=request.POST.get('promo', ''),
            package=package,
            backdrop=backdrop,
            pet_count=pets,
            total_price=total,
            payment_method=request.POST.get('payment', 'gcash'),
        )
        booking.addons.set(addons)

        # Note: Calendar event will be created automatically by post_save signal

        return redirect('booking_detail', ref_code=ref_code)

    
    package_id = request.GET.get('package')
    # Optimized: Only fetch necessary fields
    packages = Package.objects.only('id', 'name', 'base_price', 'image', 'description').order_by('base_price')
    addons = Addon.objects.only('id', 'name', 'price', 'description').all()
    backdrops = Backdrop.objects.only('id', 'name', 'color', 'image').all()
    booked_times = []
    
    # Get selected package object if package_id is provided
    selected_package = None
    if package_id:
        try:
            selected_package = Package.objects.only('id', 'name', 'base_price').get(id=package_id)
        except Package.DoesNotExist:
            pass
    
    return render(request, 'bookings/book.html', {
        'packages': packages,
        'addons': addons,
        'backdrops': backdrops,
        'selected_package_id': package_id,
        'selected_package': selected_package,
        'booked_times': booked_times,
    })

def payment_upload(request, ref_code):
    """Payment upload is no longer used — redirect to booking detail."""
    return redirect('booking_detail', ref_code=ref_code)

def book_ajax(request):
    """
    AJAX version of the book view.
    Returns JSON with booking details on success, or error message on failure.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    package_id = request.POST.get('package')
    if not package_id:
        return JsonResponse({'error': 'Please select a package before booking.'}, status=400)

    try:
        date_obj = datetime.fromisoformat(request.POST['date']).date()
        time_24h = convert_to_24h(request.POST['time'])
        time_obj = parse_time_to_object(time_24h)
        package = Package.objects.get(id=package_id)

        site_settings = SiteSettings.get_settings()

        # ── Booking system enabled check ──────────────────────────────────
        if not site_settings.enable_bookings:
            return JsonResponse({'error': 'Online booking is currently unavailable. Please contact us directly.'}, status=400)

        # ── Advance booking days check ────────────────────────────────────
        if site_settings.booking_advance_days > 0:
            from datetime import date as date_class
            max_date = date_class.today() + timedelta(days=site_settings.booking_advance_days)
            if date_obj > max_date:
                return JsonResponse({'error': f'Bookings can only be made up to {site_settings.booking_advance_days} days in advance.'}, status=400)

        # ── Daily booking limit check ─────────────────────────────────────
        if site_settings.max_daily_bookings > 0:
            daily_count = Booking.objects.filter(
                date=date_obj,
                status__in=['confirmed', 'paid']
            ).count()
            if daily_count >= site_settings.max_daily_bookings:
                return JsonResponse({'error': 'This date is fully booked. Please choose a different date.'}, status=400)

        # Check time slot
        if Booking.objects.filter(date=date_obj, time=time_obj, status__in=['confirmed', 'paid']).exists():
            return JsonResponse({'error': 'This time slot is already booked. Please choose another time.'}, status=400)

        ref_code = f"LOOKHERE-{uuid.uuid4().hex[:5].upper()}"
        total = package.base_price
        addons = []
        if 'addons' in request.POST:
            addon_ids = request.POST.getlist('addons')
            addons = Addon.objects.filter(id__in=addon_ids)
            total += sum(addon.price for addon in addons)

        backdrop = None
        if request.POST.get('backdrop'):
            backdrop = Backdrop.objects.get(id=request.POST['backdrop'])

        booking = Booking.objects.create(
            reference_code=ref_code,
            date=date_obj,
            time=time_obj,
            customer_name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            birthday=request.POST.get('birthday') or None,
            voucher_code=request.POST.get('promo', ''),
            package=package,
            backdrop=backdrop,
            pet_count=int(request.POST.get('pets', 0)),
            total_price=total,
            payment_method=request.POST.get('payment', 'gcash'),
            status='confirmed',
        )
        booking.addons.set(addons)

        # Note: Confirmation email will be sent automatically when admin marks booking as paid
        # Calendar event will be created automatically by post_save signal

        # Send notification to studio
        try:
            send_receipt_to_studio(booking)
            print(f"✅ Studio notification sent")
        except Exception as studio_error:
            print(f"⚠️ Failed to send studio notification: {studio_error}")

        # Build response data
        addons_list = ', '.join([a.name for a in booking.addons.all()]) or 'None'
        return JsonResponse({
            'success': True,
            'reference_code': booking.reference_code,
            'date': booking.date.strftime('%B %d, %Y'),
            'time': booking.time.strftime('%I:%M %p').lstrip('0'),
            'package': booking.package.name,
            'backdrop': booking.backdrop.name if booking.backdrop else 'Not Selected',
            'addons': addons_list,
            'total': f"₱{booking.total_price:,.2f}",
            'name': booking.customer_name,
            'email': booking.email,
            'phone': booking.phone,
            'redirect_url': f'/booking/{ref_code}/',
        })

    except Exception as e:
        print(f"book_ajax error: {e}")
        import traceback; traceback.print_exc()
        return JsonResponse({'error': 'Something went wrong. Please try again.'}, status=500)

def booking_detail(request, ref_code):
    # Optimized: Use select_related to fetch package, backdrop in one query
    booking = get_object_or_404(
        Booking.objects.select_related('package', 'backdrop').prefetch_related('addons'),
        reference_code=ref_code
    )
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

def receipt_view(request, ref_code):
    """Display receipt for a booking - Optimized"""
    # Optimized: Use select_related and prefetch_related to reduce queries
    booking = get_object_or_404(
        Booking.objects.select_related('package', 'backdrop').prefetch_related('addons'),
        reference_code=ref_code
    )
    return render(request, 'bookings/receipt.html', {'booking': booking})

def booked_times_api(request):
    """
    API endpoint to get booked times for a specific date - Optimized.
    Merges two sources:
      1. Django bookings (pending/paid)
      2. Google Calendar events (any event on that date blocks the slot)
    """
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'booked_times': []})

    try:
        date_obj = datetime.fromisoformat(date_str).date()

        # ── Source 1: Django bookings (Optimized) ──────────────────────────
        # Only fetch time field for better performance
        bookings = Booking.objects.filter(
            date=date_obj,
            status__in=['confirmed', 'paid']
        ).values_list('time', flat=True)
        
        booked_times = []
        for t in bookings:
            hour = t.hour
            minute = t.minute
            period = 'AM' if hour < 12 else 'PM'
            display_hour = hour % 12 or 12
            booked_times.append(f"{display_hour}:{minute:02d} {period}")

        # ── Source 2: Google Calendar events ──────────────────────────────
        try:
            from .google_calendar import _get_service
            from django.conf import settings as dj_settings

            service = _get_service()
            if service and dj_settings.GOOGLE_CALENDAR_ID:
                # Fetch all events on this date in Manila time
                day_start = f"{date_str}T00:00:00+08:00"
                day_end   = f"{date_str}T23:59:59+08:00"

                result = service.events().list(
                    calendarId=dj_settings.GOOGLE_CALENDAR_ID,
                    timeMin=day_start,
                    timeMax=day_end,
                    singleEvents=True,
                    orderBy='startTime',
                ).execute()

                all_slots = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # 9 AM – 6 PM

                for event in result.get('items', []):
                    # Only block slots from events created by this booking system
                    # Check if the event description contains a reference code pattern
                    description = event.get('description', '')
                    summary = event.get('summary', '')
                    is_our_event = ('Reference:' in description or 
                                   summary.startswith('📸') or
                                   'Ref Code:' in description)
                    
                    if not is_our_event:
                        continue  # Skip events not created by this system

                    start = event['start'].get('dateTime', '')
                    if not start:
                        # All-day event from our system — block ALL slots for that day
                        for h in all_slots:
                            period = 'AM' if h < 12 else 'PM'
                            display_hour = h % 12 or 12
                            slot = f"{display_hour}:00 {period}"
                            if slot not in booked_times:
                                booked_times.append(slot)
                        continue

                    # Parse the event start time
                    # dateTime format: 2026-05-01T14:00:00+08:00
                    try:
                        time_part = start[11:16]  # "14:00"
                        ev_hour, ev_minute = map(int, time_part.split(':'))
                        period = 'AM' if ev_hour < 12 else 'PM'
                        display_hour = ev_hour % 12 or 12
                        slot = f"{display_hour}:{ev_minute:02d} {period}"
                        if slot not in booked_times:
                            booked_times.append(slot)
                    except Exception:
                        pass

        except Exception as gcal_err:
            # Google Calendar unavailable — fall back to Django-only
            print(f"Google Calendar fetch error (non-fatal): {gcal_err}")

        return JsonResponse({'booked_times': booked_times})

    except Exception as e:
        print(f'Error in booked_times_api: {e}')
        return JsonResponse({'booked_times': [], 'error': str(e)}, status=500)

def send_booking_cancellation_email(booking):
    """Send booking cancellation email"""
    subject = f"Booking Cancelled - {booking.reference_code}"
    
    date_str = booking.date.strftime('%B %d, %Y') if hasattr(booking.date, 'strftime') else str(booking.date)
    time_str = booking.time.strftime('%I:%M %p') if hasattr(booking.time, 'strftime') else str(booking.time)
    
    # Include cancellation reason if provided
    reason_section = ""
    if booking.cancellation_reason:
        reason_section = f"""
    CANCELLATION REASON:
    {booking.cancellation_reason}
    """
    
    message = f"""
    Dear {booking.customer_name},
    
    We regret to inform you that your booking has been cancelled.
    {reason_section}
    CANCELLED BOOKING DETAILS:
    Reference Code: {booking.reference_code}
    Date: {date_str}
    Time: {time_str}
    Package: {booking.package.name}
    Total Amount: ₱{booking.total_price:,.2f}
    
    If you have already made a payment, we will process your refund within 3-5 business days. You will receive a separate email confirmation once the refund has been processed.
    
    We sincerely apologize for any inconvenience this may cause. If you have any questions or would like to reschedule, please don't hesitate to contact us.
    
    CONTACT INFORMATION:
    Email: lookherespstudio@gmail.com
    Address: 2nd Floor, Chinabank Bldg, Gualberto Avenue, Poblacion B, Rosario, 4225 Batangas
    
    Thank you for your understanding.
    
    Best regards,
    Look Here Self Portrait Studio Team
    """
    
    try:
        send_mail(
            subject,
            message,
            django_settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )
        print(f"Cancellation email sent to {booking.email}")
        return True
    except Exception as e:
        print(f"Cancellation email error: {e}")
        return False


@staff_member_required
def quick_settings_api(request):
    """GET: return current site settings as JSON. POST: update selected fields."""
    settings = SiteSettings.get_settings()

    if request.method == 'POST':
        try:
            enable_bookings = request.POST.get('enable_bookings')
            max_daily = request.POST.get('max_daily_bookings')
            advance_days = request.POST.get('booking_advance_days')
            opening = request.POST.get('opening_time')
            closing = request.POST.get('closing_time')

            if enable_bookings is not None:
                settings.enable_bookings = enable_bookings == 'true'
            if max_daily is not None:
                settings.max_daily_bookings = int(max_daily)
            if advance_days is not None:
                settings.booking_advance_days = int(advance_days)
            if opening:
                settings.opening_time = opening
            if closing:
                settings.closing_time = closing

            settings.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    # GET — return current values
    return JsonResponse({
        'enable_bookings': settings.enable_bookings,
        'max_daily_bookings': settings.max_daily_bookings,
        'booking_advance_days': settings.booking_advance_days,
        'opening_time': settings.opening_time.strftime('%H:%M') if settings.opening_time else '09:00',
        'closing_time': settings.closing_time.strftime('%H:%M') if settings.closing_time else '18:00',
        'settings_url': '/admin/bookings/sitesettings/1/change/',
    })


@staff_member_required
def notifications_api(request):
    """Return all notifications for admin/staff as JSON, newest first.
    Includes both read and unread so the history panel always shows everything.
    """
    try:
        notifications = Notification.objects.order_by('-created_at')[:50]
        data = []
        for n in notifications:
            # Build admin URL for booking notifications so they're clickable
            admin_url = ''
            if n.notification_type == 'new_booking' and n.reference_code:
                try:
                    booking = Booking.objects.only('pk').get(reference_code=n.reference_code)
                    admin_url = f'/admin/bookings/booking/{booking.pk}/change/'
                except Booking.DoesNotExist:
                    pass
            data.append({
                'id': n.pk,
                'title': n.title,
                'message': n.message,
                'reference_code': n.reference_code,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%b %d, %Y %I:%M %p'),
                'admin_url': admin_url,
            })
        unread_count = sum(1 for n in data if not n['is_read'])
        print(f"Notifications API called: {len(data)} notifications, {unread_count} unread")
        return JsonResponse({'notifications': data, 'unread_count': unread_count})
    except Exception as e:
        print(f"Error in notifications_api: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'notifications': [], 'unread_count': 0, 'error': str(e)})


@staff_member_required
def notifications_mark_read(request):
    """Mark notifications as read.
    POST with 'id' param: marks a single notification.
    POST without 'id': marks all unread notifications.
    """
    if request.method == 'POST':
        notif_id = request.POST.get('id')
        if notif_id:
            Notification.objects.filter(pk=notif_id).update(is_read=True)
        else:
            Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@staff_member_required
def admin_reports(request):
    """Admin reports page with detailed analytics"""
    
    # Date range filter
    date_range = request.GET.get('range', '30')  # Default 30 days
    
    if date_range == '7':
        start_date = datetime.now() - timedelta(days=7)
        range_label = 'Last 7 Days'
    elif date_range == '30':
        start_date = datetime.now() - timedelta(days=30)
        range_label = 'Last 30 Days'
    elif date_range == '90':
        start_date = datetime.now() - timedelta(days=90)
        range_label = 'Last 90 Days'
    elif date_range == 'year':
        start_date = datetime.now() - timedelta(days=365)
        range_label = 'Last Year'
    else:
        start_date = datetime.now() - timedelta(days=30)
        range_label = 'Last 30 Days'
    
    # Client bookings report
    client_bookings = Booking.objects.filter(
        created_at__gte=start_date
    ).values('customer_name', 'email', 'phone').annotate(
        total_bookings=Count('id'),
        total_spent=Sum('total_price'),
        paid_bookings=Count('id', filter=Q(status='paid')),
        pending_bookings=Count('id', filter=Q(status='confirmed')),
    ).order_by('-total_bookings')[:20]
    
    # Weekly bookings report
    weekly_report = Booking.objects.filter(
        created_at__gte=start_date
    ).annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        total_bookings=Count('id'),
        paid_bookings=Count('id', filter=Q(status='paid')),
        revenue=Sum('total_price', filter=Q(status='paid'))
    ).order_by('-week')
    
    # Monthly bookings report
    monthly_report = Booking.objects.filter(
        created_at__gte=start_date
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_bookings=Count('id'),
        paid_bookings=Count('id', filter=Q(status='paid')),
        revenue=Sum('total_price', filter=Q(status='paid'))
    ).order_by('-month')
    
    # Package performance
    package_performance = Booking.objects.filter(
        created_at__gte=start_date,
        status='paid'
    ).values('package__name').annotate(
        bookings=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-revenue')
    
    # Daily bookings for the selected range
    daily_bookings = Booking.objects.filter(
        created_at__gte=start_date
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Summary stats
    total_bookings = Booking.objects.filter(created_at__gte=start_date).count()
    paid_bookings = Booking.objects.filter(created_at__gte=start_date, status='paid').count()
    total_revenue = Booking.objects.filter(created_at__gte=start_date, status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    avg_booking_value = total_revenue / paid_bookings if paid_bookings > 0 else 0
    
    context = {
        'client_bookings': client_bookings,
        'weekly_report': weekly_report,
        'monthly_report': monthly_report,
        'package_performance': package_performance,
        'daily_bookings': daily_bookings,
        'total_bookings': total_bookings,
        'paid_bookings': paid_bookings,
        'total_revenue': total_revenue,
        'avg_booking_value': avg_booking_value,
        'date_range': date_range,
        'range_label': range_label,
    }
    
    return render(request, 'admin/reports.html', context)


@staff_member_required
def notification_debug(request):
    """Debug page for testing notification system"""
    return render(request, 'admin/notification_debug.html')


@staff_member_required
def create_test_notification(request):
    """Create a test notification for debugging"""
    if request.method == 'POST':
        try:
            notif = Notification.objects.create(
                notification_type='new_booking',
                title='Test Notification',
                message=f'This is a test notification created at {datetime.now().strftime("%I:%M %p")}',
                reference_code='TEST-DEBUG',
                is_read=False
            )
            return JsonResponse({'success': True, 'id': notif.pk})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@staff_member_required
def package_prices_api(request):
    """Return all package prices for dynamic price calculation"""
    packages = Package.objects.all().values('id', 'name', 'base_price')
    data = [{'id': p['id'], 'name': p['name'], 'price': float(p['base_price'])} for p in packages]
    return JsonResponse({'packages': data})
