# Archive: Legacy Folder Structure (2025-10-14)

## What was archived

**Empty subdirectories** from `data/csv/` that were inconsistent with the actual data layout:

```
data/csv/
├── operational/  ← Empty directory (archived)
├── webshop/      ← Empty directory (archived)  
├── finance/      ← Empty directory (archived)
└── hr/           ← Empty directory (archived)
```

## Why archived

The project uses a **flat structure** for CSV files:
```
data/csv/
├── eurostyle_operational.customers.csv.gz
├── eurostyle_operational.orders.csv.gz
├── eurostyle_finance.legal_entities.csv.gz
├── eurostyle_hr.employees.csv.gz
├── eurostyle_pos.transactions.csv.gz
└── eurostyle_webshop.web_sessions.csv.gz
```

This flat structure is:
- ✅ **Consistent** with the `eurostyle_{database}.{table}.csv.gz` naming pattern
- ✅ **Configuration-driven** (no hard-coded paths in scripts)
- ✅ **Simpler** for automation and data loading
- ✅ **Compatible** with the POS system integration

## Original documentation

The empty subdirectories were referenced in `FOLDER_STRUCTURE.md` but never actually used by the data generation system.

## Restoration

If hierarchical structure is needed in the future:
```bash
# Restore archived directories
cp -r archive/2025-10-14/data_csv_legacy_structure/* data/csv/

# Move files into subdirectories (example for operational)
mv data/csv/eurostyle_operational.*.csv.gz data/csv/operational/
```