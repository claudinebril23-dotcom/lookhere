-- ============================================================================
-- PHOTOBOOTH BOOKING SYSTEM - STORED PROCEDURES AND TRIGGERS
-- ============================================================================
-- Purpose: Manage booking schedule without immediate payment
-- Focus: Prevent double bookings and enforce daily booking limits
-- ============================================================================

-- ============================================================================
-- 1. STORED PROCEDURE: confirm_booking_slot
-- ============================================================================
-- Purpose: Confirm a pending booking if daily limit is not exceeded
-- Logic: Similar to "Over-enrollment" check (Handout page 38)
-- ============================================================================

CREATE OR REPLACE FUNCTION confirm_booking_slot(
    p_booking_id INTEGER
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    booking_ref VARCHAR(50)
) AS $$
DECLARE
    v_booking_date DATE;
    v_booking_status VARCHAR(20);
    v_booking_ref VARCHAR(50);
    v_current_confirmed_count INTEGER;
    v_max_daily_bookings INTEGER;
BEGIN
    -- Get booking details
    SELECT date, status, reference_code
    INTO v_booking_date, v_booking_status, v_booking_ref
    FROM bookings_booking
    WHERE id = p_booking_id;

    -- Check if booking exists
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Booking not found'::TEXT, NULL::VARCHAR(50);
        RETURN;
    END IF;

    -- Check if booking is already confirmed
    IF v_booking_status = 'confirmed' THEN
        RETURN QUERY SELECT FALSE, 
            'Booking is already confirmed'::TEXT, 
            v_booking_ref;
        RETURN;
    END IF;

    -- Check if booking is pending
    IF v_booking_status != 'pending' THEN
        RETURN QUERY SELECT FALSE, 
            format('Cannot confirm booking with status: %s', v_booking_status)::TEXT,
            v_booking_ref;
        RETURN;
    END IF;

    -- Get max daily bookings from site settings
    SELECT max_daily_bookings
    INTO v_max_daily_bookings
    FROM bookings_sitesettings
    LIMIT 1;

    -- Default to 10 if not set
    IF v_max_daily_bookings IS NULL THEN
        v_max_daily_bookings := 10;
    END IF;

    -- Count confirmed bookings for the same date
    -- (Similar to checking enrollment capacity - Handout page 38)
    SELECT COUNT(*)
    INTO v_current_confirmed_count
    FROM bookings_booking
    WHERE date = v_booking_date
      AND status = 'confirmed'
      AND id != p_booking_id;

    -- Check if daily limit would be exceeded (Over-enrollment logic)
    IF v_current_confirmed_count >= v_max_daily_bookings THEN
        RETURN QUERY SELECT FALSE,
            format('Cannot confirm: Daily booking limit reached (%s/%s bookings on %s)',
                   v_current_confirmed_count, v_max_daily_bookings, v_booking_date)::TEXT,
            v_booking_ref;
        RETURN;
    END IF;

    -- All checks passed - confirm the booking
    UPDATE bookings_booking
    SET status = 'confirmed',
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_booking_id;

    -- Return success
    RETURN QUERY SELECT TRUE,
        format('Booking confirmed successfully (%s/%s slots used on %s)',
               v_current_confirmed_count + 1, v_max_daily_bookings, v_booking_date)::TEXT,
        v_booking_ref;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USAGE EXAMPLE:
-- SELECT * FROM confirm_booking_slot(1);
-- ============================================================================


-- ============================================================================
-- 2. TRIGGER FUNCTION: prevent_double_booking
-- ============================================================================
-- Purpose: Prevent inserting bookings at same date/time as confirmed bookings
-- Logic: Similar to validation constraints (Handout page 21)
-- ============================================================================

CREATE OR REPLACE FUNCTION trg_prevent_double_booking_func()
RETURNS TRIGGER AS $$
DECLARE
    v_existing_booking_ref VARCHAR(50);
    v_existing_customer VARCHAR(255);
BEGIN
    -- Check if there's already a CONFIRMED booking at this date and time
    -- (Validation logic - Handout page 21)
    SELECT reference_code, customer_name
    INTO v_existing_booking_ref, v_existing_customer
    FROM bookings_booking
    WHERE date = NEW.date
      AND time = NEW.time
      AND status = 'confirmed'
      AND id != COALESCE(NEW.id, -1)  -- Exclude current booking if updating
    LIMIT 1;

    -- If a confirmed booking exists, prevent the insert/update
    IF FOUND THEN
        RAISE EXCEPTION 'DOUBLE_BOOKING_ERROR: Time slot % on % is already confirmed (Booking: %, Customer: %). Please choose a different time slot.',
            NEW.time,
            NEW.date,
            v_existing_booking_ref,
            v_existing_customer
        USING HINT = 'Check available time slots or confirm a different booking first';
    END IF;

    -- Allow the operation
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 3. CREATE TRIGGER: trg_prevent_double_booking
-- ============================================================================
-- Fires BEFORE INSERT or UPDATE on bookings_booking table
-- ============================================================================

DROP TRIGGER IF EXISTS trg_prevent_double_booking ON bookings_booking;

CREATE TRIGGER trg_prevent_double_booking
    BEFORE INSERT OR UPDATE OF date, time, status
    ON bookings_booking
    FOR EACH ROW
    WHEN (NEW.status = 'confirmed')  -- Only check when confirming
    EXECUTE FUNCTION trg_prevent_double_booking_func();

-- ============================================================================
-- TRIGGER EXPLANATION:
-- - Fires BEFORE INSERT or UPDATE
-- - Only when status is 'confirmed'
-- - Checks if date/time slot is already taken by another confirmed booking
-- - Raises exception to prevent double booking
-- ============================================================================


-- ============================================================================
-- 4. HELPER FUNCTION: get_daily_booking_status
-- ============================================================================
-- Purpose: Check booking availability for a specific date
-- ============================================================================

CREATE OR REPLACE FUNCTION get_daily_booking_status(p_date DATE)
RETURNS TABLE(
    booking_date DATE,
    confirmed_count INTEGER,
    pending_count INTEGER,
    max_bookings INTEGER,
    available_slots INTEGER,
    is_full BOOLEAN
) AS $$
DECLARE
    v_confirmed INTEGER;
    v_pending INTEGER;
    v_max INTEGER;
BEGIN
    -- Get max daily bookings
    SELECT max_daily_bookings INTO v_max
    FROM bookings_sitesettings
    LIMIT 1;
    
    IF v_max IS NULL THEN
        v_max := 10;
    END IF;

    -- Count confirmed bookings
    SELECT COUNT(*) INTO v_confirmed
    FROM bookings_booking
    WHERE date = p_date AND status = 'confirmed';

    -- Count pending bookings
    SELECT COUNT(*) INTO v_pending
    FROM bookings_booking
    WHERE date = p_date AND status = 'pending';

    -- Return status
    RETURN QUERY SELECT
        p_date,
        v_confirmed,
        v_pending,
        v_max,
        GREATEST(0, v_max - v_confirmed),
        (v_confirmed >= v_max);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USAGE EXAMPLE:
-- SELECT * FROM get_daily_booking_status('2026-05-20');
-- ============================================================================


-- ============================================================================
-- 5. HELPER FUNCTION: get_available_time_slots
-- ============================================================================
-- Purpose: Get all available (non-confirmed) time slots for a date
-- ============================================================================

CREATE OR REPLACE FUNCTION get_available_time_slots(p_date DATE)
RETURNS TABLE(
    time_slot TIME,
    is_available BOOLEAN,
    booking_status VARCHAR(20),
    customer_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.time as time_slot,
        CASE 
            WHEN b.status = 'confirmed' THEN FALSE
            ELSE TRUE
        END as is_available,
        b.status as booking_status,
        b.customer_name
    FROM bookings_booking b
    WHERE b.date = p_date
    ORDER BY b.time;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USAGE EXAMPLE:
-- SELECT * FROM get_available_time_slots('2026-05-20');
-- ============================================================================


-- ============================================================================
-- 6. VERIFICATION QUERIES
-- ============================================================================

-- Check if functions were created successfully
SELECT 
    routine_name,
    routine_type,
    data_type as return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name IN (
      'confirm_booking_slot',
      'trg_prevent_double_booking_func',
      'get_daily_booking_status',
      'get_available_time_slots'
  )
ORDER BY routine_name;

-- Check if trigger was created successfully
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE trigger_name = 'trg_prevent_double_booking';

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

-- ============================================================================
-- TESTING EXAMPLES
-- ============================================================================

-- Example 1: Check daily booking status
-- SELECT * FROM get_daily_booking_status('2026-05-18');

-- Example 2: Confirm a pending booking
-- SELECT * FROM confirm_booking_slot(1);

-- Example 3: Try to confirm when limit is reached (should fail)
-- SELECT * FROM confirm_booking_slot(999);

-- Example 4: Try to create double booking (should fail with trigger)
-- INSERT INTO bookings_booking (date, time, status, customer_name, email, phone, package_id, total_price, reference_code)
-- VALUES ('2026-05-18', '10:00:00', 'confirmed', 'Test User', 'test@test.com', '1234567890', 1, 299.00, 'TEST-12345');

-- ============================================================================
