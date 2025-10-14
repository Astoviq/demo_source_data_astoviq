#!/usr/bin/env python3
"""
Quick data status checker for EuroStyle ClickHouse databases
"""
import sys
import os
import clickhouse_connect

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_data_status():
    """Check data volumes across all databases"""
    try:
        client = clickhouse_connect.get_client(
            host='localhost', 
            port=8124,
            username='eurostyle_user',
            password='eurostyle_demo_2024'
        )
        
        databases = ['eurostyle_operational', 'eurostyle_webshop', 'eurostyle_finance', 'eurostyle_hr']
        
        print("📊 EuroStyle Data Status Check")
        print("=" * 50)
        
        total_records = 0
        for db in databases:
            print(f"\n🏢 {db.replace('eurostyle_', '').upper()} DATABASE:")
            try:
                # Get all tables for this database
                tables = client.query(f"SHOW TABLES FROM {db}").result_rows
                db_total = 0
                
                for table_row in tables:
                    table_name = table_row[0]
                    try:
                        count = client.query(f"SELECT count() FROM {db}.{table_name}").result_rows[0][0]
                        db_total += count
                        print(f"   • {table_name}: {count:,} records")
                    except Exception as e:
                        print(f"   • {table_name}: ERROR - {str(e)}")
                
                print(f"   📋 Database Total: {db_total:,} records")
                total_records += db_total
                
            except Exception as e:
                print(f"   ❌ Database access error: {str(e)}")
        
        print(f"\n🎯 GRAND TOTAL: {total_records:,} records across all databases")
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    check_data_status()