#!/usr/bin/env python3
"""
EuroStyle Empty Column Checker
Comprehensive analysis of empty columns across all databases
"""
import subprocess
import json
from typing import Dict, List, Tuple
import sys

class EmptyColumnChecker:
    def __init__(self):
        self.databases = ['eurostyle_operational', 'eurostyle_finance', 'eurostyle_hr', 'eurostyle_webshop']
        self.empty_columns = {}
        self.critical_empty_columns = {}
        
    def run_query(self, query: str) -> List[Dict]:
        """Execute ClickHouse query and return results"""
        try:
            cmd = [
                'docker', 'exec', 'eurostyle_clickhouse_retail', 'clickhouse-client',
                '--query', query,
                '--format', 'JSONEachRow'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON lines
            results = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def get_table_columns(self, database: str, table: str) -> List[Dict]:
        """Get column information for a table"""
        query = f"DESCRIBE {database}.{table}"
        return self.run_query(query)
    
    def get_all_tables(self, database: str) -> List[str]:
        """Get all table names in a database"""
        query = f"SELECT name FROM system.tables WHERE database = '{database}'"
        results = self.run_query(query)
        return [row['name'] for row in results]
    
    def check_column_emptiness(self, database: str, table: str, column: str) -> Tuple[int, int, float]:
        """Check how many rows have empty/null values in a column"""
        # Count total rows
        total_query = f"SELECT COUNT(*) as total FROM {database}.{table}"
        total_result = self.run_query(total_query)
        total_rows = int(total_result[0]['total']) if total_result else 0
        
        if total_rows == 0:
            return 0, 0, 0.0
        
        # Count empty rows - simplified approach
        try:
            # Check for NULL values first
            null_query = f"SELECT COUNT(*) as empty FROM {database}.{table} WHERE {column} IS NULL"
            null_result = self.run_query(null_query)
            null_rows = int(null_result[0]['empty']) if null_result else 0
            
            # Check for empty strings
            try:
                empty_str_query = f"SELECT COUNT(*) as empty FROM {database}.{table} WHERE toString({column}) = ''"
                empty_str_result = self.run_query(empty_str_query)
                empty_str_rows = int(empty_str_result[0]['empty']) if empty_str_result else 0
            except:
                empty_str_rows = 0
            
            empty_rows = null_rows + empty_str_rows
            
        except Exception as e:
            # Final fallback - just check NULL
            try:
                null_query = f"SELECT COUNT(*) as empty FROM {database}.{table} WHERE {column} IS NULL"
                null_result = self.run_query(null_query)
                empty_rows = int(null_result[0]['empty']) if null_result else 0
            except:
                empty_rows = 0
        
        empty_percentage = (empty_rows / total_rows) * 100 if total_rows > 0 else 0
        return total_rows, empty_rows, empty_percentage
    
    def is_critical_column(self, column_name: str, column_type: str) -> bool:
        """Determine if a column is critical (should not be empty)"""
        critical_patterns = [
            '_id', '_code', 'id', 'code', 'key', 
            'email', 'name', 'title', 'status',
            'currency', 'amount', 'price', 'quantity',
            'date', 'timestamp', 'created', 'updated'
        ]
        
        column_lower = column_name.lower()
        
        # Primary key patterns
        if any(pattern in column_lower for pattern in ['_id', 'id']) and 'String' in column_type:
            return True
            
        # Business critical fields
        if any(pattern in column_lower for pattern in critical_patterns):
            return True
            
        return False
    
    def analyze_database(self, database: str):
        """Analyze all tables in a database for empty columns"""
        print(f"\n🔍 Analyzing {database}...")
        print("=" * 60)
        
        tables = self.get_all_tables(database)
        db_results = {}
        
        for table in tables:
            print(f"📊 Checking {table}...")
            columns = self.get_table_columns(database, table)
            table_results = {}
            
            for column_info in columns:
                column_name = column_info['name']
                column_type = column_info['type']
                
                total, empty, percentage = self.check_column_emptiness(database, table, column_name)
                
                if empty > 0:
                    is_critical = self.is_critical_column(column_name, column_type)
                    table_results[column_name] = {
                        'type': column_type,
                        'total_rows': total,
                        'empty_rows': empty,
                        'empty_percentage': percentage,
                        'is_critical': is_critical
                    }
                    
                    if percentage > 50:  # More than 50% empty
                        print(f"  ⚠️  {column_name}: {empty}/{total} ({percentage:.1f}%) empty" + 
                              (" [CRITICAL]" if is_critical else ""))
                    elif is_critical and empty > 0:
                        print(f"  🔴 {column_name}: {empty}/{total} ({percentage:.1f}%) empty [CRITICAL]")
            
            if table_results:
                db_results[table] = table_results
        
        if db_results:
            self.empty_columns[database] = db_results
    
    def generate_report(self):
        """Generate comprehensive report of empty columns"""
        print(f"\n📋 EMPTY COLUMNS ANALYSIS REPORT")
        print("=" * 80)
        
        total_issues = 0
        critical_issues = 0
        
        for database, tables in self.empty_columns.items():
            print(f"\n🏦 {database.upper()}")
            print("-" * 40)
            
            for table, columns in tables.items():
                has_issues = False
                for column, info in columns.items():
                    if not has_issues:
                        print(f"\n📊 {table}:")
                        has_issues = True
                    
                    status = "🔴 CRITICAL" if info['is_critical'] else "⚠️  WARNING"
                    print(f"  {status}: {column} ({info['type']}) - " +
                          f"{info['empty_rows']}/{info['total_rows']} " +
                          f"({info['empty_percentage']:.1f}%) empty")
                    
                    total_issues += 1
                    if info['is_critical']:
                        critical_issues += 1
        
        print(f"\n📈 SUMMARY:")
        print(f"  • Total empty column issues: {total_issues}")
        print(f"  • Critical issues (need fixing): {critical_issues}")
        print(f"  • Databases affected: {len(self.empty_columns)}")
        
        return critical_issues > 0
    
    def generate_fix_suggestions(self):
        """Generate specific SQL fix suggestions for critical empty columns"""
        print(f"\n🔧 FIX SUGGESTIONS:")
        print("=" * 80)
        
        for database, tables in self.empty_columns.items():
            for table, columns in tables.items():
                critical_columns = {k: v for k, v in columns.items() if v['is_critical']}
                
                if critical_columns:
                    print(f"\n-- Fix {database}.{table}")
                    for column, info in critical_columns.items():
                        if '_id' in column.lower() or column.lower().endswith('id'):
                            print(f"-- Update {column} with generated IDs")
                        elif 'code' in column.lower():
                            print(f"-- Update {column} with generated codes")
                        elif 'currency' in column.lower():
                            print(f"-- Update {column} with default currency values")
                        elif any(x in column.lower() for x in ['name', 'title']):
                            print(f"-- Update {column} with default names/titles")
    
    def run_full_analysis(self):
        """Run complete analysis across all databases"""
        print("🔍 EuroStyle Empty Column Analysis")
        print("=" * 80)
        
        for database in self.databases:
            self.analyze_database(database)
        
        needs_fixes = self.generate_report()
        
        if needs_fixes:
            self.generate_fix_suggestions()
            return True
        else:
            print("\n✅ No critical empty column issues found!")
            return False

def main():
    checker = EmptyColumnChecker()
    needs_fixes = checker.run_full_analysis()
    
    if needs_fixes:
        print(f"\n⚡ Run with --fix parameter to automatically fix critical issues")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()