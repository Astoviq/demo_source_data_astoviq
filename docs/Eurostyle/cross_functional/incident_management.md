---
id: eurostyle-cross-incident-mgmt
title: Incident Management & Escalation
version: 0.1
audience: internal
owner: PMO / SRE (where applicable)
brand: EuroStyle Fashion
confidentiality: Internal
created_at: 2025-10-15
updated_at: 2025-10-15
---

# Incident Management & Escalation

## Severity Matrix
- Sev1: Checkout/POS down; financial posting blocked; data breach
- Sev2: Major feature degraded; large reconciliation variance
- Sev3: Minor feature issue; small data delays
- Sev4: Cosmetic or documentation

## Response Targets
- Sev1: acknowledge < 10 min; comms every 30 min; restore < 2 h
- Sev2: acknowledge < 30 min; restore < 8 h

## Roles
- Incident Lead: based on process (site = E‑comm; POS = Retail Ops; close = Finance; O2C = Ops)
- Comms Lead: PMO; Status channel in Teams

## Post‑Incident
- 48 h: root cause, corrective actions, owner, ETA
- Track actions in Jira; review in weekly ops forum