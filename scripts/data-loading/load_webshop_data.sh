#!/bin/bash
# Load webshop CSV data into ClickHouse

echo "🚀 Loading webshop data into ClickHouse..."

# Copy CSV files to ClickHouse user_files directory
echo "Copying CSV files to container..."
docker cp data/csv/eurostyle_webshop.cart_activities.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.search_queries.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.product_reviews.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.wishlist_items.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.web_analytics_events.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.email_marketing.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.product_recommendations.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/
docker cp data/csv/eurostyle_webshop.ab_test_results.csv eurostyle_clickhouse_retail:/var/lib/clickhouse/user_files/

echo "Loading data into tables..."

# Load cart_activities
echo "Loading cart_activities..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO cart_activities SELECT * FROM file('eurostyle_webshop.cart_activities.csv', 'CSVWithNames')"

# Load search_queries  
echo "Loading search_queries..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO search_queries SELECT * FROM file('eurostyle_webshop.search_queries.csv', 'CSVWithNames')"

# Load product_reviews
echo "Loading product_reviews..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO product_reviews SELECT * FROM file('eurostyle_webshop.product_reviews.csv', 'CSVWithNames')"

# Load wishlist_items
echo "Loading wishlist_items..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO wishlist_items SELECT * FROM file('eurostyle_webshop.wishlist_items.csv', 'CSVWithNames')"

# Load web_analytics_events
echo "Loading web_analytics_events..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO web_analytics_events SELECT * FROM file('eurostyle_webshop.web_analytics_events.csv', 'CSVWithNames')"

# Load email_marketing
echo "Loading email_marketing..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO email_marketing SELECT * FROM file('eurostyle_webshop.email_marketing.csv', 'CSVWithNames')"

# Load product_recommendations
echo "Loading product_recommendations..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO product_recommendations SELECT * FROM file('eurostyle_webshop.product_recommendations.csv', 'CSVWithNames')"

# Load ab_test_results
echo "Loading ab_test_results..."
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="INSERT INTO ab_test_results SELECT * FROM file('eurostyle_webshop.ab_test_results.csv', 'CSVWithNames')"

echo "Verifying data load..."

# Check table counts
docker exec eurostyle_clickhouse_retail clickhouse-client --database=eurostyle_webshop --query="
SELECT 
    table,
    formatReadableQuantity(total_rows) as rows 
FROM system.tables 
WHERE database = 'eurostyle_webshop' 
ORDER BY total_rows DESC"

echo "✅ Webshop data loading complete!"