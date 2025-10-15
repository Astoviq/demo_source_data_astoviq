---
id: eurostyle-metrics-scorecards
title: Metrics and Scorecards – EuroStyle Fashion
version: 0.1
audience: internal
owner: Analytics COE
brand: EuroStyle Fashion
confidentiality: Internal
created_at: 2025-10-15
updated_at: 2025-10-15
---

# Metrics and Scorecards

This catalog defines must‑have KPIs with business definitions, formulas, owners, targets, thresholds, data sources, and ClickHouse examples. Targets are indicative and may be adjusted per market/season.

## Financial

### Net Revenue (EUR)
- Definition: Total order revenue incl. tax and shipping less discounts
- Owner: Finance
- Target: YoY +8%
- Thresholds: green ≥ target; yellow ≥ target–2pp; red < target–2pp
- Source: `eurostyle_operational.orders`
- Query:
```sql
SELECT sum(total_amount_eur) AS net_revenue_eur
FROM eurostyle_operational.orders
WHERE order_date >= toDate('2024-01-01');
```

### Gross Margin % (POS)
- Definition: (POS revenue − COGS) / POS revenue
- Owner: Finance, Merchandising
- Target: ≥ 58%
- Source: `eurostyle_pos.transaction_items` JOIN `eurostyle_operational.products`
- Query:
```sql
SELECT
  sum(ti.line_total_eur) AS revenue_eur,
  sum(ti.quantity * p.cost_price_eur) AS cogs_eur,
  (sum(ti.line_total_eur) - sum(ti.quantity * p.cost_price_eur)) / nullIf(sum(ti.line_total_eur), 0) AS gross_margin_pct
FROM eurostyle_pos.transaction_items ti
LEFT JOIN eurostyle_operational.products p ON ti.product_id = p.product_id
WHERE ti.item_id LIKE 'ITEM_EU_%';
```

### Revenue Reconciliation Variance (Ops vs Finance)
- Definition: Finance GL revenue minus Operational revenue
- Owner: Finance
- Target: 0 (exact match)
- Source: `eurostyle_operational.orders`, `eurostyle_finance.gl_journal_lines`
- Query:
```sql
WITH operational AS (
  SELECT toStartOfMonth(order_date) AS month, sum(total_amount_eur) AS ops_revenue
  FROM eurostyle_operational.orders
  GROUP BY month
), finance AS (
  SELECT toStartOfMonth(journal_date) AS month, sum(credit_amount) AS fin_revenue
  FROM eurostyle_finance.gl_journal_lines
  WHERE account_id LIKE '4%'
  GROUP BY month
)
SELECT o.month, o.ops_revenue, f.fin_revenue, (f.fin_revenue - o.ops_revenue) AS variance
FROM operational o
LEFT JOIN finance f ON o.month = f.month
ORDER BY month;
```

## Customer & Digital

### Conversion Rate (Webshop)
- Definition: Converting sessions / total sessions
- Owner: E‑commerce
- Target: 2.5% (market-dependent)
- Source: `eurostyle_webshop.web_sessions`
- Query:
```sql
SELECT (countIf(conversion_session = 1) * 100.0) / nullIf(count(), 0) AS conversion_rate_pct
FROM eurostyle_webshop.web_sessions
WHERE session_date >= toDate('2024-01-01');
```

### Repeat Purchase Rate
- Definition: Customers with ≥2 orders / customers with ≥1 order
- Owner: CRM
- Target: ≥ 32%
- Source: `eurostyle_operational.orders`
- Query:
```sql
WITH co AS (
  SELECT customer_id, count() AS orders
  FROM eurostyle_operational.orders
  WHERE order_date >= addYears(today(), -1)
  GROUP BY customer_id
)
SELECT sum(orders >= 2) / nullIf(sum(orders >= 1), 0) AS repeat_purchase_rate
FROM co;
```

### Average Order Value (AOV)
- Definition: Net revenue / number of orders
- Owner: E‑commerce, Merchandising
- Source: `eurostyle_operational.orders`
- Query:
```sql
SELECT sum(total_amount_eur) / nullIf(count(), 0) AS aov_eur
FROM eurostyle_operational.orders
WHERE order_date >= addMonths(today(), -3);
```

## Operations & Fulfillment

### Order Cycle Time (days)
- Definition: Average days from order_datetime to delivery_date
- Owner: Operations
- Source: `eurostyle_operational.orders`
- Query:
```sql
SELECT avg(dateDiff('day', order_datetime, delivery_date)) AS cycle_days
FROM eurostyle_operational.orders
WHERE delivery_date IS NOT NULL;
```

### On‑Time Fulfillment Rate
- Definition: % of delivered orders on/before promised_delivery_date
- Owner: Operations
- Source: `eurostyle_operational.orders`
- Query:
```sql
SELECT countIf(delivery_date <= promised_delivery_date) / nullIf(countIf(promised_delivery_date IS NOT NULL), 0) AS on_time_rate
FROM eurostyle_operational.orders
WHERE delivery_date IS NOT NULL;
```

### Return Rate
- Definition: Returned orders / total orders
- Owner: Operations, Customer Service
- Source: `eurostyle_operational.orders`
- Query:
```sql
SELECT countIf(order_status = 'returned') / nullIf(count(), 0) AS return_rate
FROM eurostyle_operational.orders
WHERE order_date >= addMonths(today(), -3);
```

## POS Performance

### Sales per Employee (EUR)
- Definition: POS revenue per employee over a period
- Owner: Retail Ops, HR
- Source: `eurostyle_pos.transactions`
- Query:
```sql
SELECT employee_id, sum(total_amount_eur) AS sales_eur
FROM eurostyle_pos.transactions
WHERE transaction_date >= addMonths(today(), -1)
GROUP BY employee_id
ORDER BY sales_eur DESC
LIMIT 20;
```

### Units per Transaction (UPT)
- Definition: Units sold / number of transactions
- Owner: Retail Ops
- Source: `eurostyle_pos.transaction_items`
- Query:
```sql
SELECT sum(quantity) / nullIf(countDistinct(transaction_id), 0) AS upt
FROM eurostyle_pos.transaction_items
WHERE toDate(now()) >= toDate(addMonths(today(), -1));
```

### Refund/Void Rate
- Definition: Voided/refunded transactions / total
- Owner: Retail Ops, Finance
- Source: `eurostyle_pos.transactions`
- Query:
```sql
SELECT countIf(payment_status IN ('voided','refunded')) / nullIf(count(), 0) AS refund_void_rate
FROM eurostyle_pos.transactions
WHERE transaction_date >= addMonths(today(), -1);
```

## HR Effectiveness

### Revenue per Planned Hour (POS)
- Definition: Sales EUR / planned hours in period
- Owner: HR, Retail Ops
- Source: `eurostyle_pos.transactions`, `eurostyle_pos.employee_assignments`
- Query:
```sql
WITH sales AS (
  SELECT employee_id, sum(total_amount_eur) AS sales_eur
  FROM eurostyle_pos.transactions
  WHERE transaction_date >= addMonths(today(), -1)
  GROUP BY employee_id
), hours AS (
  SELECT employee_id, sum(planned_hours) AS planned_hours
  FROM eurostyle_pos.employee_assignments
  WHERE assignment_date >= addMonths(today(), -1)
  GROUP BY employee_id
)
SELECT s.employee_id, sales_eur / nullIf(planned_hours, 0) AS revenue_per_planned_hour
FROM sales s
LEFT JOIN hours h ON s.employee_id = h.employee_id
ORDER BY revenue_per_planned_hour DESC;
```

### Employee Turnover Rate (Conceptual)
- Definition: Terminations in period / average headcount
- Owner: HR
- Source: `eurostyle_hr.*` (requires status history/events)
- Query (placeholder):
```sql
-- Requires employee_status_history table with effective dates
-- SELECT terminations / nullIf(avg_headcount, 0) AS turnover_rate ...
```

## Compliance & Sustainability

### VAT Compliance Rate (POS)
- Definition: Share of POS transactions with valid country VAT rates
- Owner: Finance
- Source: `eurostyle_pos.transactions`
- Query:
```sql
SELECT
  country_code,
  countIf(
    (country_code='NL' AND vat_rate_percentage IN (21)) OR
    (country_code='DE' AND vat_rate_percentage IN (19)) OR
    (country_code='FR' AND vat_rate_percentage IN (20)) OR
    (country_code='BE' AND vat_rate_percentage IN (21)) OR
    (country_code='LU' AND vat_rate_percentage IN (17))
  ) / nullIf(count(), 0) AS compliance_rate
FROM eurostyle_pos.transactions
GROUP BY country_code
ORDER BY country_code;
```

### Product Sustainability Coverage
- Definition: % of active products with sustainability_score populated
- Owner: Merchandising, Sustainability
- Source: `eurostyle_operational.products`
- Query:
```sql
SELECT countIf(is_active AND sustainability_score > 0) / nullIf(countIf(is_active), 0) AS sustainability_coverage
FROM eurostyle_operational.products;
```

### OTIFNI (%): On Time, In Full, No Issues
- Definition: Share of delivered orders that were delivered on/before promised date (On Time), had no returns (In Full proxy), and no issues recorded with completed payment (No Issues)
- Owner: Operations (primary), Finance (validation)
- Target: ≥ 95%
- Source: `eurostyle_operational.orders`
- Notes: "In Full" is proxied by absence of returns; detailed line-level checks may require shipment/item data.
- Query:
```sql
SELECT
  (countIf(
    delivery_date IS NOT NULL
    AND promised_delivery_date IS NOT NULL
    AND delivery_date <= promised_delivery_date
    AND order_status != 'returned'
    AND isNull(return_reason)
    AND payment_status = 'completed'
    AND isNull(customer_service_notes)
  ) * 100.0) / nullIf(countIf(delivery_date IS NOT NULL AND promised_delivery_date IS NOT NULL), 0) AS otifni_pct
FROM eurostyle_operational.orders;
```

---

Governance: KPI owners review definitions quarterly; targets per market/season kept in planning systems. All queries are examples and may be adapted to actual environments.
