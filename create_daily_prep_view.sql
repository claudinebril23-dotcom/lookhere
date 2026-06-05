-- ============================================================================
-- DAILY STUDIO PREPARATION VIEW
-- ============================================================================
-- Purpose: Provide staff with daily setup information without sensitive data
-- Based on: Views (Page 13) and Joins (Page 8) from handout
-- Security: Excludes customer contact info, prices, and payment details
-- ============================================================================

-- ============================================================================
-- 1. CREATE VIEW: v_today_studio_setup
-- ============================================================================
-- Purpose: Show today's bookings with setup information only
-- Joins: bookings_booking + bookings_package + bookings_backdrop
-- Filter: Only today's date, only confirmed/paid bookings
-- Security: No customer contact info, no prices
-- ============================================================================

CREATE OR REPLACE VIEW v_today_studio_setup AS
SELECT 
    -- Time information (for scheduling)
    b.time AS booking_time,
    
    -- Package information (what equipment to prepare)
    p.name AS package_name,
    p.duration AS session_duration,
    
    -- Backdrop information (what to set up)
    bd.name AS backdrop_name,
    bd.color AS backdrop_color,
    
    -- Booking reference (for staff to identify session)
    b.reference_code AS session_ref,
    
    -- Status (to know which are confirmed)
    b.status AS booking_status,
    
    -- Date (for filtering)
    b.date AS booking_date
    
FROM bookings_booking b
    -- JOIN with package table (Page 8 - Inner Join)
    INNER JOIN bookings_package p ON b.package_id = p.id
    
    -- LEFT JOIN with backdrop (some bookings may not have backdrop)
    LEFT JOIN bookings_backdrop bd ON b.backdrop_id = bd.id

WHERE 
    -- Filter for today's date only
    b.date = CURRENT_DATE
    
    -- Only show confirmed or paid bookings (not pending/cancelled)
    AND b.status IN ('confirmed', 'paid')

-- Order by time for easy morning preparation
ORDER BY b.time ASC;

-- ============================================================================
-- SECURITY NOTES:
-- ============================================================================
-- EXCLUDED (Sensitive Data):
-- - customer_name (privacy)
-- - email (privacy)
-- - phone (privacy)
-- - total_price (business data)
-- - payment_method (business data)
-- - payment_proof (business data)
-- - birthday (privacy)
-- - voucher_code (business data)
--
-- INCLUDED (Setup Information Only):
-- - booking_time (when to prepare)
-- - package_name (what equipment needed)
-- - session_duration (how long to allocate)
-- - backdrop_name (what backdrop to set up)
-- - backdrop_color (visual reference)
-- - session_ref (to identify the session)
-- - booking_status (confirmed vs paid)
-- ============================================================================


-- ============================================================================
-- 2. CREATE VIEW: v_tomorrow_studio_setup
-- ============================================================================
-- Purpose: Show tomorrow's bookings for advance preparation
-- Same structure as today's view but for next day
-- ============================================================================

CREATE OR REPLACE VIEW v_tomorrow_studio_setup AS
SELECT 
    b.time AS booking_time,
    p.name AS package_name,
    p.duration AS session_duration,
    bd.name AS backdrop_name,
    bd.color AS backdrop_color,
    b.reference_code AS session_ref,
    b.status AS booking_status,
    b.date AS booking_date
    
FROM bookings_booking b
    INNER JOIN bookings_package p ON b.package_id = p.id
    LEFT JOIN bookings_backdrop bd ON b.backdrop_id = bd.id

WHERE 
    b.date = CURRENT_DATE + INTERVAL '1 day'
    AND b.status IN ('confirmed', 'paid')

ORDER BY b.time ASC;


-- ============================================================================
-- 3. CREATE VIEW: v_weekly_studio_schedule
-- ============================================================================
-- Purpose: Show this week's bookings for weekly planning
-- Useful for staff to see the week ahead
-- ============================================================================

CREATE OR REPLACE VIEW v_weekly_studio_schedule AS
SELECT 
    b.date AS booking_date,
    b.time AS booking_time,
    p.name AS package_name,
    p.duration AS session_duration,
    bd.name AS backdrop_name,
    bd.color AS backdrop_color,
    b.reference_code AS session_ref,
    b.status AS booking_status
    
FROM bookings_booking b
    INNER JOIN bookings_package p ON b.package_id = p.id
    LEFT JOIN bookings_backdrop bd ON b.backdrop_id = bd.id

WHERE 
    -- This week (Monday to Sunday)
    b.date >= DATE_TRUNC('week', CURRENT_DATE)
    AND b.date < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '7 days'
    AND b.status IN ('confirmed', 'paid')

ORDER BY b.date ASC, b.time ASC;


-- ============================================================================
-- 4. HELPER VIEW: v_studio_setup_summary
-- ============================================================================
-- Purpose: Daily summary of what needs to be prepared
-- Shows count of each package type and backdrop needed
-- ============================================================================

CREATE OR REPLACE VIEW v_studio_setup_summary AS
SELECT 
    b.date AS booking_date,
    p.name AS package_name,
    bd.name AS backdrop_name,
    COUNT(*) AS session_count,
    STRING_AGG(TO_CHAR(b.time, 'HH24:MI'), ', ' ORDER BY b.time) AS time_slots
    
FROM bookings_booking b
    INNER JOIN bookings_package p ON b.package_id = p.id
    LEFT JOIN bookings_backdrop bd ON b.backdrop_id = bd.id

WHERE 
    b.date = CURRENT_DATE
    AND b.status IN ('confirmed', 'paid')

GROUP BY b.date, p.name, bd.name
ORDER BY session_count DESC;


-- ============================================================================
-- 5. VERIFICATION QUERIES
-- ============================================================================

-- Check if views were created successfully
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'v_today_studio_setup',
      'v_tomorrow_studio_setup',
      'v_weekly_studio_schedule',
      'v_studio_setup_summary'
  )
ORDER BY table_name;

-- Check view columns (verify no sensitive data)
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'v_today_studio_setup'
ORDER BY ordinal_position;


-- ============================================================================
-- 6. USAGE EXAMPLES
-- ============================================================================

-- Example 1: View today's setup list
-- SELECT * FROM v_today_studio_setup;

-- Example 2: View tomorrow's setup list
-- SELECT * FROM v_tomorrow_studio_setup;

-- Example 3: View this week's schedule
-- SELECT * FROM v_weekly_studio_schedule;

-- Example 4: View today's summary
-- SELECT * FROM v_studio_setup_summary;

-- Example 5: Check what backdrops are needed today
-- SELECT DISTINCT backdrop_name, backdrop_color 
-- FROM v_today_studio_setup 
-- WHERE backdrop_name IS NOT NULL;

-- Example 6: Count sessions by time slot
-- SELECT booking_time, COUNT(*) as sessions
-- FROM v_today_studio_setup
-- GROUP BY booking_time
-- ORDER BY booking_time;


-- ============================================================================
-- 7. SECURITY VERIFICATION
-- ============================================================================

-- Verify that sensitive columns are NOT in the view
-- This query should return 0 rows if security is correct
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'v_today_studio_setup'
  AND column_name IN (
      'customer_name',
      'email',
      'phone',
      'total_price',
      'payment_method',
      'payment_proof',
      'birthday',
      'voucher_code',
      'base_price',
      'pet_count'
  );

-- If the above query returns 0 rows, security is correct!


-- ============================================================================
-- 8. GRANT PERMISSIONS (Optional - for restricted staff access)
-- ============================================================================

-- If you want to create a staff-only database user:
-- CREATE USER studio_staff WITH PASSWORD 'secure_password';

-- Grant SELECT only on the views (no access to base tables)
-- GRANT SELECT ON v_today_studio_setup TO studio_staff;
-- GRANT SELECT ON v_tomorrow_studio_setup TO studio_staff;
-- GRANT SELECT ON v_weekly_studio_schedule TO studio_staff;
-- GRANT SELECT ON v_studio_setup_summary TO studio_staff;

-- Staff user can now query views but cannot see sensitive data!


-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Views are READ-ONLY - they do not modify data
-- 2. Views are automatically updated when base tables change
-- 3. No impact on existing database structure or data
-- 4. No impact on existing application functionality
-- 5. Can be dropped at any time without affecting base tables
-- 6. Performance: Views execute queries in real-time (no storage overhead)
-- ============================================================================
