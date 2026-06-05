"""
Management command to check database performance and query optimization.
Usage: python manage.py check_performance
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import override_settings
from bookings.models import Package, Booking, GalleryImage
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check database performance and query optimization'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('DATABASE PERFORMANCE CHECK'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # Reset query counter
        connection.queries_log.clear()

        # Test 1: Package queries
        self.stdout.write(self.style.WARNING('Test 1: Package Queries'))
        self.stdout.write('-' * 70)
        
        query_count_before = len(connection.queries)
        packages = list(Package.objects.only('id', 'name', 'base_price').order_by('base_price'))
        query_count_after = len(connection.queries)
        
        self.stdout.write(f"✓ Fetched {len(packages)} packages")
        self.stdout.write(f"✓ Queries executed: {query_count_after - query_count_before}")
        self.stdout.write(self.style.SUCCESS('✓ OPTIMIZED' if query_count_after - query_count_before <= 1 else '✗ NEEDS OPTIMIZATION'))
        self.stdout.write('')

        # Test 2: Booking with relations
        self.stdout.write(self.style.WARNING('Test 2: Booking with Relations'))
        self.stdout.write('-' * 70)
        
        query_count_before = len(connection.queries)
        bookings = list(
            Booking.objects
            .select_related('package', 'backdrop')
            .prefetch_related('addons')
            .order_by('-created_at')[:10]
        )
        
        # Access related objects to trigger queries
        for booking in bookings:
            _ = booking.package.name
            if booking.backdrop:
                _ = booking.backdrop.name
            _ = list(booking.addons.all())
        
        query_count_after = len(connection.queries)
        
        self.stdout.write(f"✓ Fetched {len(bookings)} bookings with relations")
        self.stdout.write(f"✓ Queries executed: {query_count_after - query_count_before}")
        self.stdout.write(self.style.SUCCESS('✓ OPTIMIZED' if query_count_after - query_count_before <= 3 else '✗ NEEDS OPTIMIZATION'))
        self.stdout.write('')

        # Test 3: Gallery with images
        self.stdout.write(self.style.WARNING('Test 3: Gallery with Images'))
        self.stdout.write('-' * 70)
        
        query_count_before = len(connection.queries)
        galleries = list(
            GalleryImage.objects
            .filter(is_active=True)
            .prefetch_related('images')
            .only('id', 'title', 'quote', 'category')[:6]
        )
        
        # Access related images
        for gallery in galleries:
            _ = list(gallery.images.all())
        
        query_count_after = len(connection.queries)
        
        self.stdout.write(f"✓ Fetched {len(galleries)} galleries with images")
        self.stdout.write(f"✓ Queries executed: {query_count_after - query_count_before}")
        self.stdout.write(self.style.SUCCESS('✓ OPTIMIZED' if query_count_after - query_count_before <= 2 else '✗ NEEDS OPTIMIZATION'))
        self.stdout.write('')

        # Test 4: Time slot availability check
        self.stdout.write(self.style.WARNING('Test 4: Time Slot Availability'))
        self.stdout.write('-' * 70)
        
        today = timezone.now().date()
        query_count_before = len(connection.queries)
        
        booked = Booking.objects.filter(
            date=today,
            status__in=['pending', 'paid']
        ).values_list('time', flat=True)
        _ = list(booked)
        
        query_count_after = len(connection.queries)
        
        self.stdout.write(f"✓ Checked availability for {today}")
        self.stdout.write(f"✓ Queries executed: {query_count_after - query_count_before}")
        self.stdout.write(self.style.SUCCESS('✓ OPTIMIZED' if query_count_after - query_count_before <= 1 else '✗ NEEDS OPTIMIZATION'))
        self.stdout.write('')

        # Database statistics
        self.stdout.write(self.style.WARNING('Database Statistics'))
        self.stdout.write('-' * 70)
        
        total_packages = Package.objects.count()
        total_bookings = Booking.objects.count()
        total_galleries = GalleryImage.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        paid_bookings = Booking.objects.filter(status='paid').count()
        
        self.stdout.write(f"📦 Total Packages: {total_packages}")
        self.stdout.write(f"📅 Total Bookings: {total_bookings}")
        self.stdout.write(f"   ├─ Pending: {pending_bookings}")
        self.stdout.write(f"   └─ Paid: {paid_bookings}")
        self.stdout.write(f"🖼️  Total Gallery Sets: {total_galleries}")
        self.stdout.write('')

        # Index check
        self.stdout.write(self.style.WARNING('Database Indexes'))
        self.stdout.write('-' * 70)
        
        try:
            with connection.cursor() as cursor:
                # Check database type
                db_vendor = connection.vendor
                
                if db_vendor == 'postgresql':
                    cursor.execute("""
                        SELECT indexname, tablename 
                        FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename LIKE 'bookings_%'
                        ORDER BY tablename, indexname;
                    """)
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        self.stdout.write(f"✓ Found {len(indexes)} indexes on booking tables")
                        for idx_name, table_name in indexes[:10]:
                            self.stdout.write(f"  • {table_name}: {idx_name}")
                    else:
                        self.stdout.write(self.style.ERROR("✗ No custom indexes found"))
                
                elif db_vendor == 'sqlite':
                    cursor.execute("""
                        SELECT name, tbl_name 
                        FROM sqlite_master 
                        WHERE type = 'index' 
                        AND tbl_name LIKE 'bookings_%'
                        ORDER BY tbl_name, name;
                    """)
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        self.stdout.write(f"✓ Found {len(indexes)} indexes on booking tables")
                        for idx_name, table_name in indexes[:10]:
                            self.stdout.write(f"  • {table_name}: {idx_name}")
                    else:
                        self.stdout.write(self.style.ERROR("✗ No custom indexes found"))
                else:
                    self.stdout.write(f"ℹ Database type: {db_vendor} (index check not implemented)")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Could not check indexes: {e}"))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('PERFORMANCE CHECK COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
