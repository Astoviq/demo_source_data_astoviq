#!/bin/bash

# EuroStyle Fashion - Create Webshop Tables Script
echo "🛍️ Creating EuroStyle webshop database tables..."

# Database connection details
DB_HOST="localhost"
DB_PORT="9002"
DB_NAME="eurostyle_operational"
DB_USER="eurostyle_user"
DB_PASS="eurostyle_demo_2024"

# Function to execute ClickHouse SQL
execute_sql() {
    local sql="$1"
    local table_name="$2"
    
    echo "Creating table: $table_name"
    docker exec eurostyle_clickhouse_retail clickhouse-client \
        --user=$DB_USER \
        --password=$DB_PASS \
        --database=$DB_NAME \
        --query="$sql"
    
    if [ $? -eq 0 ]; then
        echo "✅ $table_name created successfully"
    else
        echo "❌ Failed to create $table_name"
        exit 1
    fi
}

# Create Page Views Table
execute_sql "CREATE TABLE IF NOT EXISTS page_views (
    page_view_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    page_type String,
    page_url String,
    page_title String,
    product_id Nullable(String),
    category_l1 Nullable(String),
    category_l2 Nullable(String),
    view_timestamp DateTime,
    time_on_page_seconds UInt16,
    scroll_depth_percent UInt8,
    click_events UInt8,
    is_mobile Bool,
    referrer_page Nullable(String),
    exit_page Bool,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, view_timestamp, session_id)" "page_views"

# Create Cart Activities Table
execute_sql "CREATE TABLE IF NOT EXISTS cart_activities (
    cart_activity_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    activity_type String,
    product_id String,
    size String,
    color String,
    quantity_before UInt16,
    quantity_after UInt16,
    unit_price_eur Decimal(18, 2),
    activity_timestamp DateTime,
    cart_total_items UInt16,
    cart_total_value_eur Decimal(18, 2),
    product_position_in_list Nullable(UInt16),
    recommendation_type Nullable(String),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, activity_timestamp, session_id)" "cart_activities"

# Create Search Queries Table
execute_sql "CREATE TABLE IF NOT EXISTS search_queries (
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
ORDER BY (country_code, search_timestamp, session_id)" "search_queries"

# Create Product Reviews Table
execute_sql "CREATE TABLE IF NOT EXISTS product_reviews (
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
ORDER BY (product_id, review_date, review_id)" "product_reviews"

# Create Wishlist Items Table
execute_sql "CREATE TABLE IF NOT EXISTS wishlist_items (
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
ORDER BY (customer_id, added_date, wishlist_item_id)" "wishlist_items"

# Create Web Analytics Events Table
execute_sql "CREATE TABLE IF NOT EXISTS web_analytics_events (
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
ORDER BY (country_code, event_timestamp, session_id)" "web_analytics_events"

echo "🎉 All webshop tables created successfully!"
echo "📊 Checking created tables..."

# List all tables to verify
docker exec eurostyle_clickhouse_retail clickhouse-client \
    --user=$DB_USER \
    --password=$DB_PASS \
    --database=$DB_NAME \
    --query="SELECT table AS table_name, total_rows FROM system.tables WHERE database = 'eurostyle_operational' ORDER BY table_name"