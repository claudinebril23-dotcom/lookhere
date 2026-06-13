from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncDate
from django.db import models
from datetime import datetime, timedelta
import json
from .models import Package, Addon, Backdrop, Booking, SiteSettings, GalleryPhoto, Notification
from .views import send_booking_confirmation_email, send_booking_sms, send_booking_cancellation_email


# Customize admin site
admin.site.site_header = "Look Here Studio Administration"
admin.site.site_title = "Look Here Admin"
admin.site.index_title = "Dashboard"


# Add dashboard stats to admin index
admin.site.index_template = 'admin/index.html'
admin.site.enable_nav_sidebar = False  # Disable sidebar for cleaner look


def get_dashboard_context():
    """Get comprehensive dashboard statistics and analytics"""
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Basic stats
    total_bookings = Booking.objects.count()
    paid_bookings = Booking.objects.filter(status='paid').count()
    pending_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    total_revenue = Booking.objects.filter(status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Weekly stats (scalar — last 7 days)
    weekly_bookings = Booking.objects.filter(created_at__gte=seven_days_ago).count()
    weekly_revenue = Booking.objects.filter(status='paid', created_at__gte=seven_days_ago).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Monthly stats (scalar — last 30 days)
    monthly_bookings = Booking.objects.filter(created_at__gte=thirty_days_ago).count()
    monthly_revenue = Booking.objects.filter(status='paid', created_at__gte=thirty_days_ago).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Weekly report — per-week breakdown (last 8 weeks)
    eight_weeks_ago = now - timedelta(weeks=8)
    weekly_report = (
        Booking.objects
        .filter(created_at__gte=eight_weeks_ago)
        .annotate(week=TruncWeek('created_at'))
        .values('week')
        .annotate(
            total_bookings=Count('id'),
            paid_bookings=Count('id', filter=models.Q(status='paid')),
            revenue=Sum('total_price', filter=models.Q(status='paid')),
        )
        .order_by('-week')[:8]
    )

    # Monthly report — per-month breakdown (last 6 months)
    six_months_ago = now - timedelta(days=180)
    monthly_report = (
        Booking.objects
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total_bookings=Count('id'),
            paid_bookings=Count('id', filter=models.Q(status='paid')),
            revenue=Sum('total_price', filter=models.Q(status='paid')),
        )
        .order_by('-month')[:6]
    )

    # Top clients — aggregated per customer (last 30 days)
    client_bookings = (
        Booking.objects
        .filter(created_at__gte=thirty_days_ago)
        .values('customer_name', 'email', 'phone')
        .annotate(
            total_bookings=Count('id'),
            total_spent=Sum('total_price'),
            paid_bookings=Count('id', filter=models.Q(status='paid')),
        )
        .order_by('-total_bookings')[:10]
    )

    # Daily report — per-day breakdown (last 14 days)
    fourteen_days_ago = now - timedelta(days=13)
    daily_report = (
        Booking.objects
        .filter(date__gte=fourteen_days_ago.date())
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(
            total_bookings=Count('id'),
            paid_bookings=Count('id', filter=models.Q(status='paid')),
            confirmed_bookings=Count('id', filter=models.Q(status='confirmed')),
            cancelled_bookings=Count('id', filter=models.Q(status='cancelled')),
            revenue=Sum('total_price', filter=models.Q(status='paid')),
        )
        .order_by('-day')[:14]
    )

    # Daily trends for chart (last 14 days, fills gaps with 0)
    daily_trends = []
    for i in range(13, -1, -1):
        d = (now - timedelta(days=i)).date()
        count = Booking.objects.filter(date=d).count()
        revenue_day = Booking.objects.filter(
            date=d, status='paid'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        daily_trends.append({
            'date': d.strftime('%b %d'),
            'count': count,
            'revenue': float(revenue_day),
        })

    # Today's stats
    today = now.date()
    today_bookings = Booking.objects.filter(date=today).count()
    today_paid = Booking.objects.filter(date=today, status='paid').count()
    today_confirmed = Booking.objects.filter(date=today, status='confirmed').count()
    today_cancelled = Booking.objects.filter(date=today, status='cancelled').count()
    today_revenue = Booking.objects.filter(
        date=today, status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Yesterday's stats for comparison
    yesterday = today - timedelta(days=1)
    yesterday_bookings = Booking.objects.filter(date=yesterday).count()
    yesterday_revenue = Booking.objects.filter(
        date=yesterday, status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # 14-day revenue total (sum across daily_report)
    daily_revenue_total = Booking.objects.filter(
        date__gte=fourteen_days_ago.date(), status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Weekly revenue total (sum across weekly_report = last 8 weeks)
    weekly_revenue_total = Booking.objects.filter(
        created_at__gte=eight_weeks_ago, status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Monthly revenue total (sum across monthly_report = last 6 months)
    monthly_revenue_total = Booking.objects.filter(
        created_at__gte=six_months_ago, status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Top packages
    top_packages = Booking.objects.filter(status='paid').values('package__name').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-count')[:5]

    # Recent bookings
    recent_bookings = Booking.objects.select_related('package').order_by('-created_at')[:10]

    # Booking trends (last 7 days)
    booking_trends = []
    for i in range(6, -1, -1):
        date = now.date() - timedelta(days=i)
        count = Booking.objects.filter(created_at__date=date).count()
        booking_trends.append({
            'date': date.strftime('%b %d'),
            'count': count
        })

    # Revenue trends (last 6 months)
    revenue_trends = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        revenue = Booking.objects.filter(
            status='paid',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        revenue_trends.append({
            'month': month_start.strftime('%b'),
            'revenue': float(revenue)
        })

    return {
        'total_bookings': total_bookings,
        'paid_bookings': paid_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'weekly_bookings': weekly_bookings,
        'weekly_revenue': weekly_revenue,
        'monthly_bookings': monthly_bookings,
        'monthly_revenue': monthly_revenue,
        'weekly_report': weekly_report,
        'monthly_report': monthly_report,
        'client_bookings': client_bookings,
        'total_packages': Package.objects.count(),
        'recent_bookings': recent_bookings,
        'top_packages': top_packages,
        'booking_trends': json.dumps(booking_trends),
        'revenue_trends': json.dumps(revenue_trends),
        # Daily performance
        'daily_report': daily_report,
        'daily_trends': json.dumps(daily_trends),
        'today_bookings': today_bookings,
        'today_paid': today_paid,
        'today_confirmed': today_confirmed,
        'today_cancelled': today_cancelled,
        'today_revenue': today_revenue,
        'yesterday_bookings': yesterday_bookings,
        'yesterday_revenue': yesterday_revenue,
        'daily_revenue_total': daily_revenue_total,
        'weekly_revenue_total': weekly_revenue_total,
        'monthly_revenue_total': monthly_revenue_total,
    }


# Override admin index to add custom context
from django.contrib.admin import AdminSite as BaseAdminSite

class CustomAdminSite(BaseAdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(get_dashboard_context())
        # Add site settings for logo
        extra_context['site_settings'] = SiteSettings.get_settings()
        return super().index(request, extra_context)
    
    def each_context(self, request):
        """Add site settings to every admin page"""
        context = super().each_context(request)
        context['site_settings'] = SiteSettings.get_settings()
        return context

# Replace default admin site
admin.site.__class__ = CustomAdminSite




@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price_display', 'processing_time', 'image_preview')
    list_filter = ('processing_time',)
    search_fields = ('name',)
    fields = ('name', 'duration', 'base_price', 'processing_time', 'description', 'image')
    ordering = ('base_price',)
    
    def price_display(self, obj):
        return format_html(
            '<span style="color:#667eea;font-weight:600;font-size:14px;">₱{}</span>',
            f'{obj.base_price:,.2f}'
        )
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'base_price'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 6px; border: 2px solid #e5e7eb;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'

@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_display', 'description_preview')
    search_fields = ('name',)
    ordering = ('price',)
    
    def price_display(self, obj):
        return format_html(
            '<span style="color:#10b981;font-weight:600;font-size:14px;">+₱{}</span>',
            f'{obj.price:,.2f}'
        )
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def description_preview(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description or '-'
    description_preview.short_description = 'Description'

@admin.register(Backdrop)
class BackdropAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'color_preview', 'image_preview')
    search_fields = ('name',)
    fields = ('name', 'image')
    readonly_fields = ('color',)
    
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    color_preview.short_description = 'Color Preview'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: cover; border-radius: 3px; border: 1px solid #ccc;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Image Preview'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    from .forms import BookingAdminForm
    form = BookingAdminForm
    
    list_display = ('reference_code', 'customer_name', 'date_time_display', 'package', 'total_price_display', 'status_badge', 'created_at')
    list_filter = ('status', 'date', 'package')
    search_fields = ('reference_code', 'customer_name')
    readonly_fields = ('reference_code', 'created_at', 'google_calendar_event_id')
    date_hierarchy = 'date'
    ordering = ('-created_at',)
    actions = ['send_confirmation_email', 'mark_as_paid', 'mark_as_cancelled']
    list_per_page = 25

    class Media:
        js = ('admin/js/jquery.init.js',)
        css = {
            'all': ('bookings/css/booking_admin.css',)
        }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['stat_total'] = Booking.objects.count()
        extra_context['stat_confirmed'] = Booking.objects.filter(status='confirmed').count()
        extra_context['stat_paid'] = Booking.objects.filter(status='paid').count()
        extra_context['stat_cancelled'] = Booking.objects.filter(status='cancelled').count()
        return super().changelist_view(request, extra_context=extra_context)


    fieldsets = (
        ('📅 Booking Details', {
            'fields': ('reference_code', 'date', 'time', 'status', 'package', 'addon', 'backdrop'),
        }),
        ('👤 Customer Information', {
            'fields': ('customer_name', 'email', 'phone', 'voucher_code', 'pet_count', 'total_price'),
        }),
        ('🔧 System Information', {
            'fields': ('google_calendar_event_id', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    def date_time_display(self, obj):
        return format_html(
            '<div style="line-height:1.6;">'
            '<div style="font-weight:600;color:#1f2937;">{}</div>'
            '<div style="font-size:13px;color:#6b7280;">{}</div>'
            '</div>',
            obj.date.strftime('%b %d, %Y'),
            obj.time.strftime('%I:%M %p')
        )
    date_time_display.short_description = 'Date & Time'
    date_time_display.admin_order_field = 'date'
    
    def total_price_display(self, obj):
        return format_html(
            '<span style="color:#667eea;font-weight:700;font-size:15px;">₱{}</span>',
            f'{obj.total_price:,.2f}'
        )
    total_price_display.short_description = 'Total'
    total_price_display.admin_order_field = 'total_price'

    def status_badge(self, obj):
        colours = {
            'confirmed': ('#dbeafe', '#1e40af'),  # Blue for confirmed
            'paid':      ('#d1fae5', '#065f46'),
            'cancelled': ('#fee2e2', '#991b1b'),
        }
        bg, fg = colours.get(obj.status, ('#f1f5f9', '#475569'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;'
            'font-size:0.78rem;font-weight:600;white-space:nowrap;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


    def send_confirmation_email(self, request, queryset):
        count = 0
        for booking in queryset:
            if send_booking_confirmation_email(booking):
                count += 1
        self.message_user(request, f"✅ Confirmation emails sent to {count} booking(s).")
    send_confirmation_email.short_description = "📧 Send confirmation email"
    
    def mark_as_paid(self, request, queryset):
        count = queryset.update(status='paid')
        for booking in queryset:
            send_booking_confirmation_email(booking)
        self.message_user(request, f"✅ {count} booking(s) marked as paid and confirmation emails sent.")
    mark_as_paid.short_description = "✓ Mark as Paid"
    
    def mark_as_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f"❌ {count} booking(s) marked as cancelled.")
    mark_as_cancelled.short_description = "✗ Mark as Cancelled"

    def receipt_link(self, obj):
        if obj.status == 'paid':
            receipt_url = f"/receipt/{obj.reference_code}/"
            return format_html(
                '<a class="button" href="{}" target="_blank">View Receipt</a>',
                receipt_url
            )
        return '-'
    receipt_link.short_description = 'Receipt'

    def save_model(self, request, obj, form, change):
        """Handles both detail-view saves and list-view inline saves."""
        if change:
            try:
                original = Booking.objects.get(pk=obj.pk)
                original_status = original.status
            except Booking.DoesNotExist:
                original_status = None

            super().save_model(request, obj, form, change)

            # Save the single addon selection into the M2M field
            selected_addon = form.cleaned_data.get('addon')
            if selected_addon:
                obj.addons.set([selected_addon])
            else:
                obj.addons.clear()

            if original_status and original_status != obj.status:
                # confirmed → paid: send confirmation email + SMS to customer
                if original_status == 'confirmed' and obj.status == 'paid':
                    send_booking_confirmation_email(obj)
                    send_booking_sms(obj)
                    # Update calendar event to green (paid)
                    try:
                        from .google_calendar import update_calendar_event
                        if obj.google_calendar_event_id:
                            update_calendar_event(obj, obj.google_calendar_event_id)
                    except Exception as e:
                        print(f"Google Calendar update error: {e}")
                # any → cancelled
                elif obj.status == 'cancelled' and original_status != 'cancelled':
                    send_booking_cancellation_email(obj)
                    # Delete calendar event
                    try:
                        from .google_calendar import delete_calendar_event
                        if obj.google_calendar_event_id:
                            delete_calendar_event(obj.google_calendar_event_id)
                    except Exception as e:
                        print(f"Google Calendar delete error: {e}")
            return

        # New booking — auto-generate reference_code if not set
        # (readonly_fields prevents the form from submitting it)
        if not obj.reference_code:
            import uuid as _uuid
            while True:
                candidate = f"LOOKHERE-{_uuid.uuid4().hex[:5].upper()}"
                if not Booking.objects.filter(reference_code=candidate).exists():
                    obj.reference_code = candidate
                    break

        super().save_model(request, obj, form, change)
        # Save addon for new bookings too
        selected_addon = form.cleaned_data.get('addon')
        if selected_addon:
            obj.addons.set([selected_addon])
        else:
            obj.addons.clear()


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero_background_preview', 'about_page_image_preview', 'admin_logo_preview', 'hero_overlay_opacity')
    fieldsets = (
        ('Admin Branding', {
            'fields': ('admin_logo',),
            'description': 'Upload your admin dashboard logo (recommended: 200×200px, transparent PNG)'
        }),
        ('Homepage Hero Section', {
            'fields': ('hero_background_image', 'hero_overlay_opacity'),
            'description': 'Upload a hero background image (recommended: 1920×1080px or larger). Adjust overlay opacity to control text readability (0.0 = no overlay, 1.0 = fully dark).'
        }),
        ('About Page Settings', {
            'fields': ('about_page_image',),
            'description': 'Upload the About page studio image (recommended: 700×450px or similar aspect ratio). This image appears in the "Who We Are" section.'
        }),
        ('Business Hours', {
            'fields': ('opening_time', 'closing_time'),
            'description': 'Set studio operating hours'
        }),
        ('Booking Limits', {
            'fields': ('enable_bookings', 'max_daily_bookings', 'booking_advance_days'),
            'description': (
                'Control booking availability. '
                '"Enable Bookings" toggles the entire booking system. '
                '"Max Daily Bookings" limits how many bookings can be made per day (0 = unlimited). '
                '"Advance Days" sets how far in advance customers can book.'
            )
        }),
    )
    
    def hero_background_preview(self, obj):
        if obj.hero_background_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 6px;" />',
                obj.hero_background_image.url
            )
        return '-'
    hero_background_preview.short_description = 'Hero Background'
    
    def about_page_image_preview(self, obj):
        if obj.about_page_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 65px; object-fit: cover; border-radius: 6px;" />',
                obj.about_page_image.url
            )
        return '-'
    about_page_image_preview.short_description = 'About Page Image'
    
    def admin_logo_preview(self, obj):
        if obj.admin_logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: contain; border-radius: 6px; background: #f3f4f6; padding: 5px;" />',
                obj.admin_logo.url
            )
        return '-'
    admin_logo_preview.short_description = 'Admin Logo'
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'reference_code', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'reference_code')
    readonly_fields = ('notification_type', 'title', 'message', 'reference_code', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 50
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('notification_type', 'title', 'message', 'reference_code')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Notifications are created automatically by signals
        return False
