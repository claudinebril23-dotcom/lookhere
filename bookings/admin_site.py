from django.contrib.admin import AdminSite
from django.db.models import Sum
from .models import Booking, Package


class LookHereAdminSite(AdminSite):
    site_header = "Look Here Studio Administration"
    site_title = "Look Here Admin"
    index_title = "Dashboard"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add booking statistics
        extra_context['total_bookings'] = Booking.objects.count()
        extra_context['paid_bookings'] = Booking.objects.filter(status='paid').count()
        extra_context['pending_bookings'] = Booking.objects.filter(status='pending').count()
        extra_context['cancelled_bookings'] = Booking.objects.filter(status='cancelled').count()
        extra_context['total_revenue'] = Booking.objects.filter(status='paid').aggregate(
            Sum('total_price')
        )['total_price__sum'] or 0
        
        # Add package count
        extra_context['total_packages'] = Package.objects.count()
        
        # Add recent bookings (last 5)
        extra_context['recent_bookings'] = Booking.objects.select_related('package').order_by('-created_at')[:5]
        
        return super().index(request, extra_context)
