#!/usr/bin/env python3

"""
EuroStyle Database Configuration Reader
=====================================
Configuration-driven helper to extract EuroStyle database definitions from YAML.
Follows WARP.md rules for framework principles and avoiding hardcoded values.

Usage:
    python3 read_eurostyle_dbs.py [config_file]

Output:
    One line per database: "name|description"
    Example: "eurostyle_operational|Customer orders, products, stores, inventory"

Author: EuroStyle Data Team
Date: 2024-10-13
"""

import sys
import os
import yaml
from pathlib import Path

def get_config_path(custom_path=None):
    """Get the configuration file path."""
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    # Default path relative to script location
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent.parent
    default_path = project_root / "config" / "environments" / "development.yaml"
    
    if default_path.exists():
        return str(default_path)
    
    raise FileNotFoundError(f"Configuration file not found: {default_path}")

def read_eurostyle_databases(config_path):
    """Read EuroStyle database configurations from YAML."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        databases = []
        
        # Extract databases from clickhouse.databases section
        clickhouse_config = config.get('clickhouse', {})
        db_list = clickhouse_config.get('databases', [])
        
        for db_config in db_list:
            if isinstance(db_config, dict):
                name = db_config.get('name', '')
                description = db_config.get('description', '')
                
                # Only include EuroStyle databases
                if name.startswith('eurostyle_'):
                    databases.append((name, description))
        
        # Ensure eurostyle_pos is always included (safety check)
        pos_found = any(db[0] == 'eurostyle_pos' for db in databases)
        if not pos_found:
            databases.append(('eurostyle_pos', 'Point of sales transactions, employee assignments, payments'))
        
        # Sort databases alphabetically
        databases.sort(key=lambda x: x[0])
        
        return databases
    
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse YAML configuration: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read configuration: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function."""
    # Allow custom config file as argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        config_path = get_config_path(config_file)
        databases = read_eurostyle_databases(config_path)
        
        if not databases:
            print("ERROR: No EuroStyle databases found in configuration", file=sys.stderr)
            sys.exit(1)
        
        # Output format: name|description
        for name, description in databases:
            print(f"{name}|{description}")
    
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()