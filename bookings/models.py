from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in minutes")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)  # Indexed for sorting
    processing_time = models.CharField(max_length=50)  # e.g., 1-2 days, 3-5 days
    description = models.TextField()
    image = models.ImageField(upload_to='packages/', blank=True, null=True)

    class Meta:
        ordering = ['base_price']
        indexes = [
            models.Index(fields=['base_price'], name='package_price_idx'),
        ]

    def __str__(self):
        return self.name

class Addon(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name

import hashlib
import colorsys

class Backdrop(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True, editable=False)  # auto-generated
    image = models.ImageField(upload_to='backdrops/', blank=True, null=True, help_text="Upload backdrop image (optional)")

    # Predefined color palette for common backdrop names
    COLOR_MAPPINGS = {
        'white': '#f8fafc',
        'black': '#1e293b',
        'red': '#dc2626',
        'blue': '#2563eb',
        'green': '#16a34a',
        'yellow': '#eab308',
        'purple': '#9333ea',
        'pink': '#ec4899',
        'orange': '#ea580c',
        'gray': '#6b7280',
        'grey': '#6b7280',
        'brown': '#a16207',
        'beige': '#d6d3d1',
        'cream': '#fef7cd',
        'navy': '#1e3a8a',
        'teal': '#0d9488',
        'coral': '#f97316',
        'lavender': '#a78bfa',
        'mint': '#6ee7b7',
        'rose': '#f43f5e',
        'nude': '#d4a574',
    }

    def save(self, *args, **kwargs):
        # Auto-generate color based on name
        if self.name:
            name_lower = self.name.lower()
            
            # Check if name contains any predefined color keywords
            matched_color = None
            for color_name, color_value in self.COLOR_MAPPINGS.items():
                if color_name in name_lower:
                    matched_color = color_value
                    break
            
            if matched_color:
                self.color = matched_color
            else:
                # Generate color using improved HSV algorithm
                hash_object = hashlib.md5(name_lower.encode())
                hex_dig = hash_object.hexdigest()
                
                # Use hash to generate HSV values for better color control
                hue_seed = int(hex_dig[:8], 16)
                sat_seed = int(hex_dig[8:16], 16)
                val_seed = int(hex_dig[16:24], 16)
                
                # Generate hue (0-360 degrees) - full spectrum
                hue = (hue_seed % 360) / 360.0
                
                # Generate saturation (45-75% for vibrant but pleasant colors)
                saturation = 0.45 + (sat_seed % 30) / 100.0
                
                # Generate value/brightness (55-80% for good visibility)
                value = 0.55 + (val_seed % 25) / 100.0
                
                # Convert HSV to RGB
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
                
                # Convert to 0-255 range and format as hex
                r = int(r * 255)
                g = int(g * 255)
                b = int(b * 255)
                
                self.color = f"#{r:02x}{g:02x}{b:02x}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GalleryPhoto(models.Model):
    """Simple gallery photo model for website gallery"""
    CATEGORY_CHOICES = [
        ('solo', 'Solo'),
        ('twinning', 'Twinning'),
        ('group', 'Group'),
        ('super-party', 'Super Party'),
        ('academic', 'Academic'),
    ]
    
    title = models.CharField(max_length=200, help_text="Photo title or description")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='solo')
    image = models.ImageField(upload_to='gallery/', help_text="Upload gallery photo")
    is_active = models.BooleanField(default=True, help_text="Show on website")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

# Gallery models commented out - no longer in use
# class GalleryImage(models.Model):
#     title = models.CharField(max_length=100, help_text="Title/description of the gallery set")
#     quote = models.CharField(max_length=255, blank=True, help_text="Short quote or caption displayed with this gallery set (optional)")
#     category = models.CharField(max_length=50, choices=[
#         ('solo', 'Solo'),
#         ('couple', 'Twinning'),
#         ('group', 'Group'),
#         ('family', 'Super Party'),
#         ('academic', 'Academic'),
#         ('graduation', 'Graduation'),
#         ('prenup', 'Pre Nup'),
#     ], default='solo', help_text="Category for filtering in gallery")
#     is_active = models.BooleanField(default=True, help_text="Show in gallery")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Gallery Set"
#         verbose_name_plural = "Gallery Sets"

# class GalleryImageFile(models.Model):
#     gallery = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='gallery/', help_text="Upload gallery image")
#     order = models.IntegerField(default=0, help_text="Display order within the gallery set")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.gallery.title} - Image {self.order}"
    
#     class Meta:
#         ordering = ['order', 'created_at']
#         verbose_name = "Gallery Image"
#         verbose_name_plural = "Gallery Images"

class SiteSettings(models.Model):
    """Singleton model for site-wide settings like hero background."""
    hero_background_image = models.ImageField(
        upload_to='hero/',
        blank=True,
        null=True,
        help_text="Upload the homepage hero background image (recommended: 1920×1080px or larger)"
    )
    hero_overlay_opacity = models.FloatField(
        default=0.45,
        help_text="Dark overlay opacity over the hero image (0.0 = no overlay, 1.0 = fully black). Recommended: 0.3–0.7"
    )
    
    # Admin Logo
    admin_logo = models.ImageField(
        upload_to='admin_logo/',
        blank=True,
        null=True,
        help_text="Upload admin dashboard logo (recommended: 200×200px, transparent PNG)"
    )
    
    # About Page Image
    about_page_image = models.ImageField(
        upload_to='about_page/',
        blank=True,
        null=True,
        help_text="Upload the About page studio image (recommended: 700×450px or similar aspect ratio)"
    )
    
    # Business Hours
    opening_time = models.TimeField(
        default='09:00',
        help_text="Studio opening time"
    )
    closing_time = models.TimeField(
        default='18:00',
        help_text="Studio closing time"
    )

    # Booking Limits
    enable_bookings = models.BooleanField(
        default=True,
        help_text="Enable or disable the booking system for customers"
    )
    max_daily_bookings = models.IntegerField(
        default=0,
        help_text="Maximum number of bookings allowed per day (0 = unlimited)"
    )
    booking_advance_days = models.IntegerField(
        default=30,
        help_text="How many days in advance customers can book (e.g., 30 = up to 30 days from today)"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_settings(cls):
        """Always return the single settings instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        # Delete old hero image file when replacing
        if self.pk:
            try:
                old = SiteSettings.objects.get(pk=1)
                if old.hero_background_image and old.hero_background_image != self.hero_background_image:
                    old.hero_background_image.delete(save=False)
            except SiteSettings.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class Notification(models.Model):
    """In-app notification for admin/staff when a new booking is created."""
    TYPE_CHOICES = [
        ('new_booking', 'New Booking'),
    ]
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='new_booking')
    title = models.CharField(max_length=200)
    message = models.TextField()
    reference_code = models.CharField(max_length=20, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('gcash', 'GCash'),
        ('cash', 'Cash'),
    ]
    reference_code = models.CharField(max_length=20, unique=True, db_index=True)
    date = models.DateField(db_index=True)  # Indexed for date queries
    time = models.TimeField(db_index=True)  # Indexed for time slot queries
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    birthday = models.DateField(blank=True, null=True)
    voucher_code = models.CharField(max_length=50, blank=True, verbose_name="Promo Code", help_text="Promo code (optional)")
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    addons = models.ManyToManyField(Addon, blank=True)
    backdrop = models.ForeignKey(Backdrop, on_delete=models.SET_NULL, null=True, blank=True)
    pet_count = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='gcash')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', db_index=True)
    cancellation_reason = models.TextField(blank=True, null=True, help_text="Reason for cancellation (optional)")
    google_calendar_event_id = models.CharField(max_length=100, blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Time slot availability queries (date + time + status)
            models.Index(fields=['date', 'time', 'status'], name='booking_datetime_status_idx'),
            # Report queries by status and date range
            models.Index(fields=['status', 'created_at'], name='booking_status_created_idx'),
            # Customer lookup by email
            models.Index(fields=['email'], name='booking_email_idx'),
            # Package performance reports (package + status + created_at)
            models.Index(fields=['package', 'status', 'created_at'], name='booking_pkg_status_created_idx'),
            # Date-based queries (date + status)
            models.Index(fields=['date', 'status'], name='booking_date_status_idx'),
        ]

    def __str__(self):
        return self.reference_code
