---
id: eurostyle-business-processes
title: Business Processes – EuroStyle Fashion
version: 0.1
audience: internal
owner: Process Excellence
brand: EuroStyle Fashion
confidentiality: Internal
created_at: 2025-10-15
updated_at: 2025-10-15
---

# Business Processes

## Order‑to‑Cash (E‑commerce)
```mermaid
sequenceDiagram
  participant C as Customer
  participant WS as Webshop
  participant OPS as Operational
  participant FC as Fulfillment
  participant FIN as Finance
  C->>WS: Browse, add to cart, checkout
  WS->>OPS: Create order (customer, items, totals, VAT)
  OPS->>FC: Pick/pack/ship
  FC-->>OPS: Shipping + tracking
  OPS->>FIN: Revenue + AR journals
  FIN-->>OPS: Payment confirmation
  C-->>WS: Returns (if any)
```
Key controls: identity, consent, VAT, payment capture, returns window, reconciliation.

## Order‑to‑Cash (Store / POS)
```mermaid
sequenceDiagram
  participant Customer
  participant POS
  participant OPS as Operational
  participant FIN as Finance
  participant HR as HR
  Customer->>POS: Purchase
  POS->>OPS: Update inventory
  POS->>FIN: Revenue/Tax journals
  POS->>HR: Sales attribution per employee
```
Key controls: receipt sequencing, VAT mapping, POS payment integrity, commission logic.

## Purchase‑to‑Pay (Conceptual)
- Replenishment planning → Purchase order → Goods receipt → Invoice and 3‑way match → Payment
- Future sources: suppliers, lead times, cost price validation, landed costs

## Inventory Replenishment
- Forecast demand → Set reorder levels → Reallocate across stores → Expedite exceptions

## Returns & Refunds
- Initiate return → Eligibility and condition check → Refund/credit memo → Stock disposition

## Product Lifecycle Management
- New style setup → Launch → Markdown management → End‑of‑life → Archival

## Hire‑to‑Retire (HR)
- Recruiting → Onboarding → Scheduling/assignment → Performance & training → Offboarding

## Record‑to‑Report (Finance)
- Daily journals → Month‑end close → Consolidation → Reconciliation (Ops/POS ↔ Finance)

## Data Lineage Highlights
- Customers → Orders (Operational) → Finance GL
- Sessions → Orders (Webshop linkage) → Marketing attribution
- POS Items → Products (cost, margin) → Employee performance
