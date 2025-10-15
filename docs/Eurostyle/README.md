---
id: eurostyle-business-docs
title: EuroStyle Fashion - Business Documentation
version: 0.1
audience: internal
owner: Business Architecture
brand: EuroStyle Fashion
confidentiality: Internal
created_at: 2025-10-15
updated_at: 2025-10-15
---

# EuroStyle Fashion – Business Documentation

This directory contains business-facing documentation for EuroStyle Fashion used by internal departments and for public website content. It complements the technical specs under `docs/technical-specs/`.

## Audiences
- Internal: Operations, Finance, HR, E‑commerce, Store Ops, Analytics
- Public (website-ready summaries): Company info, sustainability, careers, factsheets

## Structure
```
Eurostyle/
├── README.md
├── 01_vision_and_mission.md
├── 02_industry_model.md
├── 03_business_processes.md
├── 04_metrics_and_scorecards.md
├── 05_business_glossary.md
├── 06_customer_journey_and_channels.md
├── 07_organization_and_governance.md
├── website_content/
│   ├── about_us.md
│   ├── sustainability.md
│   ├── careers.md
│   └── investor_factsheet.md
├── templates/
│   ├── markdown_base.j2
│   ├── section.j2
│   └── kpi_table.j2
├── config/
│   ├── company_profile.yaml
│   ├── metrics_catalog.yaml
│   └── doc_defaults.yaml
├── pdf/
│   └── README.md
└── assets/
    └── .gitkeep
```

## Conventions
- Brand name: “EuroStyle Fashion” (consistent across all documents)
- Language: English for Markdown; public copy can be localized later
- Diagrams: Mermaid blocks embedded in Markdown (optionally exported to SVG for PDFs)
- Governance: Optional Document Control sections where relevant

## Export to PDF (optional)
- Mermaid to SVG (optional): `mmdc -i assets/diagram.mmd -o assets/diagram.svg`
- Single PDF from Markdown: `pandoc *.md -o pdf/Business_Overview.pdf`
- Site generators (optional): MkDocs or similar for browsable docs

## Notes
- These materials are business-facing and do not modify any application code.
- Content is designed to be reusable for onboarding and data discovery/datalake ingestion.
