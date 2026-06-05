#!/usr/bin/env python
"""
Test query performance with new indexes
"""
import os
import django
import time
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncWeek, TruncMonth
from bookings.models import Booking

def reset_query_log():
    """Reset Django query log"""
    from django.db import reset_queries
    reset_queries()

def get_query_count():
    """Get number of queries executed"""
    return len(connection.queries)

def time_query(func, description):
    """Time a query execution"""
    reset_query_log()
    start_time = time.time()
    result = func()
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
    query_count = get_query_count()
    
    return {
        'description': description,
        'time_ms': round(elapsed, 2),
        'query_count': query_count,
        'result_count': len(result) if hasattr(result, '__len__') else 'N/A'
    }

def test_performance():
    """Test various query patterns"""
    print("\n" + "="*80)
    print("DATABASE QUERY PERFORMANCE TEST")
    print("="*80 + "\n")
    
    # Get current record count
    total_bookings = Booking.objects.count()
    print(f"Total bookings in database: {total_bookings}")
    print("-" * 80 + "\n")
    
    # Date range for testing
    start_date = datetime.now() - timedelta(days=30)
    
    tests = []
    
    # Test 1: Time slot availability check
    print("Test 1: Time slot availability check")
    print("Query: filter(date=X, time=X, status__in=['pending', 'confirmed', 'paid'])")
    test_date = datetime.now().date()
    test_time = datetime.now().time()
    result = time_query(
        lambda: list(Booking.objects.filter(
            date=test_date,
            time=test_time,
            status__in=['pending', 'confirmed', 'paid']
        )),
        "Time slot check"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 2: Daily bookings by date
    print("Test 2: Daily bookings by date")
    print("Query: filter(date=X, status__in=['pending', 'confirmed', 'paid'])")
    result = time_query(
        lambda: list(Booking.objects.filter(
            date=test_date,
            status__in=['pending', 'confirmed', 'paid']
        )),
        "Daily bookings"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 3: Date range report (all bookings)
    print("Test 3: Date range report (all bookings)")
    print("Query: filter(created_at__gte=X)")
    result = time_query(
        lambda: list(Booking.objects.filter(created_at__gte=start_date)),
        "Date range (all)"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 4: Date range report (paid only)
    print("Test 4: Date range report (paid only)")
    print("Query: filter(created_at__gte=X, status='paid')")
    result = time_query(
        lambda: list(Booking.objects.filter(created_at__gte=start_date, status='paid')),
        "Date range (paid)"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 5: Package performance report
    print("Test 5: Package performance report")
    print("Query: filter(created_at__gte=X, status='paid').values('package__name').annotate(...)")
    result = time_query(
        lambda: list(Booking.objects.filter(
            created_at__gte=start_date,
            status='paid'
        ).values('package__name').annotate(
            bookings=Count('id'),
            revenue=Sum('total_price')
        ).order_by('-revenue')),
        "Package performance"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 6: Client bookings report
    print("Test 6: Client bookings report")
    print("Query: filter(created_at__gte=X).values(...).annotate(...)")
    result = time_query(
        lambda: list(Booking.objects.filter(
            created_at__gte=start_date
        ).values('customer_name', 'email', 'phone').annotate(
            total_bookings=Count('id'),
            total_spent=Sum('total_price'),
            paid_bookings=Count('id', filter=Q(status='paid')),
            pending_bookings=Count('id', filter=Q(status='pending')),
        ).order_by('-total_bookings')[:20]),
        "Client bookings"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 7: Weekly report
    print("Test 7: Weekly bookings report")
    print("Query: filter(created_at__gte=X).annotate(week=TruncWeek(...)).values(...)")
    result = time_query(
        lambda: list(Booking.objects.filter(
            created_at__gte=start_date
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total_bookings=Count('id'),
            paid_bookings=Count('id', filter=Q(status='paid')),
            revenue=Sum('total_price', filter=Q(status='paid'))
        ).order_by('-week')),
        "Weekly report"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Test 8: Monthly report
    print("Test 8: Monthly bookings report")
    print("Query: filter(created_at__gte=X).annotate(month=TruncMonth(...)).values(...)")
    result = time_query(
        lambda: list(Booking.objects.filter(
            created_at__gte=start_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_bookings=Count('id'),
            paid_bookings=Count('id', filter=Q(status='paid')),
            revenue=Sum('total_price', filter=Q(status='paid'))
        ).order_by('-month')),
        "Monthly report"
    )
    tests.append(result)
    print(f"   Time: {result['time_ms']}ms | Queries: {result['query_count']} | Results: {result['result_count']}")
    print()
    
    # Summary
    print("="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80 + "\n")
    
    total_time = sum(t['time_ms'] for t in tests)
    avg_time = total_time / len(tests)
    
    print(f"Total tests: {len(tests)}")
    print(f"Total time: {total_time:.2f}ms")
    print(f"Average time: {avg_time:.2f}ms")
    print()
    
    # Performance rating
    if avg_time < 10:
        rating = "🚀 EXCELLENT"
        color = "green"
    elif avg_time < 50:
        rating = "✅ GOOD"
        color = "green"
    elif avg_time < 100:
        rating = "⚠️ ACCEPTABLE"
        color = "yellow"
    else:
        rating = "❌ NEEDS OPTIMIZATION"
        color = "red"
    
    print(f"Performance Rating: {rating}")
    print()
    
    # Slowest queries
    print("Slowest Queries:")
    print("-" * 80)
    sorted_tests = sorted(tests, key=lambda x: x['time_ms'], reverse=True)
    for i, test in enumerate(sorted_tests[:3], 1):
        print(f"{i}. {test['description']}: {test['time_ms']}ms")
    print()
    
    # Index usage verification
    print("="*80)
    print("INDEX USAGE VERIFICATION")
    print("="*80 + "\n")
    
    # Check if indexes are being used
    with connection.cursor() as cursor:
        # Get index usage stats
        cursor.execute("""
            SELECT 
                indexrelname as index_name,
                idx_scan as scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            AND relname = 'bookings_booking'
            AND indexrelname IN (
                'booking_datetime_status_idx',
                'booking_status_created_idx',
                'booking_email_idx',
                'booking_pkg_status_created_idx',
                'booking_date_status_idx'
            )
            ORDER BY idx_scan DESC;
        """)
        
        results = cursor.fetchall()
        
        print("Index Usage Statistics:")
        print("-" * 80)
        print(f"{'Index Name':<40} {'Scans':<10} {'Tuples Read':<15} {'Tuples Fetched':<15}")
        print("-" * 80)
        
        for row in results:
            index_name, scans, tuples_read, tuples_fetched = row
            print(f"{index_name:<40} {scans:<10} {tuples_read:<15} {tuples_fetched:<15}")
        
        print("-" * 80)
        print()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 80)
    
    if total_bookings < 100:
        print("⚠️ Database has fewer than 100 records.")
        print("   Performance benefits of indexes are most visible with 1,000+ records.")
        print("   Current performance is excellent due to small dataset size.")
    elif total_bookings < 1000:
        print("✅ Database has a good number of records for testing.")
        print("   Indexes are providing measurable performance benefits.")
    else:
        print("🚀 Database has significant data volume.")
        print("   Indexes are critical for maintaining fast query performance.")
    
    print()
    
    if avg_time < 50:
        print("✅ Query performance is excellent!")
        print("   No optimization needed at this time.")
    elif avg_time < 100:
        print("⚠️ Query performance is acceptable but could be improved.")
        print("   Consider adding more specific indexes for slow queries.")
    else:
        print("❌ Query performance needs optimization.")
        print("   Review slow queries and consider additional indexes.")
    
    print("-" * 80 + "\n")

if __name__ == '__main__':
    test_performance()
