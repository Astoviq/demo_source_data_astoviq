#!/usr/bin/env python3
"""
Comprehensive Data Quality Analysis for EuroStyle Fashion
=======================================================
Analyzes all tables across all 5 databases for:
- Empty tables
- Empty columns 
- Poor value distribution (uniform/repetitive values)
- Missing required business data
- Cross-database consistency issues

Follows WARP.md guidelines for systematic analysis and reporting.
"""

import sys
import subprocess
import json
import yaml
from collections import defaultdict, Counter
from pathlib import Path

class EuroStyleDataQualityAnalyzer:
    def __init__(self):
        self.container_name = "eurostyle_clickhouse_retail"
        self.databases = [
            "eurostyle_operational",
            "eurostyle_finance", 
            "eurostyle_hr",
            "eurostyle_webshop",
            "eurostyle_pos"
        ]
        self.analysis_results = {
            'empty_tables': [],
            'empty_columns': [],
            'poor_distribution': [],
            'missing_data_patterns': [],
            'cross_database_issues': [],
            'summary_stats': {}
        }
        
    def execute_clickhouse_query(self, query, database=None):
        """Execute ClickHouse query and return results"""
        try:
            cmd = ["docker", "exec", self.container_name, "clickhouse-client", "--format", "TabSeparated"]
            if database:
                cmd.extend(["--database", database])
            cmd.extend(["--query", query])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError as e:
            print(f"❌ Query failed: {e.stderr}")
            return []
    
    def get_all_tables(self):
        """Get all tables across all databases"""
        tables_by_db = {}
        
        for db in self.databases:
            query = f"""
            SELECT name, engine, total_rows
            FROM system.tables 
            WHERE database = '{db}' 
            AND engine NOT LIKE '%View%'
            ORDER BY name
            """
            
            results = self.execute_clickhouse_query(query)
            tables = []
            
            for row in results:
                if row.strip():
                    parts = row.split('\t')
                    if len(parts) >= 3:
                        table_name, engine, total_rows = parts[0], parts[1], parts[2]
                        tables.append({
                            'name': table_name,
                            'engine': engine, 
                            'total_rows': int(total_rows) if total_rows.isdigit() else 0
                        })
            
            tables_by_db[db] = tables
            
        return tables_by_db
    
    def get_table_columns(self, database, table):
        """Get column information for a specific table"""
        query = f"""
        SELECT name, type, default_kind
        FROM system.columns 
        WHERE database = '{database}' AND table = '{table}'
        ORDER BY position
        """
        
        results = self.execute_clickhouse_query(query)
        columns = []
        
        for row in results:
            if row.strip():
                parts = row.split('\t')
                if len(parts) >= 2:
                    col_name, col_type = parts[0], parts[1]
                    default_kind = parts[2] if len(parts) > 2 else ""
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'default_kind': default_kind
                    })
        
        return columns
    
    def analyze_empty_tables(self, tables_by_db):
        """Find completely empty tables"""
        print("🔍 Analyzing empty tables...")
        
        empty_tables = []
        
        for db, tables in tables_by_db.items():
            for table in tables:
                # Skip ClickHouse internal/system tables with problematic names
                if '.inner_id.' in table['name'] or table['name'].startswith('.'):
                    continue
                    
                if table['total_rows'] == 0:
                    empty_tables.append({
                        'database': db,
                        'table': table['name'],
                        'engine': table['engine']
                    })
        
        self.analysis_results['empty_tables'] = empty_tables
        
        if empty_tables:
            print(f"⚠️  Found {len(empty_tables)} empty tables:")
            for empty in empty_tables:
                print(f"   • {empty['database']}.{empty['table']} ({empty['engine']})")
        else:
            print("✅ No empty tables found")
    
    def analyze_column_quality(self, tables_by_db):
        """Analyze column-level data quality"""
        print("🔍 Analyzing column data quality...")
        
        empty_columns = []
        poor_distribution = []
        
        for db, tables in tables_by_db.items():
            for table in tables:
                # Skip ClickHouse internal/system tables with problematic names
                if '.inner_id.' in table['name'] or table['name'].startswith('.'):
                    continue
                    
                if table['total_rows'] > 0:  # Only analyze tables with data
                    print(f"   Analyzing {db}.{table['name']} ({table['total_rows']} rows)...")
                    
                    try:
                        columns = self.get_table_columns(db, table['name'])
                        
                        for column in columns:
                            try:
                                # Check for empty columns - escape table name properly
                                table_ref = f"`{db}`.`{table['name']}`"
                                column_ref = f"`{column['name']}`"
                                
                                null_count_query = f"""
                                SELECT count(*) as total, 
                                       countIf({column_ref} IS NULL OR {column_ref} = '') as nulls
                                FROM {table_ref}
                                """
                                
                                null_results = self.execute_clickhouse_query(null_count_query)
                                if null_results and null_results[0]:
                                    parts = null_results[0].split('\t')
                                    if len(parts) >= 2:
                                        total, nulls = int(parts[0]), int(parts[1])
                                        
                                        null_percentage = (nulls / total * 100) if total > 0 else 0
                                        
                                        # Flag columns that are mostly empty
                                        if null_percentage > 80:
                                            empty_columns.append({
                                                'database': db,
                                                'table': table['name'],
                                                'column': column['name'],
                                                'null_percentage': round(null_percentage, 2),
                                                'total_rows': total
                                            })
                                        
                                        # Check for poor distribution (only for string/text columns with reasonable row counts)
                                        if total > 10 and 'String' in column['type']:
                                            distinct_query = f"""
                                            SELECT count() as total,
                                                   uniqExact({column_ref}) as distinct_values
                                            FROM {table_ref}
                                            WHERE {column_ref} IS NOT NULL AND {column_ref} != ''
                                            """
                                            
                                            distinct_results = self.execute_clickhouse_query(distinct_query)
                                            if distinct_results and distinct_results[0]:
                                                parts = distinct_results[0].split('\t')
                                                if len(parts) >= 2:
                                                    non_null_total, distinct_count = int(parts[0]), int(parts[1])
                                                    
                                                    if non_null_total > 0:
                                                        uniqueness_ratio = distinct_count / non_null_total
                                                        
                                                        # Flag columns with very poor distribution
                                                        if uniqueness_ratio < 0.1 and distinct_count < 10 and non_null_total > 50:
                                                            # Get most common values
                                                            common_values_query = f"""
                                                            SELECT {column_ref}, count() as cnt
                                                            FROM {table_ref}
                                                            WHERE {column_ref} IS NOT NULL AND {column_ref} != ''
                                                            GROUP BY {column_ref}
                                                            ORDER BY cnt DESC
                                                            LIMIT 3
                                                            """
                                                            
                                                            common_results = self.execute_clickhouse_query(common_values_query)
                                                            common_values = []
                                                            for row in common_results:
                                                                if row.strip():
                                                                    parts = row.split('\t')
                                                                    if len(parts) >= 2:
                                                                        value, count = parts[0], int(parts[1])
                                                                        common_values.append({'value': value, 'count': count})
                                                            
                                                            poor_distribution.append({
                                                                'database': db,
                                                                'table': table['name'],
                                                                'column': column['name'],
                                                                'uniqueness_ratio': round(uniqueness_ratio, 3),
                                                                'distinct_values': distinct_count,
                                                                'total_non_null': non_null_total,
                                                                'common_values': common_values
                                                            })
                            except Exception as e:
                                # Skip problematic columns
                                print(f"     Skipping column {column['name']}: {str(e)[:50]}...")
                                continue
                    except Exception as e:
                        print(f"     Skipping table {table['name']}: {str(e)[:50]}...")
                        continue
        
        self.analysis_results['empty_columns'] = empty_columns
        self.analysis_results['poor_distribution'] = poor_distribution
        
        if empty_columns:
            print(f"⚠️  Found {len(empty_columns)} mostly empty columns:")
            for col in empty_columns[:10]:  # Show first 10
                print(f"   • {col['database']}.{col['table']}.{col['column']} ({col['null_percentage']}% null)")
        
        if poor_distribution:
            print(f"⚠️  Found {len(poor_distribution)} columns with poor value distribution:")
            for col in poor_distribution[:10]:  # Show first 10
                print(f"   • {col['database']}.{col['table']}.{col['column']} ({col['distinct_values']} unique in {col['total_non_null']} rows)")
    
    def analyze_business_data_patterns(self, tables_by_db):
        """Analyze business-specific data patterns and missing expected data"""
        print("🔍 Analyzing business data patterns...")
        
        missing_patterns = []
        
        # Expected business data patterns per database
        expected_patterns = {
            'eurostyle_operational': {
                'customers': ['email', 'phone', 'country_code', 'registration_date'],
                'products': ['price_eur', 'category_l1', 'brand', 'stock_quantity'],
                'orders': ['customer_id', 'total_amount_eur', 'order_status', 'payment_method']
            },
            'eurostyle_finance': {
                'gl_journal_headers': ['journal_type', 'transaction_date', 'total_amount'],
                'gl_journal_lines': ['account_id', 'debit_amount', 'credit_amount'],
                'legal_entities': ['entity_code', 'country_code', 'entity_type']
            },
            'eurostyle_hr': {
                'employees': ['first_name', 'last_name', 'hire_date', 'annual_salary_eur'],
                'departments': ['department_name', 'manager_id', 'budget_eur']
            },
            'eurostyle_webshop': {
                'web_sessions': ['customer_id', 'session_start', 'page_views', 'device_type'],
                'page_views': ['session_id', 'page_url', 'timestamp']
            },
            'eurostyle_pos': {
                'transactions': ['transaction_id', 'store_id', 'total_amount_eur', 'payment_method'],
                'transaction_items': ['transaction_id', 'product_id', 'quantity', 'unit_price_eur']
            }
        }
        
        # Check for missing expected tables and columns
        for db, expected_tables in expected_patterns.items():
            if db in tables_by_db:
                existing_table_names = [t['name'] for t in tables_by_db[db]]
                
                for expected_table, expected_columns in expected_tables.items():
                    if expected_table not in existing_table_names:
                        missing_patterns.append({
                            'type': 'missing_table',
                            'database': db,
                            'table': expected_table,
                            'description': f'Expected business table {expected_table} not found'
                        })
                    else:
                        # Check if table has data and expected columns
                        table_info = next((t for t in tables_by_db[db] if t['name'] == expected_table), None)
                        if table_info and table_info['total_rows'] > 0:
                            actual_columns = [c['name'] for c in self.get_table_columns(db, expected_table)]
                            
                            for expected_col in expected_columns:
                                if expected_col not in actual_columns:
                                    missing_patterns.append({
                                        'type': 'missing_column',
                                        'database': db,
                                        'table': expected_table,
                                        'column': expected_col,
                                        'description': f'Expected business column {expected_col} not found'
                                    })
        
        self.analysis_results['missing_data_patterns'] = missing_patterns
        
        if missing_patterns:
            print(f"⚠️  Found {len(missing_patterns)} missing business data patterns:")
            for pattern in missing_patterns[:10]:
                print(f"   • {pattern['type']}: {pattern['description']}")
    
    def generate_summary_stats(self, tables_by_db):
        """Generate overall summary statistics"""
        total_tables = sum(len(tables) for tables in tables_by_db.values())
        total_rows = sum(sum(t['total_rows'] for t in tables) for tables in tables_by_db.values())
        empty_table_count = len(self.analysis_results['empty_tables'])
        empty_column_count = len(self.analysis_results['empty_columns'])
        poor_distribution_count = len(self.analysis_results['poor_distribution'])
        
        self.analysis_results['summary_stats'] = {
            'total_databases': len(self.databases),
            'total_tables': total_tables,
            'total_rows': total_rows,
            'empty_tables': empty_table_count,
            'empty_columns': empty_column_count,
            'poor_distribution_columns': poor_distribution_count,
            'missing_business_patterns': len(self.analysis_results['missing_data_patterns'])
        }
    
    def save_analysis_report(self):
        """Save detailed analysis report"""
        timestamp = subprocess.run(['date', '+%Y%m%d_%H%M%S'], capture_output=True, text=True).stdout.strip()
        report_file = Path(f"data/validation/data_quality_analysis_{timestamp}.yaml")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            yaml.dump(self.analysis_results, f, default_flow_style=False, sort_keys=False)
        
        print(f"📄 Detailed analysis report saved: {report_file}")
        return report_file
    
    def print_summary_report(self):
        """Print concise summary report"""
        stats = self.analysis_results['summary_stats']
        
        print("\n" + "="*60)
        print("📊 EUROSTYLE DATA QUALITY ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n🏛️  **DATABASE OVERVIEW**")
        print(f"   • Total Databases: {stats['total_databases']}")
        print(f"   • Total Tables: {stats['total_tables']}")  
        print(f"   • Total Records: {stats['total_rows']:,}")
        
        print(f"\n⚠️  **ISSUES IDENTIFIED**")
        print(f"   • Empty Tables: {stats['empty_tables']}")
        print(f"   • Empty Columns: {stats['empty_columns']}")
        print(f"   • Poor Distribution Columns: {stats['poor_distribution_columns']}")
        print(f"   • Missing Business Patterns: {stats['missing_business_patterns']}")
        
        if stats['empty_tables'] > 0:
            print(f"\n📋 **TOP EMPTY TABLES**")
            for empty in self.analysis_results['empty_tables'][:5]:
                print(f"   • {empty['database']}.{empty['table']}")
        
        if stats['poor_distribution_columns'] > 0:
            print(f"\n📋 **TOP POOR DISTRIBUTION COLUMNS**")
            for poor in self.analysis_results['poor_distribution'][:5]:
                print(f"   • {poor['database']}.{poor['table']}.{poor['column']} ({poor['distinct_values']} unique)")
        
        if stats['missing_business_patterns'] > 0:
            print(f"\n📋 **MISSING BUSINESS PATTERNS**")
            for missing in self.analysis_results['missing_data_patterns'][:5]:
                print(f"   • {missing['type']}: {missing.get('table', 'N/A')}.{missing.get('column', 'N/A')}")
        
        print(f"\n💡 **RECOMMENDATIONS**")
        if stats['empty_tables'] > 0:
            print(f"   • Investigate why {stats['empty_tables']} tables are empty")
        if stats['poor_distribution_columns'] > 0:
            print(f"   • Improve data generation for {stats['poor_distribution_columns']} columns with poor distribution")
        if stats['missing_business_patterns'] > 0:
            print(f"   • Add missing expected business tables/columns")
        
        print("="*60)
    
    def run_analysis(self):
        """Run complete data quality analysis"""
        print("🚀 Starting comprehensive data quality analysis...")
        print(f"📊 Analyzing {len(self.databases)} databases: {', '.join(self.databases)}")
        
        # Get all tables across databases
        tables_by_db = self.get_all_tables()
        
        # Run all analysis components
        self.analyze_empty_tables(tables_by_db)
        self.analyze_column_quality(tables_by_db)
        self.analyze_business_data_patterns(tables_by_db)
        self.generate_summary_stats(tables_by_db)
        
        # Generate reports
        report_file = self.save_analysis_report()
        self.print_summary_report()
        
        return report_file

def main():
    try:
        analyzer = EuroStyleDataQualityAnalyzer()
        report_file = analyzer.run_analysis()
        
        print(f"\n✅ Analysis complete! See detailed report: {report_file}")
        
        # Return analysis results for further processing
        return analyzer.analysis_results
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()