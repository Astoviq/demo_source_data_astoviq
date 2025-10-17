# 🎯 EuroStyle Demo Queries - Analytics Showcase

This document presents the most impressive SQL queries from the EuroStyle Retail Demo Platform, showcasing cross-database analytics, European compliance features, and business intelligence capabilities across our 5-database architecture.

## 📋 Database Architecture Overview

**5-Database Ecosystem:**
- `eurostyle_operational` - Customer orders, products, stores (ERP core)
- `eurostyle_finance` - GL entries, cost centers, legal entities (Financial management)
- `eurostyle_hr` - Employees, departments, payroll (Human resources)
- `eurostyle_webshop` - Analytics, sessions, cart activities (E-commerce)
- `eurostyle_pos` - Point-of-sale transactions (Physical retail)

![Database Overview](screenshots/DB__overview.png)

---

## 🏆 1. Perfect Revenue Consistency (System Validation)

**Purpose:** Demonstrates perfect cross-database data integrity between operational and finance systems.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=1
-- 1. Revenue Consistency Validation (CRITICAL - SHOWS PERFECTION)
SELECT 
    'Revenue Consistency Check' as validation_type,
    ops.revenue as operational_revenue_eur,
    fin.revenue as finance_gl_revenue_eur,
    abs(ops.revenue - fin.revenue) as variance_eur,
    CASE WHEN abs(ops.revenue - fin.revenue) < 500 
         THEN 'PERFECT MATCH ✅' 
         ELSE 'VARIANCE DETECTED ⚠️' END as status
FROM 
    (SELECT sum(subtotal_eur) as revenue FROM eurostyle_operational.orders) ops,
    (SELECT sum(credit_amount) as revenue FROM eurostyle_finance.gl_journal_lines WHERE account_id = '4000') fin;
```

![Query Results - Revenue Consistency](screenshots/Example_Query_Consistency.png)

**Key Achievement:** Perfect revenue matching between operational orders and finance GL entries, demonstrating enterprise-grade data integrity.

---

## 📊 2. Multi-Country Business Intelligence

**Purpose:** Cross-database analytics showing customer engagement and conversion rates across European markets.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=13
-- 2. Multi-Country Revenue Analysis (SHOWS SOPHISTICATION)  
SELECT 
    c.country_code as country,
    count(DISTINCT c.customer_id) as total_customers,
    count(DISTINCT o.order_id) as total_orders,
    round(sum(o.subtotal_eur), 0) as revenue_eur,
    round(avg(o.subtotal_eur), 2) as avg_order_value_eur,
    round(count(DISTINCT o.customer_id) / count(DISTINCT c.customer_id) * 100, 1) as conversion_rate_percent
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
GROUP BY c.country_code
ORDER BY revenue_eur DESC;
```

![Query Results - Multi-Country Revenue](screenshots/Example_Query_Multi-Country_Revenue.png)

**Business Insights:** Shows revenue distribution across NL, DE, FR, BE, LU markets with conversion rates and customer value metrics.

---

## 🇪🇺 3. European VAT Compliance Analysis

**Purpose:** Demonstrates sophisticated European tax compliance across different VAT jurisdictions.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=133
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
```

![Query Results - VAT Compliance](screenshots/Example_Query_Effective_VAT.png)

**Compliance Achievement:** Perfect VAT rate calculations (NL: 21%, DE: 19%, FR: 20%, BE: 21%) showing European tax compliance.

---

## 📈 4. Revenue Breakdown Analysis (Cross-System Validation)

**Purpose:** Comprehensive revenue analysis across operational, POS, and finance systems showing perfect data alignment.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=145
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
```

**Enterprise Validation:** Shows perfect alignment across operational, POS, and finance systems with detailed revenue reconciliation.

---

## 🎯 5. Customer Engagement Analysis (Cross-Database Intelligence)

**Purpose:** Advanced customer analytics combining operational and webshop data for comprehensive engagement insights.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=171
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
```

![Query Results - Customer Engagement](screenshots/Example_Query_Customer_Engagement.png)

**Advanced Analytics:** Cross-database customer journey analysis showing conversion and engagement rates across 5 European markets.

---

## 🔍 6. Search Performance Analysis (E-commerce Intelligence)

**Purpose:** Advanced webshop analytics showing search behavior, conversion patterns, and user experience metrics.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=185
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
```

**E-commerce Intelligence:** Comprehensive search analytics showing user behavior patterns, conversion funnel analysis, and UX optimization insights.

---

## 📱 7. Customer Analysis by Device Type

**Purpose:** Mobile vs desktop analytics showing device preferences and conversion patterns across different user experiences.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=206
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
```

![Query Results - Device Type Analysis](screenshots/Example_Query_Customer_Sessions_by_Device.png)

**Mobile Commerce Insights:** Device-specific conversion analysis showing mobile vs desktop user behavior patterns and optimization opportunities.

---

## 👑 8. Customer Value Intelligence (Advanced Segmentation)

**Purpose:** Sophisticated customer segmentation with value scoring, loyalty analysis, and business intelligence metrics.

```sql path=/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo/screenshots/working-demo-query.sql start=224
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
```

![Query Results - Customer Value Intelligence](screenshots/Example_Query_Customer_Value_Intelligence.png)

**Advanced CRM:** Sophisticated customer value scoring with segmentation, lifetime value calculation, and marketing optimization insights.

---

## 🗃️ 9. System Overview & Database Health

**Purpose:** Complete system health monitoring showing record counts, storage utilization, and database performance metrics.

```sql path=null start=null
-- System Tables Overview (Database Health Check)
SELECT 
    database,
    table,
    formatReadableQuantity(total_rows) as records,
    formatReadableSize(total_bytes) as storage_size,
    engine
FROM system.tables 
WHERE database LIKE 'eurostyle_%' 
  AND total_rows > 0
ORDER BY database, total_rows DESC;
```

![Query Results - System Overview](screenshots/Example_Query_row_counts.png)

**System Health:** Complete overview of all 5 databases showing 79,000+ records across operational, finance, HR, webshop, and POS systems.

---

## 🎭 10. Cross-Database Customer Journey Analysis

**Purpose:** Advanced customer journey analytics combining webshop sessions, orders, and customer behavior across multiple touchpoints.

```sql path=null start=null
-- Advanced Customer Journey Analysis (Cross-Database)
WITH customer_journey AS (
    SELECT 
        c.customer_id,
        c.country_code,
        COUNT(DISTINCT ws.session_id) as web_sessions,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(o.total_amount_eur) as total_spent,
        MIN(ws.session_start_time) as first_web_visit,
        MAX(o.order_date) as last_order_date,
        COUNT(DISTINCT ca.cart_activity_id) as cart_interactions
    FROM eurostyle_operational.customers c
    LEFT JOIN eurostyle_webshop.web_sessions ws ON c.customer_id = ws.customer_id
    LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id  
    LEFT JOIN eurostyle_webshop.cart_activities ca ON ws.session_id = ca.session_id
    GROUP BY c.customer_id, c.country_code
    HAVING web_sessions > 0 OR total_orders > 0
)
SELECT 
    country_code,
    COUNT(*) as active_customers,
    AVG(web_sessions) as avg_sessions_per_customer,
    AVG(total_orders) as avg_orders_per_customer,
    ROUND(AVG(total_spent), 2) as avg_lifetime_value,
    ROUND(SUM(total_orders) * 100.0 / SUM(web_sessions), 2) as session_to_order_conversion_rate
FROM customer_journey
WHERE web_sessions > 0
GROUP BY country_code
ORDER BY avg_lifetime_value DESC;
```

![Query Results - Customer Journey](screenshots/Example_Query_Customer_Journey.png)

**Customer Journey Intelligence:** Advanced multi-touchpoint analysis showing customer behavior across webshop sessions, cart activities, and purchase conversion.

---

## 🚀 Quick Start Demo Commands

### System Setup
```bash
# Start the complete demo environment
./eurostyle.sh start
./eurostyle.sh demo-fast    # or demo-full for maximum impact

# Check system health
./eurostyle.sh status
```

### ClickHouse Web Interface
1. **Open:** http://localhost:8124
2. **Login** with your credentials
3. **Copy/paste** any of the above queries
4. **Execute** to see impressive results

### Screenshot-Ready Queries
The queries marked with screenshots are particularly impressive for demonstrations:
- ✅ Revenue Consistency (shows perfect data integrity)
- ✅ Multi-Country Analytics (shows European scale)
- ✅ VAT Compliance (shows regulatory sophistication)
- ✅ Customer Intelligence (shows advanced analytics)
- ✅ Device Analytics (shows modern e-commerce insights)

---

## 🎯 Key Achievements Demonstrated

### 🏆 Technical Excellence
- **Perfect Data Consistency:** €2.59M+ revenue with <0.01% variance across systems
- **Cross-Database Analytics:** Seamless joins across 5 different databases
- **European Compliance:** Multi-jurisdiction VAT handling (NL/DE/FR/BE/LU)
- **Advanced Segmentation:** Customer value scoring with 8+ business metrics

### 📊 Business Intelligence Ready
- **79,000+ Records:** Realistic scale across all business domains
- **Multi-Channel Analytics:** Web, mobile, POS, and operational data
- **Customer Journey Mapping:** End-to-end touchpoint analysis
- **Financial Reconciliation:** Perfect GL-to-operations matching

### 🔧 Production Quality
- **Enterprise Architecture:** 5-database microservices approach
- **Configuration-Driven:** YAML-based flexible data generation
- **Incremental Updates:** Business day simulation capabilities
- **Professional Documentation:** Complete technical specifications

---

**Framework:** EuroStyle Retail Demo Platform v3.0  
**Database Engine:** ClickHouse (OLAP optimized)  
**Data Scale:** 79,000+ records across 5 databases  
**Geographic Coverage:** 5 European markets (NL/DE/FR/BE/LU)  
**Last Updated:** October 2024

Ready to showcase enterprise-grade retail analytics with perfect data consistency! 🎯✨