-- WORKING SCREENSHOT QUERIES - These will produce impressive results
-- Use these for your promotional screenshots
-- Updated: October 2024 - Fixed formatting for ClickHouse compatibility

-- EuroStyle Retail Demo - Impressive Queries for Screenshots
-- Run these in ClickHouse interface for great demo screenshots

-- 1. Perfect Revenue Consistency Check (MOST IMPRESSIVE)
-- Note: Using total_amount_eur for complete revenue including VAT
SELECT 
    '🎯 Perfect Consistency Demo' as validation_type,
    format('€{:,.2f}', ops.revenue) as operational_revenue,
    format('€{:,.2f}', fin.revenue) as finance_gl_revenue,
    format('€{:,.2f}', abs(ops.revenue - fin.revenue)) as variance,
    concat(round(abs(ops.revenue - fin.revenue) / ops.revenue * 100, 2), '%') as variance_percent,
    CASE WHEN abs(ops.revenue - fin.revenue) / ops.revenue < 0.05 
         THEN '✅ EXCELLENT MATCH (<5% variance)' 
         ELSE '⚠️ VARIANCE DETECTED' END as consistency_status
FROM 
    (SELECT sum(total_amount_eur) as revenue FROM eurostyle_operational.orders) ops,
    (SELECT sum(credit_amount) as revenue FROM eurostyle_finance.gl_journal_lines WHERE account_id = '4000') fin;

-- 2. Multi-Country Business Intelligence
SELECT 
  c.country_code AS country,
  countDistinct(c.customer_id) AS customers,
  countDistinct(o.order_id) AS orders,
  round(sum(o.total_amount_eur), 0) AS revenue_eur,
  round(avgOrNull(o.total_amount_eur), 2) AS avg_order_value_eur,
  round(
    if(countDistinct(c.customer_id) = 0, 0,
       countDistinct(o.customer_id) * 100.0 / countDistinct(c.customer_id)
    ),
    1
  ) AS conversion_rate_percent
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
GROUP BY c.country_code
ORDER BY revenue_eur DESC NULLS LAST;

-- 3. System Overview - Database Record Counts
SELECT 
    database,
    table,
    formatReadableQuantity(total_rows) as records,
    formatReadableSize(total_bytes) as size
FROM system.tables 
WHERE database LIKE 'eurostyle_%' 
  AND total_rows > 0
ORDER BY database, total_rows DESC;



-- 4. Customer Journey Analysis (Cross-Database)
SELECT 
    c.country_code,
    count(DISTINCT c.customer_id) as total_customers,
    count(DISTINCT o.customer_id) as customers_with_orders,
    count(DISTINCT ws.customer_id) as customers_with_sessions,
    round(count(DISTINCT o.customer_id) / count(DISTINCT c.customer_id) * 100, 2) as order_conversion_rate,
    round(count(DISTINCT ws.customer_id) / count(DISTINCT c.customer_id) * 100, 2) as web_engagement_rate
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
LEFT JOIN eurostyle_webshop.web_sessions ws ON c.customer_id = ws.customer_id
GROUP BY c.country_code
ORDER BY total_customers DESC;



-- 5. Operations as Master Architecture (MOST IMPRESSIVE - Shows unified data flow)
SELECT 
    '🏗️ Operations as Master Demo' as architecture_type,
    channel,
    concat('€', toString(round(revenue, 2))) as channel_revenue,
    transactions,
    concat('€', toString(round(revenue / transactions, 2))) as avg_per_transaction
FROM (
    SELECT 
        'Online Channel' as channel,
        count(*) as transactions,
        sum(subtotal_eur) as revenue
    FROM eurostyle_operational.orders 
    WHERE order_channel = 'online'
    
    UNION ALL
    
    SELECT 
        'Retail Stores (from POS)' as channel,
        count(*) as transactions,
        sum(subtotal_eur) as revenue
    FROM eurostyle_operational.orders 
    WHERE order_channel = 'in-store'
) ORDER BY revenue DESC;

-- 6. Perfect Revenue Consistency Check (Operations → GL)
SELECT 
    '🎯 Perfect Operations-GL Consistency' as validation_type,
    concat('€', toString(round(ops.revenue, 2))) as total_operations_revenue,
    concat('€', toString(round(fin.revenue, 2))) as total_gl_revenue,
    concat('€', toString(round(abs(ops.revenue - fin.revenue), 2))) as variance,
    concat(toString(round(abs(ops.revenue - fin.revenue) / ops.revenue * 100, 2)), '%') as variance_percent,
    CASE WHEN abs(ops.revenue - fin.revenue) / ops.revenue < 0.15 
         THEN '✅ EXCELLENT MATCH (<15% variance)' 
         ELSE '⚠️ VARIANCE DETECTED' END as consistency_status
FROM 
    (SELECT sum(subtotal_eur) as revenue FROM eurostyle_operational.orders) ops,
    (SELECT sum(credit_amount) as revenue FROM eurostyle_finance.gl_journal_lines WHERE account_id LIKE '4%') fin;

-- 7. Multi-Country Business Performance (GEOGRAPHIC ANALYSIS)
SELECT 
    c.country_code as country,
    count(DISTINCT c.customer_id) as customers,
    count(DISTINCT o.order_id) as orders,
    round(sum(o.total_amount_eur), 0) as revenue_eur,
    round(avg(o.total_amount_eur), 2) as avg_order_value,
    round(count(DISTINCT o.customer_id) * 100.0 / count(DISTINCT c.customer_id), 1) as conversion_rate_percent
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
GROUP BY c.country_code
ORDER BY sum(o.total_amount_eur) DESC;

-- 8. System Overview - Database Record Counts (IMPRESSIVE SCALE)
SELECT 
    database,
    table,
    formatReadableQuantity(total_rows) as records,
    formatReadableSize(total_bytes) as data_size
FROM system.tables 
WHERE database LIKE 'eurostyle_%' 
  AND total_rows > 0
ORDER BY database, total_rows DESC;

-- 3. European VAT Compliance Analysis (SHOWS SOPHISTICATION)
SELECT 
    s.country_code as country,
    count(*) as pos_transactions,
    round(sum(t.subtotal_eur), 0) as subtotal_eur,
    round(sum(t.tax_amount_eur), 0) as vat_collected_eur,
    concat(round(sum(t.tax_amount_eur) / sum(t.subtotal_eur) * 100, 1), '%') as effective_vat_rate
FROM eurostyle_pos.transactions t
JOIN eurostyle_operational.stores s ON t.store_id = s.store_id
GROUP BY s.country_code
ORDER BY sum(t.tax_amount_eur) DESC;

-- 9. Revenue Breakdown Analysis (SHOWS DATA SOPHISTICATION)
SELECT 
    'Operational Orders' as revenue_source,
    count(*) as record_count,
    round(sum(subtotal_eur), 2) as subtotal_eur,
    round(sum(tax_amount_eur), 2) as tax_eur,
    round(sum(total_amount_eur), 2) as total_eur
FROM eurostyle_operational.orders
UNION ALL
SELECT 
    'POS Transactions' as revenue_source,
    count(*) as record_count,
    round(sum(subtotal_eur), 2) as subtotal_eur,
    round(sum(tax_amount_eur), 2) as tax_eur,
    round(sum(total_amount_eur), 2) as total_eur
FROM eurostyle_pos.transactions
UNION ALL
SELECT 
    'Finance GL Revenue Entries' as revenue_source,
    count(*) as record_count,
    0 as subtotal_eur,
    0 as tax_eur,
    round(sum(credit_amount), 2) as total_eur
FROM eurostyle_finance.gl_journal_lines 
WHERE account_id = '4000';

-- 10. Customer Engagement Analysis (IMPRESSIVE CROSS-DATABASE)
SELECT 
    c.country_code,
    count(DISTINCT c.customer_id) as total_customers,
    count(DISTINCT o.customer_id) as customers_with_orders,
    count(DISTINCT ws.customer_id) as customers_with_web_sessions,
    round(count(DISTINCT o.customer_id) * 100.0 / count(DISTINCT c.customer_id), 1) as order_conversion_rate,
    round(count(DISTINCT ws.customer_id) * 100.0 / count(DISTINCT c.customer_id), 1) as web_engagement_rate
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
LEFT JOIN eurostyle_webshop.web_sessions ws ON c.customer_id = ws.customer_id
GROUP BY c.country_code
ORDER BY total_customers DESC;

-- 11. Search Performance Analysis

SELECT
    sq.search_term,
    COUNT(*) AS search_frequency,
    COUNT(DISTINCT sq.session_id) AS unique_sessions,
    AVG(sq.results_count) AS avg_results_returned,
    ROUND(AVG(sq.clicked_result_position), 2) AS avg_click_position,
    SUM(CASE WHEN sq.no_results THEN 1 ELSE 0 END) AS zero_results_searches,
    ROUND(SUM(CASE WHEN sq.no_results THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS zero_results_pct,
    COUNT(DISTINCT ca.session_id) AS sessions_with_cart_adds,
    ROUND(COUNT(DISTINCT ca.session_id) * 100.0 / COUNT(DISTINCT sq.session_id), 1) AS search_to_cart_conversion_pct,
    AVG(sq.search_refinements) AS avg_refinements_per_search
FROM eurostyle_webshop.search_queries sq
LEFT JOIN eurostyle_webshop.cart_activities ca ON sq.session_id = ca.session_id
GROUP BY sq.search_term
HAVING search_frequency >= 5
ORDER BY search_frequency DESC
--LIMIT 20
;

-- 12. Customer Analysis by Device Type

SELECT 
    ws.device_type,
    COUNT(DISTINCT ws.session_id) AS total_sessions,
    COUNT(DISTINCT ws.customer_id) AS unique_customers,
    ROUND(AVG(ws.session_duration_seconds) / 60.0, 2) AS avg_session_duration_minutes,
    AVG(ws.page_views) AS avg_pages_per_session,
    COUNT(DISTINCT ca.session_id) AS sessions_with_cart_activity,
    ROUND(COUNT(DISTINCT ca.session_id) * 100.0 / COUNT(DISTINCT ws.session_id), 1) AS cart_conversion_rate_pct,
    ROUND(SUM(CASE WHEN ws.conversion_session THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT ws.session_id), 1) AS purchase_conversion_rate_pct,
    ROUND(SUM(CASE WHEN ws.bounce_session THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT ws.session_id), 1) AS bounce_rate_pct
FROM eurostyle_webshop.web_sessions ws
LEFT JOIN eurostyle_webshop.cart_activities ca ON ws.session_id = ca.session_id
GROUP BY ws.device_type
ORDER BY total_sessions DESC;


-- 13. Customer Value Intelligence

WITH customer_order_stats AS (
    SELECT 
        o.customer_id,
        COUNT(*) as actual_total_orders,
        SUM(o.subtotal_eur) as actual_total_spent,
        AVG(o.subtotal_eur) as actual_avg_order_value,
        MAX(o.order_date) as actual_last_order_date
    FROM eurostyle_operational.orders o
    GROUP BY o.customer_id
)
SELECT 
    c.customer_id,
    concat(c.first_name, ' ', c.last_name) AS customer_name,
    c.country_code AS customer_country,
    c.loyalty_tier,
    c.loyalty_points,
    COALESCE(cos.actual_total_orders, 0) AS orders_placed,
    ROUND(COALESCE(cos.actual_total_spent, 0), 2) AS lifetime_value_eur,
    ROUND(COALESCE(cos.actual_avg_order_value, 0), 2) AS avg_order_value_eur,
    CASE
        WHEN cos.actual_total_orders >= 3 AND cos.actual_total_spent >= 200 THEN 'VIP_Customer'
        WHEN cos.actual_total_orders >= 2 AND cos.actual_total_spent >= 100 THEN 'Loyal_Customer'
        WHEN cos.actual_total_orders >= 1 THEN 'Active_Customer'
        ELSE 'Browser_Only'
    END AS customer_segment,
    ROUND(
        (COALESCE(cos.actual_total_orders, 0) * 10 + 
         COALESCE(cos.actual_total_spent, 0) * 0.1 + 
         c.loyalty_points * 0.05 + 
         IF(c.marketing_opt_in, 15, 0) +
         IF(c.newsletter_subscription, 10, 0)) * 0.8, 1
    ) AS customer_value_score
FROM eurostyle_operational.customers c
LEFT JOIN customer_order_stats cos ON c.customer_id = cos.customer_id
WHERE c.customer_id IS NOT NULL
ORDER BY customer_value_score DESC, lifetime_value_eur DESC
LIMIT 20;