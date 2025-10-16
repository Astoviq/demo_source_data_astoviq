# 🔄 Data Transformation Scripts

## Overview

This directory contains scripts for transforming data between systems to implement proper enterprise architecture patterns.

## Operations as Master Implementation

### POS to Operations Orders Transformer

**Script**: `pos_to_operations_orders.py`

**Purpose**: Transforms POS transactions into Operations orders to implement the "Operations as Master" architecture pattern used in enterprise retail environments.

**What it does**:
1. Loads POS transactions from `data/csv/eurostyle_pos.transactions.csv.gz`
2. Maps each POS transaction to a proper Operations order
3. Generates sequential order IDs continuing from existing online orders
4. Creates corresponding order line items
5. Saves combined data (online + transformed in-store orders) back to CSV

**Usage**:
```bash
# Transform POS transactions to Operations orders
python3 scripts/data-transformation/pos_to_operations_orders.py

# Results:
# - Transforms 1,750 POS transactions → 1,750 in-store orders
# - Combines with existing 335 online orders
# - Total: 2,250 orders in Operations database
```

**Architecture Impact**:

**Before Transformation**:
```
Operations DB: 335 online orders (€172,610)
POS DB: 1,750 transactions (€308,031)
Problem: Duplicate/separate systems
```

**After Transformation**:
```
Operations DB: 2,250 orders (ALL channels)
├── Online: 335 orders (€172,610)
└── In-store: 1,915 orders (€389,963)
POS DB: Analytics and payment details
Result: Single source of truth
```

### Data Flow

```mermaid
graph LR
    A[POS Transactions] --> B[pos_to_operations_orders.py]
    B --> C[Operations Orders]
    D[Existing Online Orders] --> E[Combined Orders CSV]
    C --> E
    E --> F[ClickHouse Load]
```

### Generated Data Structure

**Order Transformation**:
- `order_id`: Sequential (ORD_EU_2024_000501, 000502, etc.)
- `customer_id`: Random mapping to existing customers
- `order_channel`: 'in-store'
- `store_id`: From original POS transaction
- `subtotal_eur`: From POS total_amount_eur
- `fulfillment_center`: Store ID (immediate pickup)
- `shipping_method`: 'in_store_pickup'

**Order Line Items**:
- `order_line_id`: Generated (OL_000501_001, etc.)
- `product_id`: 'PROD_MIXED_RETAIL' (placeholder)
- `quantity`: From POS item_count
- `line_total_eur`: From POS total_amount_eur

## Benefits of This Transformation

### Enterprise Architecture Compliance
- **Single Source of Truth**: All sales in Operations database
- **Unified Reporting**: Single query covers all channels
- **Audit Trail**: Complete order history regardless of origin

### Data Consistency
- **Revenue Matching**: Operations total matches GL entries
- **ID Continuity**: Sequential order numbering across channels
- **Referential Integrity**: All orders reference valid customers/stores

### Business Intelligence
- **Channel Analysis**: Compare online vs in-store performance
- **Customer Journey**: Cross-channel customer behavior
- **Financial Reporting**: Unified revenue recognition

## Corporate Alignment

This transformation implements the same pattern used by major retailers:
- **Target**: All channels (online, stores, mobile) → Operations system
- **Walmart**: Omnichannel order management through central OMS
- **Best Buy**: Ship-from-store, buy-online-pickup-in-store unified in Operations

The EuroStyle implementation demonstrates this enterprise pattern at demo scale while maintaining data integrity and realistic business logic.