# Individual Loading Scripts Archive

**Date Archived**: October 16, 2024  
**Reason**: Migration to unified `./eurostyle.sh` management system  
**WARP.md Compliance**: Following rule to archive old code instead of deletion

## What's Archived

The following individual database loading scripts have been archived:

- `load_finance_data.sh` - Individual finance database loader
- `load_hr_data.sh` - Individual HR database loader  
- `load_webshop_data.sh` - Individual webshop database loader
- `load_csv_data.sh` - Legacy CSV loading utility

## Why Archived

These scripts were replaced by the unified `./eurostyle.sh` system which provides:

- **Unified Entry Point**: Single command interface for all operations
- **Better Integration**: Seamless data generation + loading workflows
- **Improved Consistency**: All databases loaded with same standards
- **Configuration-Driven**: No hard-coded paths or database names
- **Production Ready**: Professional logging, error handling, validation

## Migration Guide

**Old Way** (archived):
```bash
bash scripts/data-loading/load_finance_data.sh
bash scripts/data-loading/load_hr_data.sh  
bash scripts/data-loading/load_webshop_data.sh
```

**New Way** (current):
```bash
./eurostyle.sh demo-fast    # Generate and load all databases
./eurostyle.sh demo-full    # Generate and load all databases (full scale)
./eurostyle.sh increment    # Add incremental data
./eurostyle.sh status       # Check system status
```

## Current Loading Architecture

The new system uses:
- `load_full_dataset.sh` - Unified loader for all databases (used by demo-fast/demo-full)
- `load_incremental_data.sh` - Incremental data loader (used by increment)

Both are called automatically by `./eurostyle.sh` commands and should not be run directly.

## Recovery

If you need to restore these individual loaders:
1. The archived scripts are fully functional
2. Copy them back to `scripts/data-loading/` 
3. Ensure CSV files are in `data/csv/` with correct naming pattern

However, we recommend using `./eurostyle.sh` for all operations going forward.