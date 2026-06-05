from django.http import JsonResponse
from django.db.models import Q
from .models import Booking, Package, Addon, Backdrop, GalleryPhoto

def global_search_api(request):
    """
    Global search API endpoint that searches across multiple models.
    Returns aggregated results grouped by model type.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Search Bookings
    bookings = Booking.objects.filter(
        Q(reference_code__icontains=query) |
        Q(customer_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    ).select_related('package')[:5]
    
    for booking in bookings:
        results.append({
            'type': 'Booking',
            'title': f"{booking.reference_code} - {booking.customer_name}",
            'meta': [
                f"📅 {booking.date.strftime('%b %d, %Y')}",
                f"📦 {booking.package.name}",
                f"Status: {booking.get_status_display()}"
            ],
            'url': f"/admin/bookings/booking/{booking.id}/change/"
        })
    
    # Search Packages
    packages = Package.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:5]
    
    for package in packages:
        results.append({
            'type': 'Package',
            'title': package.name,
            'meta': [
                f"⏱️ {package.duration} min",
                f"💰 ₱{package.base_price:,.2f}"
            ],
            'url': f"/admin/bookings/package/{package.id}/change/"
        })
    
    # Search Add-ons
    addons = Addon.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:5]
    
    for addon in addons:
        results.append({
            'type': 'Add-on',
            'title': addon.name,
            'meta': [
                f"💰 +₱{addon.price:,.2f}"
            ],
            'url': f"/admin/bookings/addon/{addon.id}/change/"
        })
    
    # Search Backdrops
    backdrops = Backdrop.objects.filter(name__icontains=query)[:5]
    
    for backdrop in backdrops:
        results.append({
            'type': 'Backdrop',
            'title': backdrop.name,
            'meta': [
                f"🎨 {backdrop.color}"
            ],
            'url': f"/admin/bookings/backdrop/{backdrop.id}/change/"
        })
    
    # Search Gallery Photos
    gallery_photos = GalleryPhoto.objects.filter(
        Q(title__icontains=query) |
        Q(category__icontains=query)
    )[:5]
    
    for photo in gallery_photos:
        results.append({
            'type': 'Gallery',
            'title': photo.title,
            'meta': [
                f"📁 {photo.get_category_display()}",
                '✅ Active' if photo.is_active else '❌ Inactive'
            ],
            'url': f"/admin/bookings/galleryphoto/{photo.id}/change/"
        })
    
    return JsonResponse({'results': results})
