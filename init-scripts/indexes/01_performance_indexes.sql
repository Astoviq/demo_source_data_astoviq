-- =====================================================
-- EuroStyle Fashion - Performance Indexes
-- =====================================================
-- Creates additional indexes to optimize query performance
-- across all databases for common analytical queries
--
-- Author: EuroStyle Fashion Data Team
-- Version: 2.0
-- Date: 2024-10-14
-- =====================================================

SELECT 'Creating performance indexes for optimal query performance...' as status FORMAT Pretty;

-- =====================================================
-- OPERATIONAL DATABASE INDEXES
-- =====================================================

SELECT 'Creating operational database indexes...' as status FORMAT Pretty;

-- Customer analysis indexes
-- Note: ClickHouse doesn't use traditional CREATE INDEX syntax, 
-- but we can create materialized views for complex aggregations

-- Customer activity summary (materialized view acting as index)
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.customer_activity_mv
(
    customer_id String,
    country_code String,
    total_orders UInt32,
    total_spent_eur Decimal64(2),
    last_order_date Date,
    avg_order_value Decimal64(2),
    days_since_last_order UInt32,
    customer_lifetime_value Decimal64(2)
) ENGINE = SummingMergeTree()
ORDER BY (country_code, customer_id)
AS SELECT 
    customer_id,
    country_code,
    COUNT(*) as total_orders,
    SUM(total_amount_eur) as total_spent_eur,
    MAX(order_date) as last_order_date,
    AVG(total_amount_eur) as avg_order_value,
    dateDiff('day', MAX(order_date), today()) as days_since_last_order,
    SUM(total_amount_eur) as customer_lifetime_value
FROM eurostyle_operational.orders
WHERE order_status = 'delivered'
GROUP BY customer_id, country_code;

-- Product performance summary 
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.product_sales_mv
(
    product_id String,
    category_l1 String,
    category_l2 String,
    total_quantity UInt32,
    total_revenue_eur Decimal64(2),
    total_orders UInt32,
    avg_price_eur Decimal64(2),
    last_sale_date Date
) ENGINE = SummingMergeTree()
ORDER BY (category_l1, category_l2, product_id)
AS SELECT 
    ol.product_id,
    p.category_l1,
    p.category_l2,
    SUM(ol.quantity) as total_quantity,
    SUM(ol.total_price_eur) as total_revenue_eur,
    COUNT(DISTINCT ol.order_id) as total_orders,
    AVG(ol.unit_price_eur) as avg_price_eur,
    MAX(o.order_date) as last_sale_date
FROM eurostyle_operational.order_lines ol
JOIN eurostyle_operational.orders o ON ol.order_id = o.order_id
JOIN eurostyle_operational.products p ON ol.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY ol.product_id, p.category_l1, p.category_l2;

-- Store performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.store_performance_mv
(
    store_id String,
    country_code String,
    month_year String,
    total_orders UInt32,
    total_revenue_eur Decimal64(2),
    unique_customers UInt32,
    avg_order_value Decimal64(2)
) ENGINE = SummingMergeTree()
ORDER BY (country_code, store_id, month_year)
AS SELECT 
    o.store_id,
    s.country_code,
    formatDateTime(o.order_date, '%Y-%m') as month_year,
    COUNT(*) as total_orders,
    SUM(o.total_amount_eur) as total_revenue_eur,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    AVG(o.total_amount_eur) as avg_order_value
FROM eurostyle_operational.orders o
JOIN eurostyle_operational.stores s ON o.store_id = s.store_id
WHERE o.order_status = 'delivered'
GROUP BY o.store_id, s.country_code, formatDateTime(o.order_date, '%Y-%m');

-- =====================================================
-- WEBSHOP DATABASE INDEXES  
-- =====================================================

SELECT 'Creating webshop database indexes...' as status FORMAT Pretty;

-- Session funnel analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_webshop.session_funnel_mv
(
    country_code String,
    date Date,
    total_sessions UInt32,
    sessions_with_product_views UInt32,
    sessions_with_cart_activity UInt32,
    conversion_sessions UInt32,
    bounce_sessions UInt32
) ENGINE = SummingMergeTree()
ORDER BY (country_code, date)
AS SELECT 
    ws.country_code,
    toDate(ws.session_start) as date,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT CASE WHEN pv.session_id IS NOT NULL THEN ws.session_id END) as sessions_with_product_views,
    COUNT(DISTINCT CASE WHEN ca.session_id IS NOT NULL THEN ws.session_id END) as sessions_with_cart_activity,
    SUM(CASE WHEN ws.conversion_session = true THEN 1 ELSE 0 END) as conversion_sessions,
    SUM(CASE WHEN ws.bounce_session = true THEN 1 ELSE 0 END) as bounce_sessions
FROM eurostyle_webshop.web_sessions ws
LEFT JOIN eurostyle_webshop.page_views pv ON ws.session_id = pv.session_id AND pv.product_id != ''
LEFT JOIN eurostyle_webshop.cart_activities ca ON ws.session_id = ca.session_id
GROUP BY ws.country_code, toDate(ws.session_start);

-- Product engagement summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_webshop.product_engagement_mv
(
    product_id String,
    date Date,
    product_page_views UInt32,
    unique_sessions UInt32,
    cart_additions UInt32,
    review_count UInt32,
    avg_rating Decimal32(2),
    wishlist_additions UInt32
) ENGINE = SummingMergeTree()
ORDER BY (product_id, date)
AS SELECT 
    COALESCE(pv.product_id, ca.product_id, pr.product_id, wl.product_id) as product_id,
    COALESCE(toDate(pv.view_timestamp), toDate(ca.activity_timestamp), pr.review_date, toDate(wl.added_date)) as date,
    COUNT(DISTINCT pv.page_view_id) as product_page_views,
    COUNT(DISTINCT COALESCE(pv.session_id, ca.session_id)) as unique_sessions,
    SUM(CASE WHEN ca.activity_type = 'add_to_cart' THEN ca.quantity_after - ca.quantity_before ELSE 0 END) as cart_additions,
    COUNT(DISTINCT pr.review_id) as review_count,
    AVG(pr.rating) as avg_rating,
    COUNT(DISTINCT wl.wishlist_item_id) as wishlist_additions
FROM eurostyle_webshop.page_views pv
FULL OUTER JOIN eurostyle_webshop.cart_activities ca ON pv.product_id = ca.product_id AND toDate(pv.view_timestamp) = toDate(ca.activity_timestamp)
FULL OUTER JOIN eurostyle_webshop.product_reviews pr ON COALESCE(pv.product_id, ca.product_id) = pr.product_id AND toDate(COALESCE(pv.view_timestamp, ca.activity_timestamp)) = pr.review_date
FULL OUTER JOIN eurostyle_webshop.wishlist_items wl ON COALESCE(pv.product_id, ca.product_id, pr.product_id) = wl.product_id AND toDate(COALESCE(pv.view_timestamp, ca.activity_timestamp, pr.review_date)) = toDate(wl.added_date)
WHERE COALESCE(pv.product_id, ca.product_id, pr.product_id, wl.product_id) != ''
GROUP BY COALESCE(pv.product_id, ca.product_id, pr.product_id, wl.product_id), 
         COALESCE(toDate(pv.view_timestamp), toDate(ca.activity_timestamp), pr.review_date, toDate(wl.added_date));

-- =====================================================
-- FINANCE DATABASE INDEXES
-- =====================================================

SELECT 'Creating finance database indexes...' as status FORMAT Pretty;

-- Monthly GL summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_finance.gl_monthly_summary_mv
(
    entity_code String,
    account_code String,
    month_year String,
    total_debits_eur Decimal64(2),
    total_credits_eur Decimal64(2),
    net_amount_eur Decimal64(2),
    transaction_count UInt32
) ENGINE = SummingMergeTree()
ORDER BY (entity_code, account_code, month_year)
AS SELECT 
    entity_code,
    account_code,
    formatDateTime(transaction_date, '%Y-%m') as month_year,
    SUM(debit_amount_eur) as total_debits_eur,
    SUM(credit_amount_eur) as total_credits_eur,
    SUM(debit_amount_eur - credit_amount_eur) as net_amount_eur,
    COUNT(*) as transaction_count
FROM eurostyle_finance.gl_journal_lines
GROUP BY entity_code, account_code, formatDateTime(transaction_date, '%Y-%m');

-- Budget vs Actual summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_finance.budget_actual_mv
(
    entity_code String,
    cost_center_code String,
    account_code String,
    period_year UInt16,
    period_month UInt8,
    budget_amount_eur Decimal64(2),
    actual_amount_eur Decimal64(2),
    variance_eur Decimal64(2),
    variance_percentage Decimal32(2)
) ENGINE = SummingMergeTree()
ORDER BY (entity_code, cost_center_code, period_year, period_month)
AS SELECT 
    bd.entity_code,
    bd.cost_center_code,
    bd.account_code,
    bd.period_year,
    bd.period_month,
    SUM(bd.budget_amount_eur) as budget_amount_eur,
    COALESCE(SUM(gl.debit_amount_eur - gl.credit_amount_eur), 0) as actual_amount_eur,
    budget_amount_eur - actual_amount_eur as variance_eur,
    CASE WHEN budget_amount_eur != 0 THEN (variance_eur / budget_amount_eur) * 100 ELSE 0 END as variance_percentage
FROM eurostyle_finance.budget_data bd
LEFT JOIN eurostyle_finance.gl_journal_lines gl ON 
    bd.entity_code = gl.entity_code AND 
    bd.account_code = gl.account_code AND
    bd.period_year = YEAR(gl.transaction_date) AND
    bd.period_month = MONTH(gl.transaction_date)
GROUP BY bd.entity_code, bd.cost_center_code, bd.account_code, bd.period_year, bd.period_month;

-- =====================================================
-- HR DATABASE INDEXES
-- =====================================================

SELECT 'Creating HR database indexes...' as status FORMAT Pretty;

-- Employee headcount summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_hr.headcount_summary_mv
(
    entity_code String,
    department_code String,
    position_level String,
    month_year String,
    headcount UInt32,
    new_hires UInt32,
    terminations UInt32,
    total_compensation_eur Decimal64(2)
) ENGINE = SummingMergeTree()
ORDER BY (entity_code, department_code, month_year)
AS SELECT 
    e.entity_code,
    d.department_code,
    jp.position_level,
    formatDateTime(today(), '%Y-%m') as month_year, -- Snapshot as of today
    COUNT(*) as headcount,
    SUM(CASE WHEN dateDiff('month', e.hire_date, today()) = 0 THEN 1 ELSE 0 END) as new_hires,
    SUM(CASE WHEN e.employee_status = 'TERMINATED' AND dateDiff('month', e.termination_date, today()) = 0 THEN 1 ELSE 0 END) as terminations,
    SUM(ch.current_annual_salary_eur) as total_compensation_eur
FROM eurostyle_hr.employees e
JOIN eurostyle_hr.departments d ON e.department_id = d.department_id
LEFT JOIN eurostyle_hr.employment_contracts ec ON e.employee_id = ec.employee_id AND ec.is_active = true
LEFT JOIN eurostyle_hr.job_positions jp ON ec.position_id = jp.position_id
LEFT JOIN eurostyle_hr.compensation_history ch ON e.employee_id = ch.employee_id AND ch.is_current = true
GROUP BY e.entity_code, d.department_code, jp.position_level, formatDateTime(today(), '%Y-%m');

-- Leave utilization summary  
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_hr.leave_utilization_mv
(
    entity_code String,
    leave_type String,
    month_year String,
    total_days_requested UInt32,
    total_days_approved UInt32,
    unique_employees UInt32,
    avg_days_per_employee Decimal32(2)
) ENGINE = SummingMergeTree()
ORDER BY (entity_code, leave_type, month_year)
AS SELECT 
    e.entity_code,
    lr.leave_type,
    formatDateTime(lr.start_date, '%Y-%m') as month_year,
    SUM(lr.days_requested) as total_days_requested,
    SUM(CASE WHEN lr.leave_status = 'APPROVED' THEN lr.days_requested ELSE 0 END) as total_days_approved,
    COUNT(DISTINCT lr.employee_id) as unique_employees,
    AVG(lr.days_requested) as avg_days_per_employee
FROM eurostyle_hr.leave_requests lr
JOIN eurostyle_hr.employees e ON lr.employee_id = e.employee_id
GROUP BY e.entity_code, lr.leave_type, formatDateTime(lr.start_date, '%Y-%m');

-- =====================================================
-- POS DATABASE INDEXES
-- =====================================================

SELECT 'Creating POS database indexes...' as status FORMAT Pretty;

-- Daily store performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_pos.daily_store_performance_mv
(
    store_id String,
    business_date Date,
    total_transactions UInt32,
    total_items_sold UInt32,
    gross_sales_eur Decimal64(2),
    net_sales_eur Decimal64(2),
    total_discounts_eur Decimal64(2),
    cash_sales_eur Decimal64(2),
    card_sales_eur Decimal64(2),
    avg_transaction_value_eur Decimal64(2)
) ENGINE = SummingMergeTree()
ORDER BY (store_id, business_date)
AS SELECT 
    t.store_id,
    t.business_date,
    COUNT(*) as total_transactions,
    SUM(t.item_count) as total_items_sold,
    SUM(t.subtotal_eur + t.tax_amount_eur) as gross_sales_eur,
    SUM(t.total_amount_eur) as net_sales_eur,
    SUM(t.discount_amount_eur) as total_discounts_eur,
    SUM(CASE WHEN t.payment_method LIKE '%CASH%' THEN t.total_amount_eur ELSE 0 END) as cash_sales_eur,
    SUM(CASE WHEN t.payment_method LIKE '%CARD%' OR t.payment_method LIKE '%CONTACTLESS%' THEN t.total_amount_eur ELSE 0 END) as card_sales_eur,
    AVG(t.total_amount_eur) as avg_transaction_value_eur
FROM eurostyle_pos.transactions t
WHERE t.transaction_status = 'COMPLETED'
GROUP BY t.store_id, t.business_date;

-- Hourly transaction patterns
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_pos.hourly_patterns_mv
(
    store_id String,
    transaction_date Date,
    transaction_hour UInt8,
    transaction_count UInt32,
    total_sales_eur Decimal64(2),
    avg_transaction_value_eur Decimal64(2)
) ENGINE = SummingMergeTree()
ORDER BY (store_id, transaction_date, transaction_hour)
AS SELECT 
    store_id,
    transaction_date,
    toHour(transaction_datetime) as transaction_hour,
    COUNT(*) as transaction_count,
    SUM(total_amount_eur) as total_sales_eur,
    AVG(total_amount_eur) as avg_transaction_value_eur
FROM eurostyle_pos.transactions
WHERE transaction_status = 'COMPLETED'
GROUP BY store_id, transaction_date, toHour(transaction_datetime);

-- =====================================================
-- CROSS-DATABASE SUMMARY TABLES
-- =====================================================

SELECT 'Creating cross-database summary tables...' as status FORMAT Pretty;

-- Unified daily business summary
CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.daily_business_summary_mv
(
    date Date,
    country_code String,
    -- Operational metrics
    operational_orders UInt32,
    operational_revenue_eur Decimal64(2),
    -- Webshop metrics  
    web_sessions UInt32,
    web_conversions UInt32,
    -- POS metrics
    pos_transactions UInt32,
    pos_revenue_eur Decimal64(2),
    -- Combined metrics
    total_revenue_eur Decimal64(2),
    omnichannel_customers UInt32
) ENGINE = SummingMergeTree()
ORDER BY (country_code, date)
AS SELECT 
    COALESCE(o.order_date, toDate(ws.session_start), pos.business_date) as date,
    COALESCE(s_op.country_code, ws.country_code, s_pos.country_code) as country_code,
    
    -- Operational metrics
    COUNT(DISTINCT o.order_id) as operational_orders,
    SUM(o.total_amount_eur) as operational_revenue_eur,
    
    -- Webshop metrics
    COUNT(DISTINCT ws.session_id) as web_sessions, 
    SUM(CASE WHEN ws.conversion_session = true THEN 1 ELSE 0 END) as web_conversions,
    
    -- POS metrics
    COUNT(DISTINCT pos.transaction_id) as pos_transactions,
    SUM(pos.total_amount_eur) as pos_revenue_eur,
    
    -- Combined metrics
    COALESCE(SUM(o.total_amount_eur), 0) + COALESCE(SUM(pos.total_amount_eur), 0) as total_revenue_eur,
    COUNT(DISTINCT CASE WHEN o.customer_id IS NOT NULL AND ws.customer_id IS NOT NULL THEN COALESCE(o.customer_id, ws.customer_id) END) as omnichannel_customers

FROM eurostyle_operational.orders o
FULL OUTER JOIN eurostyle_operational.stores s_op ON o.store_id = s_op.store_id
FULL OUTER JOIN eurostyle_webshop.web_sessions ws ON o.customer_id = ws.customer_id AND o.order_date = toDate(ws.session_start)
FULL OUTER JOIN eurostyle_pos.transactions pos ON s_op.store_id = pos.store_id AND o.order_date = pos.business_date
FULL OUTER JOIN eurostyle_operational.stores s_pos ON pos.store_id = s_pos.store_id
WHERE COALESCE(o.order_status, 'delivered') = 'delivered' 
  AND COALESCE(pos.transaction_status, 'COMPLETED') = 'COMPLETED'
GROUP BY 
    COALESCE(o.order_date, toDate(ws.session_start), pos.business_date),
    COALESCE(s_op.country_code, ws.country_code, s_pos.country_code);

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT '🎉 Performance Indexes Created Successfully!' as message FORMAT Pretty;
SELECT 'Created materialized views for optimal performance:' as status FORMAT Pretty;
SELECT '  📊 Operational: Customer activity, Product sales, Store performance' as indexes FORMAT Pretty;
SELECT '  🌐 Webshop: Session funnel, Product engagement' as indexes FORMAT Pretty;
SELECT '  🏦 Finance: GL monthly summary, Budget vs actual' as indexes FORMAT Pretty;
SELECT '  👥 HR: Headcount summary, Leave utilization' as indexes FORMAT Pretty;
SELECT '  🏪 POS: Daily performance, Hourly patterns' as indexes FORMAT Pretty;
SELECT '  🔄 Cross-DB: Daily business summary' as indexes FORMAT Pretty;

SELECT 'Materialized views will automatically maintain aggregated data for fast queries! ⚡' as completion FORMAT Pretty;