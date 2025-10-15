#!/usr/bin/env python3
"""
EuroStyle CSV Header Validator
=====================================
Validates CSV file headers against database schemas to prevent loading mismatched data.
This is a fast-fail validator that catches CSV/schema mismatches before data loading.
"""

import sys
import gzip
import csv
import os
import subprocess
from pathlib import Path
from typing import List, Set, Optional, Tuple


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def log_info(message: str):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def log_warn(message: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def log_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def open_csv_file(file_path: str):
    """Open CSV file, handling both .gz and regular files."""
    if file_path.endswith('.gz'):
        return gzip.open(file_path, 'rt', encoding='utf-8')
    else:
        return open(file_path, 'r', encoding='utf-8')


def get_csv_headers(file_path: str) -> List[str]:
    """Extract headers from CSV file."""
    try:
        with open_csv_file(file_path) as f:
            reader = csv.reader(f)
            headers = next(reader)
            return [h.strip() for h in headers]
    except Exception as e:
        log_error(f"Failed to read CSV headers from {file_path}: {e}")
        sys.exit(1)


def get_database_columns(database: str, table: str) -> List[str]:
    """Get column names from ClickHouse database table."""
    try:
        # Use Docker exec to run ClickHouse client
        cmd = [
            'docker', 'exec', '-i', 'eurostyle_clickhouse_retail', 
            'clickhouse-client', '--query',
            f"SELECT name FROM system.columns WHERE database='{database}' AND table='{table}' ORDER BY position"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        columns = [col.strip() for col in result.stdout.strip().split('\n') if col.strip()]
        
        if not columns:
            log_error(f"No columns found for table {database}.{table}")
            return []
            
        return columns
        
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to query database columns for {database}.{table}: {e}")
        log_error(f"Make sure ClickHouse container 'eurostyle_clickhouse_retail' is running")
        return []
    except Exception as e:
        log_error(f"Unexpected error querying database: {e}")
        return []


def parse_file_path(file_path: str) -> Optional[Tuple[str, str]]:
    """Parse database and table name from CSV file path."""
    # Expected format: data/csv/eurostyle_operational.customers.csv.gz
    # or: eurostyle_operational.customers.csv.gz
    
    filename = Path(file_path).name
    
    # Remove .csv.gz or .csv extension
    if filename.endswith('.csv.gz'):
        base_name = filename[:-7]
    elif filename.endswith('.csv'):
        base_name = filename[:-4]
    else:
        return None
    
    # Handle incremental and update files
    # e.g., eurostyle_operational.customers_incremental.csv.gz
    # or eurostyle_operational.customers_updates.csv.gz
    if base_name.endswith('_incremental'):
        base_name = base_name[:-12]  # Remove _incremental
    elif base_name.endswith('_updates'):
        base_name = base_name[:-8]   # Remove _updates
    
    # Split on first dot to separate database from table
    parts = base_name.split('.', 1)
    if len(parts) != 2:
        return None
        
    database, table = parts
    return database, table


def validate_csv_headers(file_path: str, expected_columns: List[str]) -> Tuple[bool, List[str], List[str]]:
    """Validate CSV headers against expected columns."""
    csv_headers = get_csv_headers(file_path)
    csv_set = set(csv_headers)
    expected_set = set(expected_columns)
    
    missing = list(expected_set - csv_set)
    extra = list(csv_set - expected_set)
    
    is_valid = len(missing) == 0 and len(extra) == 0
    return is_valid, missing, extra


def check_clickhouse_container() -> bool:
    """Check if ClickHouse container is running."""
    try:
        cmd = ['docker', 'ps', '--format', 'table {{.Names}}']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return 'eurostyle_clickhouse_retail' in result.stdout
    except:
        return False


def main():
    if len(sys.argv) < 2:
        print(f"""
{Colors.BLUE}EuroStyle CSV Header Validator{Colors.NC}

Usage:
    {sys.argv[0]} <csv_file_path> [--strict]

Examples:
    {sys.argv[0]} data/csv/eurostyle_operational.customers.csv.gz
    {sys.argv[0]} data/csv/eurostyle_hr.employees_incremental.csv.gz --strict

Options:
    --strict    Exit with error code on any mismatch (for CI/CD)
    
The validator automatically detects database and table names from the file path.
File naming convention: {{database}}.{{table}}.csv[.gz]
""")
        sys.exit(1)
    
    file_path = sys.argv[1]
    strict_mode = '--strict' in sys.argv
    
    # Check if file exists
    if not os.path.exists(file_path):
        log_error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Check if ClickHouse container is running
    if not check_clickhouse_container():
        log_error("ClickHouse container 'eurostyle_clickhouse_retail' is not running")
        log_info("Start it with: ./eurostyle.sh start")
        sys.exit(1)
    
    # Parse database and table from file path
    parsed = parse_file_path(file_path)
    if not parsed:
        log_error(f"Cannot parse database and table from file path: {file_path}")
        log_info("Expected format: {{database}}.{{table}}.csv[.gz]")
        log_info("Example: eurostyle_operational.customers.csv.gz")
        sys.exit(1)
    
    database, table = parsed
    log_info(f"Validating: {file_path}")
    log_info(f"Detected: database='{database}', table='{table}'")
    
    # Get expected columns from database
    expected_columns = get_database_columns(database, table)
    if not expected_columns:
        log_warn(f"Could not retrieve schema for {database}.{table}")
        log_warn("Skipping validation (table may not exist yet)")
        sys.exit(0)  # Don't fail if table doesn't exist
    
    # Validate CSV headers
    is_valid, missing, extra = validate_csv_headers(file_path, expected_columns)
    
    # Report results
    print()
    if is_valid:
        log_info(f"✅ CSV headers match database schema")
        log_info(f"   File: {file_path}")
        log_info(f"   Table: {database}.{table}")
        log_info(f"   Columns: {len(expected_columns)} columns matched")
    else:
        log_error(f"❌ CSV header mismatch detected")
        print(f"   File: {file_path}")
        print(f"   Table: {database}.{table}")
        print()
        
        if missing:
            log_error(f"Missing columns (in database but not in CSV):")
            for col in sorted(missing):
                print(f"     - {col}")
        
        if extra:
            log_error(f"Extra columns (in CSV but not in database):")
            for col in sorted(extra):
                print(f"     + {col}")
        
        print()
        log_info("Database columns (expected):")
        for i, col in enumerate(expected_columns, 1):
            print(f"  {i:2d}. {col}")
        
        print()
        csv_headers = get_csv_headers(file_path)
        log_info("CSV columns (actual):")
        for i, col in enumerate(csv_headers, 1):
            print(f"  {i:2d}. {col}")
    
    print()
    
    # Exit with appropriate code
    if not is_valid:
        if strict_mode:
            log_error("Exiting with error code due to --strict mode")
            sys.exit(1)
        else:
            log_warn("Validation failed, but continuing (use --strict to fail)")
            sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()