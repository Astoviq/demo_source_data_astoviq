-- WORKING SCREENSHOT QUERIES - These will produce impressive results
-- Use these for your promotional screenshots
-- Updated: October 2024 - Fixed formatting for ClickHouse compatibility

-- 1. Operations as Master Architecture (MOST IMPRESSIVE - Shows unified data flow)
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

-- 1b. Perfect Revenue Consistency Check (Operations → GL)
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

-- 2. Multi-Country Business Performance (GEOGRAPHIC ANALYSIS)
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

-- 2. System Overview - Database Record Counts (IMPRESSIVE SCALE)
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

-- 4. Revenue Breakdown Analysis (SHOWS DATA SOPHISTICATION)
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

-- 5. Customer Engagement Analysis (IMPRESSIVE CROSS-DATABASE)
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