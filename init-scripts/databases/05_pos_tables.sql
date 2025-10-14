-- =====================================================
-- EuroStyle Fashion - POS Database Schema
-- =====================================================
-- Point of Sale system for EuroStyle Fashion retail stores
-- Handles in-store transactions, payments, and store operations
--
-- Author: EuroStyle Fashion Data Team
-- Version: 2.0
-- Date: 2024-10-14
-- =====================================================

-- Use POS database
-- Note: Database should be created by master init script

-- =====================================================
-- 1. POS TRANSACTIONS TABLE
-- =====================================================
-- Main transaction header for all in-store purchases
CREATE TABLE IF NOT EXISTS eurostyle_pos.transactions (
    transaction_id String,             -- TXN_STORE001_20241014_000001
    store_id String,                   -- FK to operational.stores
    register_id String,                -- REG_001, REG_002, etc.
    employee_id String,                -- FK to hr.employees (cashier)
    
    -- Transaction timing
    transaction_date Date,
    transaction_datetime DateTime,
    business_date Date,                -- Accounting date (can differ from transaction date)
    
    -- Customer information (optional)
    customer_id Nullable(String),      -- FK to operational.customers (if loyalty member)
    customer_phone Nullable(String),   -- Phone lookup for returns
    customer_email Nullable(String),   -- Email receipt
    
    -- Financial summary
    subtotal_eur Decimal64(2),          -- Before tax, discounts
    tax_amount_eur Decimal64(2),        -- Total VAT/tax
    discount_amount_eur Decimal64(2),   -- Total discounts applied
    total_amount_eur Decimal64(2),      -- Final amount charged
    
    -- Transaction details
    item_count UInt16,                  -- Number of items in transaction
    transaction_type String,            -- SALE, RETURN, EXCHANGE, VOID
    transaction_status String,          -- PENDING, COMPLETED, CANCELLED, VOIDED
    
    -- Payment information
    payment_method String,              -- CASH, CARD, CONTACTLESS, MOBILE, MIXED
    payment_status String,              -- COMPLETED, PENDING, FAILED, REFUNDED
    change_amount_eur Nullable(Decimal64(2)), -- Cash change given
    
    -- Operational data
    receipt_number String,              -- Printed receipt number
    pos_sequence_number UInt32,         -- Sequential number for the day/register
    training_mode Bool DEFAULT false,   -- Training transaction flag
    
    -- Returns/exchanges
    original_transaction_id Nullable(String), -- For returns/exchanges
    return_reason Nullable(String),     -- Reason for return
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (store_id, transaction_date, transaction_id);

-- =====================================================
-- 2. TRANSACTION ITEMS TABLE
-- =====================================================
-- Individual items within each transaction
CREATE TABLE IF NOT EXISTS eurostyle_pos.transaction_items (
    item_id String,                     -- Generated unique ID
    transaction_id String,              -- FK to transactions
    line_number UInt8,                  -- Order within transaction (1, 2, 3...)
    
    -- Product information
    product_id String,                  -- FK to operational.products
    product_sku String,                 -- Barcode/SKU scanned
    product_name String,                -- Name at time of sale
    size String,                        -- Size selected
    color String,                       -- Color selected
    
    -- Pricing and quantities
    quantity Int8,                      -- Can be negative for returns
    unit_price_eur Decimal64(2),        -- Price per item (after item-level discounts)
    line_total_eur Decimal64(2),        -- quantity * unit_price_eur
    regular_price_eur Decimal64(2),     -- Original price before discounts
    
    -- Discounts and promotions
    discount_amount_eur Decimal64(2),   -- Total discount on this line
    discount_reason String,             -- PROMOTION, EMPLOYEE, CLEARANCE, DAMAGE
    promotion_id Nullable(String),     -- FK to operational.campaigns
    
    -- Tax information
    tax_rate Decimal64(4),              -- VAT rate applied (0.21 for NL, 0.19 for DE, etc.)
    tax_amount_eur Decimal64(2),        -- Tax on this line item
    
    -- Inventory impact
    inventory_adjustment Bool,          -- Whether this affects inventory counts
    
    -- Returns/exchanges
    return_reason Nullable(String),     -- If this is a returned item
    original_item_id Nullable(String),  -- Original item being returned
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (transaction_id, line_number);

-- =====================================================
-- 3. PAYMENTS TABLE
-- =====================================================
-- Detailed payment information (supports split payments)
CREATE TABLE IF NOT EXISTS eurostyle_pos.payments (
    payment_id String,                  -- PAY_TXN123_001, PAY_TXN123_002
    transaction_id String,              -- FK to transactions
    payment_sequence UInt8,             -- 1, 2, 3 for split payments
    
    -- Payment method details
    payment_method String,              -- CASH, VISA, MASTERCARD, AMEX, CONTACTLESS, MOBILE_PAY
    payment_type String,                -- CARD, CASH, DIGITAL_WALLET, VOUCHER
    amount_eur Decimal64(2),            -- Amount for this payment method
    
    -- Card payment details
    card_type Nullable(String),         -- DEBIT, CREDIT
    card_last_four Nullable(String),    -- Last 4 digits for receipts
    authorization_code Nullable(String), -- Card authorization code
    transaction_ref Nullable(String),   -- Payment processor reference
    
    -- Cash payment details
    cash_tendered_eur Nullable(Decimal64(2)), -- Cash amount given by customer
    change_due_eur Nullable(Decimal64(2)),     -- Change returned
    
    -- Payment status
    payment_status String,              -- APPROVED, DECLINED, PENDING, VOIDED, REFUNDED
    processor_response Nullable(String), -- Response from payment processor
    
    -- Timestamps
    payment_timestamp DateTime,
    authorization_timestamp Nullable(DateTime),
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (transaction_id, payment_sequence);

-- =====================================================
-- 4. DISCOUNTS TABLE
-- =====================================================
-- Track all discounts and promotions applied
CREATE TABLE IF NOT EXISTS eurostyle_pos.discounts (
    discount_id String,                 -- DISC_TXN123_001
    transaction_id String,              -- FK to transactions
    item_id Nullable(String),           -- FK to transaction_items (null for transaction-level discounts)
    
    -- Discount details
    discount_type String,               -- PERCENTAGE, FIXED_AMOUNT, BOGO, EMPLOYEE, LOYALTY
    discount_name String,               -- "Staff Discount", "Buy 2 Get 1 Free", etc.
    discount_code Nullable(String),     -- Promotion code if applicable
    promotion_id Nullable(String),      -- FK to operational.campaigns
    
    -- Discount calculation
    discount_percentage Nullable(Decimal64(2)), -- For percentage discounts
    discount_amount_eur Decimal64(2),   -- Final discount amount
    original_amount_eur Decimal64(2),   -- Amount before discount
    final_amount_eur Decimal64(2),      -- Amount after discount
    
    -- Authorization
    authorized_by String,               -- Employee ID who authorized discount
    authorization_code Nullable(String), -- Manager override code if needed
    discount_reason String,             -- PROMOTION, PRICE_MATCH, DAMAGE, CLEARANCE
    
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (transaction_id, discount_id);

-- =====================================================
-- 5. EMPLOYEE ASSIGNMENTS TABLE
-- =====================================================
-- Track which employees work at which stores and registers
CREATE TABLE IF NOT EXISTS eurostyle_pos.employee_assignments (
    assignment_id String,               -- ASSIGN_EMP123_STORE001
    employee_id String,                 -- FK to hr.employees
    store_id String,                    -- FK to operational.stores
    
    -- Assignment details
    assignment_type String,             -- PERMANENT, TEMPORARY, RELIEF
    role String,                        -- CASHIER, SUPERVISOR, MANAGER
    register_access Array(String),      -- Which registers employee can use
    
    -- Authorization levels
    discount_limit_eur Decimal64(2),    -- Maximum discount employee can authorize
    void_authorization Bool,            -- Can void transactions
    refund_authorization Bool,          -- Can process refunds
    training_mode Bool,                 -- Employee in training
    
    -- Assignment period
    start_date Date,
    end_date Nullable(Date),
    is_active Bool DEFAULT true,
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (employee_id, store_id, start_date);

-- =====================================================
-- 6. EMPLOYEE SHIFTS TABLE
-- =====================================================
-- Track employee work shifts and register assignments
CREATE TABLE IF NOT EXISTS eurostyle_pos.employee_shifts (
    shift_id String,                    -- SHIFT_20241014_EMP123_STORE001
    employee_id String,                 -- FK to hr.employees
    store_id String,                    -- FK to operational.stores
    register_id String,                 -- REG_001, REG_002
    
    -- Shift timing
    shift_date Date,
    clock_in_time DateTime,
    clock_out_time Nullable(DateTime),
    break_start Nullable(DateTime),
    break_end Nullable(DateTime),
    
    -- Shift performance
    transactions_processed UInt32,
    total_sales_eur Decimal64(2),
    average_transaction_time_seconds UInt32,
    
    -- Cash drawer management
    opening_cash_eur Decimal64(2),
    closing_cash_eur Nullable(Decimal64(2)),
    cash_variance_eur Nullable(Decimal64(2)), -- Difference from expected
    
    -- Shift status
    shift_status String,                -- ACTIVE, COMPLETED, ABANDONED
    notes Nullable(String),             -- Shift notes or issues
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (store_id, shift_date, employee_id);

-- =====================================================
-- 7. PROMOTIONS TABLE (POS-specific)
-- =====================================================
-- Store-level promotions and campaigns
CREATE TABLE IF NOT EXISTS eurostyle_pos.promotions (
    promotion_id String,                -- PROMO_STORE_2024_WINTER_001
    promotion_name String,              -- "Winter Clearance", "Staff Appreciation Day"
    promotion_type String,              -- PERCENTAGE, FIXED_AMOUNT, BOGO, LOYALTY_POINTS
    
    -- Promotion rules
    discount_percentage Nullable(Decimal64(2)), -- For percentage discounts
    discount_amount_eur Nullable(Decimal64(2)), -- For fixed amount discounts
    minimum_purchase_eur Nullable(Decimal64(2)), -- Minimum purchase required
    
    -- Product targeting
    applicable_products Array(String),   -- Product IDs or categories
    excluded_products Array(String),     -- Products excluded from promotion
    
    -- Store and timing restrictions
    applicable_stores Array(String),     -- Store IDs where valid
    start_date Date,
    end_date Date,
    start_time Nullable(String),         -- Daily start time (e.g., "09:00")
    end_time Nullable(String),           -- Daily end time (e.g., "21:00")
    
    -- Usage limits
    max_uses_per_transaction Nullable(UInt8), -- Limit per transaction
    max_uses_per_customer Nullable(UInt16),   -- Limit per customer
    total_usage_limit Nullable(UInt32),       -- Total uses allowed
    current_usage_count UInt32 DEFAULT 0,     -- Current usage count
    
    -- Authorization
    requires_manager_approval Bool DEFAULT false,
    authorized_by String,               -- Employee who created/approved
    
    -- Status
    is_active Bool DEFAULT true,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (promotion_id, start_date);

-- =====================================================
-- 8. STORE DAILY SUMMARIES TABLE
-- =====================================================
-- Daily operational summaries for each store
CREATE TABLE IF NOT EXISTS eurostyle_pos.store_daily_summaries (
    summary_id String,                  -- SUM_STORE001_20241014
    store_id String,                    -- FK to operational.stores
    business_date Date,
    
    -- Transaction summary
    total_transactions UInt32,
    total_items_sold UInt32,
    total_customers UInt32,             -- Unique customers served
    
    -- Financial summary
    gross_sales_eur Decimal64(2),       -- Total before discounts/returns
    discounts_eur Decimal64(2),         -- Total discounts given
    returns_eur Decimal64(2),           -- Total returns processed  
    net_sales_eur Decimal64(2),         -- Final sales amount
    tax_collected_eur Decimal64(2),     -- Total tax collected
    
    -- Payment method breakdown
    cash_sales_eur Decimal64(2),
    card_sales_eur Decimal64(2),
    contactless_sales_eur Decimal64(2),
    mobile_payment_sales_eur Decimal64(2),
    
    -- Operational metrics
    average_transaction_value_eur Decimal64(2),
    items_per_transaction Decimal32(2),
    transactions_per_hour Decimal32(2),
    
    -- Staff metrics
    staff_hours_worked Decimal32(2),
    sales_per_staff_hour_eur Decimal64(2),
    
    -- Cash drawer variance
    expected_cash_eur Decimal64(2),
    actual_cash_eur Decimal64(2),
    cash_variance_eur Decimal64(2),
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (store_id, business_date);

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT '🎉 POS Database Schema Created Successfully!' as message FORMAT Pretty;
SELECT 'Created 8 POS tables:' as status FORMAT Pretty;
SELECT '  • transactions - Main transaction records' as tables FORMAT Pretty;
SELECT '  • transaction_items - Individual items sold' as tables FORMAT Pretty;
SELECT '  • payments - Payment method details' as tables FORMAT Pretty;
SELECT '  • discounts - Discount and promotion tracking' as tables FORMAT Pretty;
SELECT '  • employee_assignments - Staff store assignments' as tables FORMAT Pretty;
SELECT '  • employee_shifts - Work shift tracking' as tables FORMAT Pretty;
SELECT '  • promotions - Store-level promotions' as tables FORMAT Pretty;
SELECT '  • store_daily_summaries - Daily operational summaries' as tables FORMAT Pretty;

SELECT 'POS database ready for retail operations! 🏪' as completion FORMAT Pretty;