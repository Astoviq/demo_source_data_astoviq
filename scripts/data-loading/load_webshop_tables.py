#!/usr/bin/env python3
"""
Load complete webshop tables into ClickHouse database

Creates all missing tables and loads the generated CSV data.
"""

import subprocess
import sys
from pathlib import Path

def run_clickhouse_query(query, database="eurostyle_webshop"):
    """Execute a ClickHouse query"""
    cmd = [
        "docker", "exec", "eurostyle_clickhouse_retail",
        "clickhouse-client", "--database", database,
        "--query", query
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing query: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_tables():
    """Create all webshop tables"""
    
    tables = {
        "search_queries": """
            CREATE TABLE IF NOT EXISTS search_queries (
                search_query_id String,
                session_id String,
                customer_id Nullable(String),
                country_code String,
                search_term String,
                search_timestamp DateTime,
                results_count UInt32,
                clicked_result_position Nullable(UInt16),
                clicked_product_id Nullable(String),
                filters_applied Array(String),
                sort_order String,
                search_refinements UInt8,
                no_results Bool,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (country_code, search_timestamp, session_id);
        """,
        
        "product_reviews": """
            CREATE TABLE IF NOT EXISTS product_reviews (
                review_id String,
                product_id String,
                customer_id String,
                country_code String,
                rating UInt8,
                review_title String,
                review_text String,
                review_date Date,
                verified_purchase Bool,
                helpful_votes UInt16,
                total_votes UInt16,
                size_purchased Nullable(String),
                color_purchased Nullable(String),
                fit_rating Nullable(String),
                quality_rating Nullable(UInt8),
                style_rating Nullable(UInt8),
                review_status String,
                moderated_by Nullable(String),
                created_at DateTime DEFAULT now(),
                updated_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (product_id, review_date, review_id);
        """,
        
        "wishlist_items": """
            CREATE TABLE IF NOT EXISTS wishlist_items (
                wishlist_item_id String,
                customer_id String,
                product_id String,
                country_code String,
                size Nullable(String),
                color Nullable(String),
                added_date DateTime,
                added_from_page String,
                priority Nullable(String),
                price_when_added_eur Decimal(18, 2),
                current_price_eur Decimal(18, 2),
                price_alert_enabled Bool,
                in_stock Bool,
                purchased Bool,
                purchase_date Nullable(Date),
                removed_date Nullable(DateTime),
                created_at DateTime DEFAULT now(),
                updated_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (customer_id, added_date, wishlist_item_id);
        """,
        
        "web_analytics_events": """
            CREATE TABLE IF NOT EXISTS web_analytics_events (
                event_id String,
                session_id String,
                customer_id Nullable(String),
                country_code String,
                event_type String,
                event_category String,
                event_action String,
                event_label Nullable(String),
                event_value Nullable(Decimal(18, 2)),
                page_url String,
                element_selector Nullable(String),
                element_text Nullable(String),
                event_timestamp DateTime,
                user_journey_step UInt16,
                ab_test_variant Nullable(String),
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (country_code, event_timestamp, session_id);
        """,
        
        "email_marketing": """
            CREATE TABLE IF NOT EXISTS email_marketing (
                email_event_id String,
                customer_id String,
                country_code String,
                campaign_id String,
                email_type String,
                email_subject String,
                event_type String,
                event_timestamp DateTime,
                email_template_id Nullable(String),
                clicked_link_url Nullable(String),
                device_type Nullable(String),
                email_client Nullable(String),
                conversion_value_eur Nullable(Decimal(18, 2)),
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (country_code, event_timestamp, customer_id);
        """,
        
        "product_recommendations": """
            CREATE TABLE IF NOT EXISTS product_recommendations (
                recommendation_id String,
                session_id String,
                customer_id Nullable(String),
                country_code String,
                recommendation_type String,
                source_product_id Nullable(String),
                recommended_product_id String,
                recommendation_position UInt8,
                page_context String,
                algorithm_version String,
                confidence_score Decimal(5, 4),
                shown_timestamp DateTime,
                clicked Bool,
                clicked_timestamp Nullable(DateTime),
                added_to_cart Bool,
                purchased Bool,
                revenue_eur Nullable(Decimal(18, 2)),
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (country_code, shown_timestamp, session_id);
        """,
        
        "ab_test_results": """
            CREATE TABLE IF NOT EXISTS ab_test_results (
                ab_test_id String,
                session_id String,
                customer_id Nullable(String),
                country_code String,
                test_name String,
                variant String,
                assignment_timestamp DateTime,
                conversion_goal String,
                converted Bool,
                conversion_timestamp Nullable(DateTime),
                conversion_value_eur Nullable(Decimal(18, 2)),
                page_views_in_test UInt16,
                time_to_conversion_seconds Nullable(UInt32),
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (test_name, assignment_timestamp, session_id);
        """
    }
    
    print("Creating webshop tables...")
    for table_name, create_sql in tables.items():
        print(f"  Creating {table_name}...")
        result = run_clickhouse_query(create_sql)
        if result is None:
            print(f"    ❌ Failed to create {table_name}")
            return False
        else:
            print(f"    ✅ Created {table_name}")
    
    return True

def load_csv_data():
    """Load CSV data into tables"""
    
    csv_files = [
        'eurostyle_webshop.cart_activities.csv',
        'eurostyle_webshop.search_queries.csv', 
        'eurostyle_webshop.product_reviews.csv',
        'eurostyle_webshop.wishlist_items.csv',
        'eurostyle_webshop.web_analytics_events.csv',
        'eurostyle_webshop.email_marketing.csv',
        'eurostyle_webshop.product_recommendations.csv',
        'eurostyle_webshop.ab_test_results.csv'
    ]
    
    print("\nLoading CSV data into tables...")
    
    for csv_file in csv_files:
        csv_path = Path(f'generated_data/{csv_file}')
        if not csv_path.exists():
            print(f"  ⚠️  CSV file not found: {csv_file}")
            continue
            
        table_name = csv_file.replace('eurostyle_webshop.', '').replace('.csv', '')
        
        print(f"  Loading {table_name} from {csv_file}...")
        
        # Copy CSV to container
        copy_cmd = ["docker", "cp", str(csv_path), f"eurostyle_clickhouse_retail:/tmp/{csv_file}"]
        result = subprocess.run(copy_cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"    ❌ Failed to copy {csv_file} to container")
            continue
        
        # Load data using ClickHouse
        load_query = f"""
        INSERT INTO {table_name} 
        SELECT * FROM file('/tmp/{csv_file}', 'CSVWithNames')
        """
        
        result = run_clickhouse_query(load_query)
        if result is None:
            print(f"    ❌ Failed to load data into {table_name}")
        else:
            # Get row count
            count_result = run_clickhouse_query(f"SELECT count() FROM {table_name}")
            print(f"    ✅ Loaded {count_result} rows into {table_name}")

def verify_tables():
    """Verify all tables exist and have data"""
    print("\nVerifying tables...")
    
    tables_result = run_clickhouse_query("SHOW TABLES")
    if tables_result:
        tables = tables_result.split('\n')
        print(f"  Found {len(tables)} tables: {', '.join(tables)}")
        
        print("\nTable row counts:")
        for table in sorted(tables):
            count = run_clickhouse_query(f"SELECT count() FROM {table}")
            size_mb = float(run_clickhouse_query(f"SELECT formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE table = '{table}' AND database = 'eurostyle_webshop'") or "0")
            print(f"    {table}: {count:>10} rows")

def main():
    print("🚀 Setting up complete EuroStyle webshop database...")
    
    # Create missing tables
    if not create_tables():
        print("❌ Failed to create tables")
        sys.exit(1)
    
    # Load data
    load_csv_data()
    
    # Verify everything
    verify_tables()
    
    print("\n✅ Webshop database setup complete!")
    print("\nAll 10 webshop analytics tables are now available:")
    print("  1. web_sessions")
    print("  2. page_views") 
    print("  3. cart_activities")
    print("  4. search_queries")
    print("  5. product_reviews")
    print("  6. wishlist_items")
    print("  7. web_analytics_events")
    print("  8. email_marketing")
    print("  9. product_recommendations")
    print("  10. ab_test_results")

if __name__ == "__main__":
    main()