# EuroStyle Cross-System Data Integration Plan

## Problem Statement

The EuroStyle demo environment currently has three independent data generation systems (Operations, Webshop, Finance) that produce inconsistent data:

- **Revenue Gap**: Operations shows €9.34M in 2024 sales, but Finance GL only shows €2.02M (78% missing)
- **Conversion Issues**: 274k webshop sessions vs 14.9k online orders (5.4% conversion vs realistic 2-3%)
- **Time Misalignment**: Different data periods across systems (Operations: 2020-2025, Finance: 2023-2024)
- **No Shared IDs**: Customer and order IDs don't link across systems

## Solution Architecture

### 1. Unified Data Registry Pattern

Create a central data registry that coordinates all data generation:

```
Central Registry
├── shared_ids/
│   ├── customers.json      # Master customer ID list
│   ├── products.json       # Master product ID list  
│   ├── orders.json         # Master order ID list
│   └── sessions.json       # Session to order mapping
├── time_config.json        # Unified time periods
└── cross_refs.json         # Cross-system references
```

### 2. Shared Identifier Schema

**Customer IDs**: `CUST_EU_NNNNNN` (shared across all systems)
**Order IDs**: `ORD_YYYY_NNNNNN` (operational primary, referenced by finance)
**Session IDs**: `SESS_YYYY_NNNNNN` (webshop primary, linked to orders)
**Campaign IDs**: `CAMP_YYYY_QNNN` (shared marketing attribution)

### 3. Data Generation Sequence

1. **Operations First** (master data):
   - Generate customers, products, stores, campaigns
   - Generate orders with realistic volumes (50k orders = €9.34M)
   - Export customer/order IDs to registry

2. **Webshop Second** (behavioral data):
   - Read operational customer/order IDs from registry
   - Generate sessions with 2.5% conversion rate to match operational orders
   - Create session-to-order mapping (14.9k successful sessions → 14.9k online orders)
   - Generate non-converting sessions for remaining volume

3. **Finance Third** (financial records):
   - Read operational orders from registry
   - Generate GL entries for 100% of operational revenue (€9.34M)
   - Create proper revenue recognition, COGS, and expense allocation
   - Maintain same time periods as operations (2020-2025)

### 4. Time Period Standardization

**Unified Time Range**: 2020-01-01 to 2025-10-10
- Operations: Full range
- Webshop: Full range (behavioral data available throughout)
- Finance: Full range (GL entries for all operational transactions)

### 5. Cross-System Relationships

#### Customer Journey Tracking
```sql
-- Unified customer view
SELECT 
    c.customer_id,
    c.country_code,
    COUNT(DISTINCT ws.session_id) as total_sessions,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.order_total_eur) as lifetime_value,
    SUM(gl.amount_eur) as finance_recorded_revenue
FROM eurostyle_operational.customers c
LEFT JOIN eurostyle_webshop.web_sessions ws ON c.customer_id = ws.customer_id
LEFT JOIN eurostyle_operational.orders o ON c.customer_id = o.customer_id
LEFT JOIN eurostyle_finance.gl_journal_lines gl ON o.order_id = gl.reference_id
```

#### Revenue Reconciliation
```sql
-- Cross-system revenue validation
WITH operational_revenue AS (
    SELECT DATE_TRUNC('month', order_date) as month,
           SUM(order_total_eur) as ops_revenue
    FROM eurostyle_operational.orders 
    WHERE order_date >= '2020-01-01'
    GROUP BY month
),
finance_revenue AS (
    SELECT DATE_TRUNC('month', transaction_date) as month,
           SUM(amount_eur) as fin_revenue
    FROM eurostyle_finance.gl_journal_lines 
    WHERE account_code LIKE '4%' -- Revenue accounts
    GROUP BY month
)
SELECT o.month, o.ops_revenue, f.fin_revenue,
       (f.fin_revenue - o.ops_revenue) as variance
FROM operational_revenue o
LEFT JOIN finance_revenue f ON o.month = f.month
```

### 6. Implementation Strategy

#### Phase 1: Create Central Registry System
- Build shared ID management system
- Create cross-system reference tables
- Establish unified time configuration

#### Phase 2: Modify Data Generators
- Update operational generator to export IDs
- Modify webshop generator to read operational IDs
- Update finance generator to process operational transactions

#### Phase 3: Implement Conversion Flow
- Design realistic webshop-to-order conversion (2-3% rate)
- Create session attribution to orders
- Generate non-converting sessions for volume

#### Phase 4: Finance Integration
- Map 100% of operational orders to GL entries
- Implement proper revenue recognition timing
- Add COGS and expense allocation

### 7. Data Volume Targets (Realistic)

| System | Entity | Current | Target |
|--------|--------|---------|--------|
| Operations | Orders | 50,000 | 50,000 |
| Operations | Revenue | €9.34M | €9.34M |
| Webshop | Sessions | 274,000 | 180,000 |
| Webshop | Converting Sessions | ~14,900 | 14,900 (match online orders) |
| Webshop | Conversion Rate | 5.4% | 2.5% |
| Finance | GL Revenue | €2.02M | €9.34M |
| Finance | Coverage | 22% | 100% |

### 8. Validation Queries

After implementation, these queries should pass:

```sql
-- 1. Revenue reconciliation (should be ~0)
SELECT ABS(ops.total - fin.total) as revenue_variance
FROM (SELECT SUM(order_total_eur) as total FROM eurostyle_operational.orders WHERE YEAR(order_date) = 2024) ops,
     (SELECT SUM(amount_eur) as total FROM eurostyle_finance.gl_journal_lines WHERE account_code LIKE '4%' AND YEAR(transaction_date) = 2024) fin;

-- 2. Conversion rate validation (should be 2-3%)
SELECT (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM eurostyle_webshop.web_sessions WHERE session_date >= '2024-01-01')) as conversion_rate
FROM eurostyle_webshop.web_sessions ws 
JOIN eurostyle_operational.orders o ON ws.session_id = o.source_session_id 
WHERE ws.session_date >= '2024-01-01';

-- 3. Customer consistency (should be 0)
SELECT COUNT(*) as orphaned_orders
FROM eurostyle_operational.orders o
LEFT JOIN eurostyle_operational.customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

## Benefits

1. **Demo Credibility**: Finance reports will match operational reality
2. **Realistic Analytics**: Proper conversion rates and customer journey tracking
3. **Cross-System Reporting**: Enable comprehensive business intelligence
4. **Maintenance**: Single point of truth for shared data relationships
5. **Scalability**: Framework supports adding new systems (HR, Supply Chain, etc.)

## Next Steps

1. Build central registry system
2. Update operational data generator to export shared IDs
3. Modify webshop generator for realistic conversion flow
4. Fix finance generator to process all operational transactions
5. Test and validate cross-system consistency