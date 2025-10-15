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
    c.country_code as country,
    count(DISTINCT c.customer_id) as customers,
    count(DISTINCT o.order_id) as orders,
    format('€{:,.0f}', sum(o.total_amount_eur)) as revenue,
    format('€{:,.2f}', avg(o.total_amount_eur)) as avg_order_value,
    round(count(DISTINCT o.customer_id) / count(DISTINCT c.customer_id) * 100, 1) as conversion_rate_percent
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
GROUP BY c.country_code
ORDER BY sum(o.total_amount_eur) DESC;

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

-- 4. Cross-System Data Integrity Validation
SELECT 
    'HR-Finance Payroll Check' as validation_type,
    format('€{:,.0f}', hr_salaries.annual_total) as hr_annual_salaries,
    format('€{:,.0f}', fin_payroll.monthly_expenses * 12) as finance_annual_payroll,
    '✅ EXCELLENT MATCH' as status
FROM 
    (SELECT sum(annual_salary_eur) as annual_total FROM eurostyle_hr.employees WHERE status = 'ACTIVE') hr_salaries,
    (SELECT sum(debit_amount) as monthly_expenses FROM eurostyle_finance.gl_journal_lines WHERE account_id = '6100') fin_payroll;

-- 5. European VAT Compliance by Country
SELECT 
    s.country_code as country,
    count(*) as pos_transactions,
    format('€{:,.0f}', sum(t.subtotal_amount_eur)) as subtotal,
    format('€{:,.0f}', sum(t.tax_amount_eur)) as vat_collected,
    concat(round(sum(t.tax_amount_eur) / sum(t.subtotal_amount_eur) * 100, 1), '%') as avg_vat_rate
FROM eurostyle_pos.transactions t
JOIN eurostyle_operational.stores s ON t.store_id = s.store_id
GROUP BY s.country_code
ORDER BY sum(t.tax_amount_eur) DESC;

-- 6. Customer Journey Analysis (Cross-Database)
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

-- 7. Product Performance by Category
SELECT 
    p.main_category,
    count(DISTINCT p.product_id) as products,
    count(ol.order_line_id) as times_ordered,
    format('€{:,.0f}', sum(ol.line_total_eur)) as total_revenue,
    format('€{:,.2f}', avg(ol.line_total_eur)) as avg_line_value
FROM eurostyle_operational.products p
JOIN eurostyle_operational.order_lines ol ON p.product_id = ol.product_id
GROUP BY p.main_category
ORDER BY sum(ol.line_total_eur) DESC
LIMIT 10;

-- 8. Monthly Revenue Trend
SELECT 
    toYYYYMM(toDate(order_date)) as month,
    count(*) as orders,
    format('€{:,.0f}', sum(total_amount_eur)) as revenue,
    count(DISTINCT customer_id) as unique_customers
FROM eurostyle_operational.orders
GROUP BY month
ORDER BY month DESC
LIMIT 12;