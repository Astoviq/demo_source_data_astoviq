-- =====================================================
-- EuroStyle Fashion - Cross-Database Analytical Views
-- =====================================================
-- Creates views that span across multiple databases to provide
-- comprehensive business intelligence and unified reporting
--
-- Author: EuroStyle Fashion Data Team
-- Version: 2.0
-- Date: 2024-10-14
-- =====================================================

SELECT 'Creating cross-database analytical views...' as status FORMAT Pretty;

-- =====================================================
-- 1. UNIFIED CUSTOMER VIEW
-- =====================================================
-- Combines customer data from operational and webshop databases
CREATE OR REPLACE VIEW eurostyle_operational.customer_360_view AS
SELECT 
    -- Customer basics from operational
    o.customer_id,
    o.email,
    o.first_name,
    o.last_name,
    o.country_code,
    o.registration_date,
    o.customer_status,
    o.loyalty_tier,
    o.total_orders as operational_orders,
    o.total_spent as operational_spent_eur,
    o.last_order_date as last_operational_order,
    
    -- Webshop behavior (aggregated)
    COUNT(DISTINCT ws.session_id) as web_sessions_count,
    COUNT(DISTINCT pv.page_view_id) as total_page_views,
    COUNT(DISTINCT pr.review_id) as product_reviews_written,
    COUNT(DISTINCT wl.wishlist_item_id) as wishlist_items_count,
    
    -- Engagement metrics
    MAX(ws.session_start) as last_web_activity,
    AVG(ws.session_duration_seconds) as avg_session_duration_sec,
    SUM(CASE WHEN ws.conversion_session = true THEN 1 ELSE 0 END) as conversion_sessions,
    
    -- Cross-channel behavior
    CASE 
        WHEN o.total_orders > 0 AND COUNT(DISTINCT ws.session_id) > 0 THEN 'OMNICHANNEL'
        WHEN o.total_orders > 0 THEN 'STORE_ONLY'
        WHEN COUNT(DISTINCT ws.session_id) > 0 THEN 'WEB_ONLY'
        ELSE 'INACTIVE'
    END as customer_type,
    
    -- Recency, Frequency, Monetary scores
    dateDiff('day', o.last_order_date, today()) as days_since_last_order,
    CASE 
        WHEN dateDiff('day', o.last_order_date, today()) <= 30 THEN 'ACTIVE'
        WHEN dateDiff('day', o.last_order_date, today()) <= 90 THEN 'LAPSING' 
        WHEN dateDiff('day', o.last_order_date, today()) <= 365 THEN 'INACTIVE'
        ELSE 'CHURNED'
    END as customer_lifecycle_stage

FROM eurostyle_operational.customers o
LEFT JOIN eurostyle_webshop.web_sessions ws ON o.customer_id = ws.customer_id
LEFT JOIN eurostyle_webshop.page_views pv ON o.customer_id = pv.customer_id
LEFT JOIN eurostyle_webshop.product_reviews pr ON o.customer_id = pr.customer_id
LEFT JOIN eurostyle_webshop.wishlist_items wl ON o.customer_id = wl.customer_id
GROUP BY 
    o.customer_id, o.email, o.first_name, o.last_name, o.country_code, 
    o.registration_date, o.customer_status, o.loyalty_tier,
    o.total_orders, o.total_spent, o.last_order_date;

-- =====================================================
-- 2. PRODUCT PERFORMANCE VIEW
-- =====================================================
-- Combines product data with sales performance across channels
CREATE OR REPLACE VIEW eurostyle_operational.product_performance_view AS
SELECT 
    -- Product details
    p.product_id,
    p.product_name,
    p.category_l1,
    p.category_l2,
    p.category_l3,
    p.brand,
    p.price_eur,
    p.sustainability_score,
    
    -- Operational sales performance
    COUNT(DISTINCT ol.order_id) as orders_containing_product,
    SUM(ol.quantity) as total_units_sold,
    SUM(ol.total_price_eur) as total_revenue_eur,
    AVG(ol.unit_price_eur) as avg_selling_price_eur,
    
    -- Webshop engagement
    COUNT(DISTINCT pv.session_id) as product_page_sessions,
    COUNT(DISTINCT pv.page_view_id) as product_page_views,
    COUNT(DISTINCT ca.session_id) as sessions_added_to_cart,
    SUM(ca.quantity_after - ca.quantity_before) as cart_additions,
    COUNT(DISTINCT pr.review_id) as customer_reviews,
    AVG(pr.rating) as avg_customer_rating,
    COUNT(DISTINCT wl.customer_id) as wishlisted_by_customers,
    
    -- Conversion metrics
    COUNT(DISTINCT ca.session_id) / COUNT(DISTINCT pv.session_id) * 100 as cart_conversion_rate,
    COUNT(DISTINCT ol.order_id) / COUNT(DISTINCT pv.session_id) * 100 as purchase_conversion_rate,
    
    -- Inventory status
    p.current_stock_total,
    CASE 
        WHEN p.current_stock_total = 0 THEN 'OUT_OF_STOCK'
        WHEN p.current_stock_total <= p.reorder_level THEN 'LOW_STOCK'
        ELSE 'IN_STOCK'
    END as stock_status,
    
    -- Performance categorization
    CASE 
        WHEN total_revenue_eur >= 10000 THEN 'HIGH_PERFORMER'
        WHEN total_revenue_eur >= 5000 THEN 'MEDIUM_PERFORMER'
        WHEN total_revenue_eur >= 1000 THEN 'LOW_PERFORMER'
        ELSE 'UNDERPERFORMER'
    END as performance_tier

FROM eurostyle_operational.products p
LEFT JOIN eurostyle_operational.order_lines ol ON p.product_id = ol.product_id
LEFT JOIN eurostyle_webshop.page_views pv ON p.product_id = pv.product_id
LEFT JOIN eurostyle_webshop.cart_activities ca ON p.product_id = ca.product_id
LEFT JOIN eurostyle_webshop.product_reviews pr ON p.product_id = pr.product_id  
LEFT JOIN eurostyle_webshop.wishlist_items wl ON p.product_id = wl.product_id
WHERE p.is_active = true
GROUP BY 
    p.product_id, p.product_name, p.category_l1, p.category_l2, p.category_l3,
    p.brand, p.price_eur, p.sustainability_score, p.current_stock_total, p.reorder_level;

-- =====================================================
-- 3. STORE PERFORMANCE DASHBOARD VIEW
-- =====================================================
-- Comprehensive store performance metrics
CREATE OR REPLACE VIEW eurostyle_operational.store_dashboard_view AS
SELECT 
    -- Store details
    s.store_id,
    s.store_name,
    s.country_code,
    s.city,
    s.store_format,
    s.performance_tier,
    
    -- Operational metrics (last 30 days)
    COUNT(DISTINCT o.order_id) as orders_last_30d,
    COUNT(DISTINCT o.customer_id) as unique_customers_last_30d,
    SUM(o.total_amount_eur) as revenue_last_30d,
    AVG(o.total_amount_eur) as avg_order_value_last_30d,
    
    -- Year-to-date performance
    COUNT(DISTINCT CASE WHEN o.order_date >= date_trunc('year', today()) THEN o.order_id END) as orders_ytd,
    SUM(CASE WHEN o.order_date >= date_trunc('year', today()) THEN o.total_amount_eur ELSE 0 END) as revenue_ytd,
    
    -- Staff metrics
    COUNT(DISTINCT hr.employee_id) as total_staff_count,
    COUNT(DISTINCT CASE WHEN hr.employee_status = 'ACTIVE' THEN hr.employee_id END) as active_staff_count,
    
    -- Performance indicators
    revenue_last_30d / 30 as avg_daily_revenue,
    orders_last_30d / 30 as avg_daily_transactions,
    unique_customers_last_30d / orders_last_30d as customer_retention_ratio,
    
    -- Target achievement
    s.target_monthly_revenue,
    (revenue_last_30d / s.target_monthly_revenue) * 100 as monthly_target_achievement_pct,
    
    -- Store health score (0-100)
    LEAST(100, GREATEST(0, 
        (revenue_last_30d / s.target_monthly_revenue * 40) +
        (CASE WHEN avg_order_value_last_30d >= 75 THEN 20 ELSE avg_order_value_last_30d / 75 * 20 END) +
        (CASE WHEN orders_last_30d >= 100 THEN 20 ELSE orders_last_30d / 100 * 20 END) +
        (CASE WHEN unique_customers_last_30d >= 80 THEN 20 ELSE unique_customers_last_30d / 80 * 20 END)
    )) as store_health_score

FROM eurostyle_operational.stores s
LEFT JOIN eurostyle_operational.orders o ON s.store_id = o.store_id 
    AND o.order_date >= today() - INTERVAL 30 DAY
LEFT JOIN eurostyle_hr.employees hr ON s.store_id = hr.location  
WHERE s.is_active = true
GROUP BY 
    s.store_id, s.store_name, s.country_code, s.city, s.store_format, 
    s.performance_tier, s.target_monthly_revenue;

-- =====================================================
-- 4. FINANCIAL RECONCILIATION VIEW  
-- =====================================================
-- Reconciles operational revenue with finance GL entries
CREATE OR REPLACE VIEW eurostyle_finance.revenue_reconciliation_view AS
SELECT 
    -- Time dimensions
    DATE_TRUNC('month', o.order_date) as month_year,
    o.store_id,
    s.country_code,
    
    -- Operational revenue (source of truth)
    SUM(o.total_amount_eur) as operational_revenue_eur,
    SUM(o.tax_amount_eur) as operational_tax_eur,
    COUNT(DISTINCT o.order_id) as total_orders,
    
    -- Finance GL entries (should match operational)
    COALESCE(SUM(gl.debit_amount_eur - gl.credit_amount_eur), 0) as gl_revenue_eur,
    
    -- Reconciliation
    operational_revenue_eur - gl_revenue_eur as variance_eur,
    ABS(variance_eur) / operational_revenue_eur * 100 as variance_percentage,
    
    -- Status
    CASE 
        WHEN ABS(variance_eur) <= 1.00 THEN 'RECONCILED'
        WHEN ABS(variance_eur) <= operational_revenue_eur * 0.01 THEN 'MINOR_VARIANCE'
        ELSE 'INVESTIGATION_REQUIRED'
    END as reconciliation_status,
    
    -- Entity mapping
    le.entity_code as finance_entity,
    le.entity_name

FROM eurostyle_operational.orders o
JOIN eurostyle_operational.stores s ON o.store_id = s.store_id
LEFT JOIN eurostyle_finance.legal_entities le ON s.country_code = le.country_code
LEFT JOIN eurostyle_finance.gl_journal_lines gl ON le.entity_code = gl.entity_code 
    AND DATE_TRUNC('month', gl.transaction_date) = DATE_TRUNC('month', o.order_date)
    AND gl.account_code LIKE '4%' -- Revenue accounts typically start with 4
WHERE o.order_status = 'delivered'
GROUP BY 
    DATE_TRUNC('month', o.order_date), o.store_id, s.country_code, 
    le.entity_code, le.entity_name
HAVING operational_revenue_eur > 0
ORDER BY month_year DESC, operational_revenue_eur DESC;

-- =====================================================
-- 5. EMPLOYEE PERFORMANCE VIEW
-- =====================================================  
-- HR and operational performance metrics for staff
CREATE OR REPLACE VIEW eurostyle_hr.employee_performance_view AS
SELECT 
    -- Employee details
    e.employee_id,
    e.first_name,
    e.last_name,
    e.email,
    e.employee_status,
    e.location as store_id,
    s.store_name,
    jp.position_title,
    jp.position_level,
    
    -- Employment details
    e.hire_date,
    DATEDIFF('day', e.hire_date, today()) as tenure_days,
    ec.contract_type,
    ch.current_annual_salary_eur,
    
    -- Performance metrics
    AVG(pr.overall_score) as avg_performance_score,
    COUNT(pr.review_id) as total_reviews,
    MAX(pr.created_date) as last_review_date,
    
    -- Leave and attendance
    SUM(CASE WHEN lr.leave_status = 'APPROVED' THEN lr.days_requested ELSE 0 END) as total_leave_days,
    COUNT(DISTINCT lr.request_id) as leave_requests_count,
    
    -- Training and development
    COUNT(DISTINCT et.program_id) as training_programs_completed,
    MAX(et.completion_date) as last_training_date,
    
    -- Compensation progression
    COUNT(DISTINCT ch.change_id) as salary_changes,
    (ch.current_annual_salary_eur - ch_first.annual_salary_eur) / ch_first.annual_salary_eur * 100 as salary_growth_pct,
    
    -- Employee lifecycle
    CASE 
        WHEN e.employee_status = 'ACTIVE' AND tenure_days <= 90 THEN 'NEW_HIRE'
        WHEN e.employee_status = 'ACTIVE' AND avg_performance_score >= 4.0 THEN 'HIGH_PERFORMER'
        WHEN e.employee_status = 'ACTIVE' AND avg_performance_score >= 3.0 THEN 'SOLID_PERFORMER'
        WHEN e.employee_status = 'ACTIVE' THEN 'NEEDS_IMPROVEMENT'
        ELSE 'INACTIVE'
    END as performance_category

FROM eurostyle_hr.employees e
LEFT JOIN eurostyle_operational.stores s ON e.location = s.store_id
LEFT JOIN eurostyle_hr.employment_contracts ec ON e.employee_id = ec.employee_id AND ec.is_active = true
LEFT JOIN eurostyle_hr.job_positions jp ON ec.position_id = jp.position_id
LEFT JOIN eurostyle_hr.compensation_history ch ON e.employee_id = ch.employee_id AND ch.is_current = true
LEFT JOIN eurostyle_hr.compensation_history ch_first ON e.employee_id = ch_first.employee_id 
    AND ch_first.effective_date = (SELECT MIN(effective_date) FROM eurostyle_hr.compensation_history WHERE employee_id = e.employee_id)
LEFT JOIN eurostyle_hr.performance_reviews pr ON e.employee_id = pr.employee_id
LEFT JOIN eurostyle_hr.leave_requests lr ON e.employee_id = lr.employee_id
LEFT JOIN eurostyle_hr.employee_training et ON e.employee_id = et.employee_id AND et.status = 'COMPLETED'
GROUP BY 
    e.employee_id, e.first_name, e.last_name, e.email, e.employee_status,
    e.location, s.store_name, jp.position_title, jp.position_level,
    e.hire_date, ec.contract_type, ch.current_annual_salary_eur, ch_first.annual_salary_eur;

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT '🎉 Cross-Database Views Created Successfully!' as message FORMAT Pretty;
SELECT 'Created 5 analytical views:' as status FORMAT Pretty;
SELECT '  • customer_360_view - Unified customer analytics' as views FORMAT Pretty;
SELECT '  • product_performance_view - Product sales & engagement' as views FORMAT Pretty;
SELECT '  • store_dashboard_view - Store performance metrics' as views FORMAT Pretty;
SELECT '  • revenue_reconciliation_view - Finance-ops reconciliation' as views FORMAT Pretty;
SELECT '  • employee_performance_view - HR performance analytics' as views FORMAT Pretty;

SELECT 'Views provide comprehensive cross-database business intelligence! 📊' as completion FORMAT Pretty;