#!/usr/bin/env python
"""
Verify database indexes on bookings_booking table
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from django.db import connection

def verify_indexes():
    """Check all indexes on bookings_booking table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                indexname, 
                indexdef 
            FROM pg_indexes 
            WHERE tablename = 'bookings_booking'
            ORDER BY indexname;
        """)
        
        results = cursor.fetchall()
        
        print("\n" + "="*80)
        print("BOOKINGS TABLE INDEXES")
        print("="*80 + "\n")
        
        for i, (index_name, index_def) in enumerate(results, 1):
            print(f"{i}. {index_name}")
            print(f"   {index_def}")
            print()
        
        print(f"Total indexes: {len(results)}")
        print("="*80 + "\n")
        
        # Check for our new indexes
        index_names = [row[0] for row in results]
        
        required_indexes = [
            'booking_datetime_status_idx',
            'booking_status_created_idx',
            'booking_email_idx',
            'booking_pkg_status_created_idx',  # NEW
            'booking_date_status_idx',  # NEW
        ]
        
        print("INDEX VERIFICATION:")
        print("-" * 80)
        for idx in required_indexes:
            status = "✅ FOUND" if idx in index_names else "❌ MISSING"
            print(f"{status}: {idx}")
        print("-" * 80 + "\n")
        
        # Check index sizes
        cursor.execute("""
            SELECT 
                indexrelname as index_name,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            AND relname = 'bookings_booking'
            ORDER BY pg_relation_size(indexrelid) DESC;
        """)
        
        sizes = cursor.fetchall()
        
        print("INDEX SIZES:")
        print("-" * 80)
        for index_name, size in sizes:
            print(f"{index_name}: {size}")
        print("-" * 80 + "\n")

if __name__ == '__main__':
    verify_indexes()
