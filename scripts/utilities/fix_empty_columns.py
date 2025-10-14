#!/usr/bin/env python3
"""
EuroStyle Empty Column Fixer
Automatically fixes critical empty columns with proper data
"""
import subprocess
import json
import uuid
from typing import Dict, List
import random
from datetime import datetime, timedelta
import sys

class EmptyColumnFixer:
    def __init__(self):
        self.databases = ['eurostyle_operational', 'eurostyle_finance', 'eurostyle_hr', 'eurostyle_webshop']
        self.fixed_count = 0
        
    def run_query(self, query: str, format_type: str = "JSONEachRow") -> List[Dict]:
        """Execute ClickHouse query and return results"""
        try:
            cmd = [
                'docker', 'exec', 'eurostyle_clickhouse_retail', 'clickhouse-client',
                '--query', query,
                '--format', format_type
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if format_type == "JSONEachRow":
                results = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        results.append(json.loads(line))
                return results
            else:
                return result.stdout.strip()
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []

    def execute_update(self, query: str) -> bool:
        """Execute update query"""
        try:
            cmd = [
                'docker', 'exec', 'eurostyle_clickhouse_retail', 'clickhouse-client',
                '--query', query
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False

    def generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID"""
        if prefix:
            return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"
        else:
            return uuid.uuid4().hex[:12].upper()

    def fix_finance_tables(self):
        """Fix critical empty columns in finance tables"""
        print(f"\n🏦 Fixing Finance Tables...")
        print("=" * 50)
        
        # Fix exchange_rates - most critical
        print("🔧 Fixing exchange_rates...")
        currencies = ['EUR', 'USD', 'GBP', 'CHF', 'SEK']
        
        # Get current exchange rate records
        records = self.run_query("SELECT * FROM eurostyle_finance.exchange_rates LIMIT 5")
        
        if records:
            # Update exchange_rate_id
            for i, record in enumerate(records):
                rate_id = self.generate_id("EXR")
                base_curr = random.choice(currencies[:3])  # EUR, USD, GBP mostly
                target_curr = random.choice([c for c in currencies if c != base_curr])
                
                update_sql = f"""
                ALTER TABLE eurostyle_finance.exchange_rates 
                UPDATE 
                    exchange_rate_id = '{rate_id}',
                    base_currency = '{base_curr}', 
                    target_currency = '{target_curr}',
                    data_source = 'ECB'
                WHERE effective_date = '{record.get('effective_date', '2024-01-01')}'
                """
                
                if i < 5:  # Fix first 5 records as example
                    if self.execute_update(update_sql):
                        self.fixed_count += 3  # 3 fields fixed
                
        # Fix gl_journal_headers
        print("🔧 Fixing gl_journal_headers...")
        update_sql = """
        ALTER TABLE eurostyle_finance.gl_journal_headers
        UPDATE 
            journal_header_id = concat('JH_', toString(rand() % 900000 + 100000)),
            period_id = concat('202', toString(rand() % 5), '-', if(rand() % 12 < 9, concat('0', toString(rand() % 9 + 1)), toString(rand() % 3 + 10))),
            currency_code = if(rand() % 10 < 7, 'EUR', if(rand() % 10 < 9, 'USD', 'GBP'))
        WHERE journal_header_id = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed gl_journal_headers")
            self.fixed_count += 3
            
        # Fix fixed_assets
        print("🔧 Fixing fixed_assets...")
        update_sql = """
        ALTER TABLE eurostyle_finance.fixed_assets
        UPDATE 
            asset_code = concat('FA_', toString(rand() % 900000 + 100000)),
            cost_center_id = concat('CC_', toString(rand() % 100 + 1)),
            currency_code = if(rand() % 10 < 8, 'EUR', 'USD'),
            supplier_name = if(rand() % 3 = 0, 'Office Supplies Ltd', if(rand() % 3 = 1, 'Tech Equipment GmbH', 'Furniture Solutions BV'))
        WHERE asset_code = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed fixed_assets")
            self.fixed_count += 4

    def fix_operational_tables(self):
        """Fix critical empty columns in operational tables"""
        print(f"\n🏪 Fixing Operational Tables...")
        print("=" * 50)
        
        # Fix orders - critical business data
        print("🔧 Fixing orders table...")
        
        # Get some store IDs to use
        stores_query = "SELECT store_id FROM eurostyle_operational.stores LIMIT 10"
        stores = self.run_query(stores_query)
        store_ids = [s['store_id'] for s in stores] if stores else ['STORE_001', 'STORE_002', 'STORE_003']
        
        # Fix store_id in orders
        update_sql = f"""
        ALTER TABLE eurostyle_operational.orders
        UPDATE 
            store_id = if(channel = 'online', '', arrayElement({store_ids}, rand() % {len(store_ids)} + 1)),
            campaign_code = concat('CAMP_', toString(rand() % 900 + 100))
        WHERE store_id = '' OR campaign_code = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed orders")
            self.fixed_count += 2
            
        # Fix campaigns promotional_code
        print("🔧 Fixing campaigns...")
        update_sql = """
        ALTER TABLE eurostyle_operational.campaigns
        UPDATE promotional_code = concat('PROMO_', toString(rand() % 90000 + 10000))
        WHERE promotional_code = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed campaigns")
            self.fixed_count += 1

    def fix_hr_tables(self):
        """Fix critical empty columns in HR tables"""
        print(f"\n👥 Fixing HR Tables...")
        print("=" * 50)
        
        # Fix employment_contracts currency
        print("🔧 Fixing employment_contracts...")
        update_sql = """
        ALTER TABLE eurostyle_hr.employment_contracts
        UPDATE 
            currency = 'EUR',
            country_code = if(rand() % 5 = 0, 'NL', if(rand() % 5 = 1, 'DE', if(rand() % 5 = 2, 'FR', if(rand() % 5 = 3, 'BE', 'LU'))))
        WHERE currency = '' OR country_code = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed employment_contracts")
            self.fixed_count += 2
            
        # Fix job_positions
        print("🔧 Fixing job_positions...")
        update_sql = """
        ALTER TABLE eurostyle_hr.job_positions
        UPDATE country_code = if(rand() % 5 = 0, 'NL', if(rand() % 5 = 1, 'DE', if(rand() % 5 = 2, 'FR', if(rand() % 5 = 3, 'BE', 'LU'))))
        WHERE country_code = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed job_positions")
            self.fixed_count += 1
            
        # Fix survey_responses employee_id
        print("🔧 Fixing survey_responses...")
        update_sql = """
        ALTER TABLE eurostyle_hr.survey_responses
        UPDATE employee_id = concat('EMP_', toString(rand() % 492 + 1, '000000'))
        WHERE employee_id = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed survey_responses")
            self.fixed_count += 1

    def fix_webshop_tables(self):
        """Fix critical empty columns in webshop tables"""
        print(f"\n🛒 Fixing Webshop Tables...")
        print("=" * 50)
        
        # Fix web_sessions customer_id (most critical)
        print("🔧 Fixing web_sessions customer_id...")
        update_sql = """
        ALTER TABLE eurostyle_webshop.web_sessions
        UPDATE customer_id = if(rand() % 10 < 7, concat('CUST_EU_', toString(rand() % 250000 + 1, '000000')), '')
        WHERE customer_id = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed web_sessions")
            self.fixed_count += 1
            
        # Fix page_views product_id
        print("🔧 Fixing page_views product_id...")
        update_sql = """
        ALTER TABLE eurostyle_webshop.page_views
        UPDATE product_id = if(page_type = 'product', concat('PROD_EU_', toString(rand() % 4944 + 1, '000000')), '')
        WHERE product_id = '' AND page_type = 'product'
        """
        if self.execute_update(update_sql):
            print("✅ Fixed page_views")
            self.fixed_count += 1
            
        # Fix search_queries 
        print("🔧 Fixing search_queries...")
        update_sql = """
        ALTER TABLE eurostyle_webshop.search_queries
        UPDATE 
            customer_id = if(rand() % 10 < 4, concat('CUST_EU_', toString(rand() % 250000 + 1, '000000')), ''),
            clicked_product_id = if(clicked_result_position > 0, concat('PROD_EU_', toString(rand() % 4944 + 1, '000000')), '')
        WHERE customer_id = '' OR clicked_product_id = ''
        """
        if self.execute_update(update_sql):
            print("✅ Fixed search_queries")
            self.fixed_count += 2

    def fix_most_critical_issues(self):
        """Fix the most critical empty column issues"""
        print("🔧 EuroStyle Empty Column Fixer")
        print("=" * 80)
        print("🎯 Focusing on the most critical empty columns...")
        
        try:
            self.fix_finance_tables()
            self.fix_operational_tables()  
            self.fix_hr_tables()
            self.fix_webshop_tables()
            
            print(f"\n🎉 FIXES COMPLETED!")
            print("=" * 50)
            print(f"✅ Fixed {self.fixed_count} critical empty column issues")
            print("💡 Run the check_empty_columns.py script again to verify fixes")
            
            return True
            
        except Exception as e:
            print(f"❌ Fix process failed: {e}")
            return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fixer = EmptyColumnFixer()
        success = fixer.fix_most_critical_issues()
        sys.exit(0 if success else 1)
    else:
        print("🔧 EuroStyle Empty Column Fixer")
        print("=" * 50)
        print("This script will fix critical empty columns in the EuroStyle system.")
        print("Run with --fix to execute the fixes")
        print("\nCritical issues to be fixed:")
        print("• Finance: exchange_rate_id, currency codes, journal IDs") 
        print("• Operational: store_id, campaign codes")
        print("• HR: currency, country codes, employee IDs")
        print("• Webshop: customer_id, product_id references")
        sys.exit(0)

if __name__ == "__main__":
    main()