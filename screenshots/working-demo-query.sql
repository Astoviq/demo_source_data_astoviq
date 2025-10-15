-- WORKING SCREENSHOT QUERIES - These will produce impressive results
-- Use these for your promotional screenshots

-- 1. Multi-Country Business Performance (MOST IMPRESSIVE)
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
    round(sum(t.subtotal_amount_eur), 0) as subtotal_eur,
    round(sum(t.tax_amount_eur), 0) as vat_collected_eur,
    concat(round(sum(t.tax_amount_eur) / sum(t.subtotal_amount_eur) * 100, 1), '%') as effective_vat_rate
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
    round(sum(subtotal_amount_eur), 2) as subtotal_eur,
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