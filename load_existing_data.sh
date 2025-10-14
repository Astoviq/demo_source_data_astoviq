#!/bin/bash

# Quick data loader for existing CSV files
# This loads the CSV files that were already generated

echo "🚀 Loading existing CSV data into ClickHouse..."

BASE_URL="http://localhost:8124/?user=eurostyle_user&password=eurostyle_demo_2024"
DATA_DIR="data-generator/generated_data"

# Function to load CSV file
load_csv() {
    local file="$1"
    local table="$2"
    
    if [[ -f "$DATA_DIR/$file" ]]; then
        echo "📊 Loading $file into $table..."
        cat "$DATA_DIR/$file" | curl -s "$BASE_URL&query=INSERT INTO eurostyle_operational.$table FORMAT CSV" --data-binary @- 
        
        # Check count
        count=$(echo "SELECT COUNT(*) FROM eurostyle_operational.$table;" | curl -s "$BASE_URL" --data-binary @-)
        echo "✅ Loaded $count records into $table"
    else
        echo "❌ File $file not found"
    fi
}

# Load the CSV files we have
load_csv "european_geography.csv" "european_geography"
load_csv "fashion_calendar.csv" "fashion_calendar"
load_csv "stores.csv" "stores"
load_csv "products.csv" "products"
load_csv "campaigns.csv" "campaigns"
load_csv "customers.csv" "customers"
load_csv "inventory.csv" "inventory"

echo "✅ Data loading complete!"

# Show summary
echo ""
echo "📊 Database summary:"
echo "SELECT 'customers' as table, COUNT(*) as records FROM eurostyle_operational.customers
UNION ALL SELECT 'products', COUNT(*) FROM eurostyle_operational.products
UNION ALL SELECT 'stores', COUNT(*) FROM eurostyle_operational.stores
UNION ALL SELECT 'campaigns', COUNT(*) FROM eurostyle_operational.campaigns
UNION ALL SELECT 'inventory', COUNT(*) FROM eurostyle_operational.inventory;" | curl -s "$BASE_URL" --data-binary @-