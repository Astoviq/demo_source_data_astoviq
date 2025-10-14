#!/usr/bin/env python3
"""
EuroStyle Source - Universal Schema Creator
==========================================
Configuration-driven schema creation following WARP.md rules.

Creates ClickHouse database schemas from YAML configuration files.
Works generically across all databases: operational, finance, hr, webshop.

Usage:
    python3 universal_schema_creator.py --database operational
    python3 universal_schema_creator.py --database hr --mode validate-only
    python3 universal_schema_creator.py --all
    python3 universal_schema_creator.py --config-path config/schemas/

Author: EuroStyle Data Team
Date: 2024-10-12
Following WARP.md configuration-driven development rules
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import subprocess
from datetime import datetime

class UniversalSchemaCreator:
    """
    Generic schema creator that works across all EuroStyle databases.
    Uses YAML configuration files to generate ClickHouse SQL schemas.
    """
    
    def __init__(self, config_path: str = "config", environment: str = "development"):
        """Initialize the universal schema creator."""
        self.config_path = Path(config_path)
        self.environment = environment
        self.schemas_path = self.config_path / "schemas"
        self.env_config = self._load_environment_config()
        self.logger = self._setup_logging()
        
        # Container configuration from environment
        self.container_name = self.env_config['clickhouse']['container_name']
        self.host = self.env_config['clickhouse']['host']
        self.port = self.env_config['clickhouse']['native_port']
        
        self.logger.info(f"🏗️  Universal Schema Creator initialized for {environment}")
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging according to WARP.md standards."""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(name)s] %(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger("UniversalSchemaCreator")
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment configuration."""
        env_file = self.config_path / "environments" / f"{self.environment}.yaml"
        
        if not env_file.exists():
            raise FileNotFoundError(f"Environment config not found: {env_file}")
            
        with open(env_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_schema_config(self, schema_file: Path) -> Dict[str, Any]:
        """Load a schema configuration file."""
        self.logger.info(f"📖 Loading schema config: {schema_file}")
        
        with open(schema_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate required fields
        required_fields = ['database', 'tables']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in {schema_file}")
                
        return config
    
    def _generate_column_definition(self, column_name: str, column_config: Dict[str, Any]) -> str:
        """Generate SQL column definition from YAML config."""
        col_type = column_config['type']
        
        # Handle nullable
        if column_config.get('nullable', True) and 'Nullable' not in col_type:
            if not column_config.get('default') and col_type != 'Nullable(Date)':
                col_type = f"Nullable({col_type})" if not col_type.startswith('Nullable') else col_type
        
        column_def = f"    {column_name} {col_type}"
        
        # Add default value
        if 'default' in column_config:
            default_val = column_config['default']
            column_def += f" DEFAULT {default_val}"
        
        return column_def
    
    def _generate_table_sql(self, database_name: str, table_name: str, table_config: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL from YAML config."""
        self.logger.info(f"🔧 Generating SQL for table: {database_name}.{table_name}")
        
        # Extract table properties
        engine = table_config.get('engine', 'MergeTree()')
        primary_key = table_config.get('primary_key', '')
        order_by = table_config.get('order_by', primary_key)
        
        # Generate column definitions
        columns = []
        for col_name, col_config in table_config['columns'].items():
            column_sql = self._generate_column_definition(col_name, col_config)
            columns.append(column_sql)
        
        columns_sql = ',\n'.join(columns)
        
        # Build CREATE TABLE statement
        sql = f"""CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
{columns_sql}
) ENGINE = {engine}"""
        
        if order_by:
            sql += f"\nORDER BY {order_by}"
        
        sql += ";"
        
        return sql
    
    def _generate_database_sql(self, schema_config: Dict[str, Any]) -> str:
        """Generate complete database SQL from schema config."""
        database_name = schema_config['database']
        description = schema_config.get('description', '')
        
        self.logger.info(f"🗄️  Generating database schema: {database_name}")
        
        # Start with database creation
        sql_parts = [
            f"-- =====================================================",
            f"-- EuroStyle {database_name.replace('eurostyle_', '').title()} Database",
            f"-- =====================================================",
            f"-- {description}",
            f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Configuration-driven schema following WARP.md rules",
            f"",
            f"CREATE DATABASE IF NOT EXISTS {database_name};",
            f"USE {database_name};",
            f""
        ]
        
        # Generate table definitions
        for table_name, table_config in schema_config['tables'].items():
            sql_parts.extend([
                f"-- {table_name.upper()} TABLE",
                f"-- " + "-" * 40,
                self._generate_table_sql(database_name, table_name, table_config),
                ""
            ])
        
        return '\n'.join(sql_parts)
    
    def _execute_clickhouse_sql(self, sql: str, database: str) -> bool:
        """Execute SQL against ClickHouse."""
        try:
            self.logger.info(f"🚀 Executing SQL for database: {database}")
            
            # Use docker exec to run SQL
            cmd = [
                'docker', 'exec', '-i', self.container_name,
                'clickhouse-client', '--multiquery'
            ]
            
            result = subprocess.run(
                cmd,
                input=sql,
                text=True,
                capture_output=True,
                check=True
            )
            
            if result.stdout:
                self.logger.info(f"✅ SQL executed successfully for {database}")
                return True
            else:
                self.logger.info(f"✅ SQL executed (no output) for {database}")
                return True
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ SQL execution failed for {database}: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error executing SQL for {database}: {e}")
            return False
    
    def validate_schema_config(self, schema_file: Path) -> bool:
        """Validate schema configuration without creating anything."""
        try:
            self.logger.info(f"🔍 Validating schema config: {schema_file}")
            
            config = self._load_schema_config(schema_file)
            
            # Validation checks
            checks = []
            
            # Check database name format
            db_name = config['database']
            if not db_name.startswith('eurostyle_'):
                checks.append(f"❌ Database name should start with 'eurostyle_': {db_name}")
            else:
                checks.append(f"✅ Database name format valid: {db_name}")
            
            # Check tables
            if not config['tables']:
                checks.append(f"❌ No tables defined")
            else:
                checks.append(f"✅ Found {len(config['tables'])} tables")
                
                # Check each table
                for table_name, table_config in config['tables'].items():
                    if 'columns' not in table_config:
                        checks.append(f"❌ Table {table_name} missing columns")
                    else:
                        col_count = len(table_config['columns'])
                        checks.append(f"✅ Table {table_name}: {col_count} columns")
            
            # Print validation results
            for check in checks:
                self.logger.info(check)
                
            # Return overall status
            failed_checks = [c for c in checks if c.startswith('❌')]
            if failed_checks:
                self.logger.error(f"❌ Validation failed: {len(failed_checks)} issues found")
                return False
            else:
                self.logger.info(f"✅ Validation passed: {schema_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Validation error for {schema_file}: {e}")
            return False
    
    def create_database_schema(self, database_name: str, mode: str = 'create') -> bool:
        """Create schema for a specific database."""
        schema_file = self.schemas_path / f"{database_name}_schema.yaml"
        
        if not schema_file.exists():
            self.logger.error(f"❌ Schema config not found: {schema_file}")
            return False
        
        # Validation mode
        if mode == 'validate-only':
            return self.validate_schema_config(schema_file)
        
        # Load and validate config
        if not self.validate_schema_config(schema_file):
            return False
            
        try:
            # Load schema config
            schema_config = self._load_schema_config(schema_file)
            
            # Generate SQL
            sql = self._generate_database_sql(schema_config)
            
            # Save SQL file for reference
            sql_output_path = self.config_path.parent / "data" / "schemas" / f"{database_name}_schema.sql"
            sql_output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sql_output_path, 'w') as f:
                f.write(sql)
            self.logger.info(f"💾 SQL saved to: {sql_output_path}")
            
            # Execute SQL if not dry-run
            if mode != 'dry-run':
                success = self._execute_clickhouse_sql(sql, database_name)
                if success:
                    self.logger.info(f"🎉 Database schema created: {database_name}")
                    return True
                else:
                    return False
            else:
                self.logger.info(f"🔍 Dry-run completed for: {database_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Schema creation failed for {database_name}: {e}")
            return False
    
    def create_all_schemas(self, mode: str = 'create') -> Dict[str, bool]:
        """Create schemas for all configured databases."""
        self.logger.info("🌍 Creating schemas for all databases")
        
        results = {}
        
        # Get all available databases from environment config
        databases = [db['name'].replace('eurostyle_', '') for db in self.env_config['clickhouse']['databases']]
        
        for database in databases:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing database: {database}")
            self.logger.info(f"{'='*60}")
            
            success = self.create_database_schema(database, mode)
            results[database] = success
            
        # Summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info("Schema Creation Summary")
        self.logger.info(f"{'='*60}")
        
        for database, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.logger.info(f"{database:20} {status}")
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"\n🎯 Overall: {successful}/{total} databases processed successfully")
        
        return results

def main():
    """Main entry point following WARP.md argument standards."""
    parser = argparse.ArgumentParser(
        description='Universal Schema Creator for EuroStyle Source databases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 universal_schema_creator.py --database operational
  python3 universal_schema_creator.py --database hr --mode validate-only
  python3 universal_schema_creator.py --all --mode dry-run
  python3 universal_schema_creator.py --all --config-path config/schemas/
        """
    )
    
    # Database selection (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--database', 
        choices=['operational', 'finance', 'hr', 'webshop'],
        help='Create schema for specific database'
    )
    group.add_argument(
        '--all', 
        action='store_true',
        help='Create schemas for all databases'
    )
    
    # Execution modes
    parser.add_argument(
        '--mode',
        choices=['create', 'validate-only', 'dry-run'],
        default='create',
        help='Execution mode (default: create)'
    )
    
    # Configuration options
    parser.add_argument(
        '--config-path',
        default='config',
        help='Path to configuration directory (default: config)'
    )
    
    parser.add_argument(
        '--environment',
        default='development',
        help='Environment to use (default: development)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Initialize schema creator
        creator = UniversalSchemaCreator(
            config_path=args.config_path,
            environment=args.environment
        )
        
        # Execute based on arguments
        if args.all:
            results = creator.create_all_schemas(mode=args.mode)
            success = all(results.values())
        else:
            success = creator.create_database_schema(args.database, mode=args.mode)
            
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logging.error(f"❌ Schema creator failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()