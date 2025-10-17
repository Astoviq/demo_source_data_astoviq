#!/bin/bash
set -e

# EuroStyle Source - CSV Data Loader
# Loads generated CSV files into ClickHouse databases
# Following WARP.md configuration-driven approach

CLICKHOUSE_HOST="localhost"
CLICKHOUSE_PORT="8124"
CSV_DIR="data/csv"
CLICKHOUSE_CLIENT="docker exec eurostyle_clickhouse_retail clickhouse-client"

echo "🚀 Loading CSV data into ClickHouse databases..."

# Function to load CSV data
load_csv_data() {
    local database=$1
    local table=$2
    local csv_file=$3
    
    echo "📥 Loading $csv_file into $database.$table"
    
    # Check if file exists
    if [[ ! -f "$csv_file" ]]; then
        echo "⚠️  File not found: $csv_file, skipping..."
        return
    fi
    
    # Load data using CSVWithNames input format (ClickHouse will match columns by header names)
    if [[ $csv_file == *.gz ]]; then
        # Compressed file
        gunzip -c "$csv_file" | $CLICKHOUSE_CLIENT --query="INSERT INTO $database.$table FORMAT CSVWithNames"
    else
        # Uncompressed file
        cat "$csv_file" | $CLICKHOUSE_CLIENT --query="INSERT INTO $database.$table FORMAT CSVWithNames"
    fi
    
    # Get row count
    local count=$($CLICKHOUSE_CLIENT --query="SELECT count(*) FROM $database.$table")
    echo "✅ Loaded $count rows into $database.$table"
}

# Load operational database
echo "📍 Loading eurostyle_operational database..."
load_csv_data "eurostyle_operational" "stores" "$CSV_DIR/eurostyle_operational.stores.csv.gz"
load_csv_data "eurostyle_operational" "products" "$CSV_DIR/eurostyle_operational.products.csv.gz" 
load_csv_data "eurostyle_operational" "customers" "$CSV_DIR/eurostyle_operational.customers.csv.gz"
load_csv_data "eurostyle_operational" "orders" "$CSV_DIR/eurostyle_operational.orders.csv.gz"

# Load finance database  
echo "📍 Loading eurostyle_finance database..."
load_csv_data "eurostyle_finance" "legal_entities" "$CSV_DIR/eurostyle_finance.legal_entities.csv.gz"
load_csv_data "eurostyle_finance" "gl_journal_headers" "$CSV_DIR/eurostyle_finance.gl_journal_headers.csv.gz"
load_csv_data "eurostyle_finance" "gl_journal_lines" "$CSV_DIR/eurostyle_finance.gl_journal_lines.csv.gz"

# Load HR database
echo "📍 Loading eurostyle_hr database..."
load_csv_data "eurostyle_hr" "employees" "$CSV_DIR/eurostyle_hr.employees.csv.gz"

# Load webshop database
echo "📍 Loading eurostyle_webshop database..."
load_csv_data "eurostyle_webshop" "web_sessions" "$CSV_DIR/eurostyle_webshop.web_sessions.csv.gz"

echo "🎉 Data loading completed!"

# Run consistency checks
echo "🔍 Running consistency validation..."

echo "📊 Database row counts:"
for db in eurostyle_operational eurostyle_finance eurostyle_hr eurostyle_webshop; do
    echo "--- $db ---"
    $CLICKHOUSE_CLIENT --query="SELECT table, sum(rows) as rows FROM system.parts WHERE database = '$db' AND active = 1 GROUP BY table ORDER BY table"
done

echo "💰 Revenue consistency check:"
OPERATIONAL_REVENUE=$($CLICKHOUSE_CLIENT --query="SELECT sum(total_amount_eur) FROM eurostyle_operational.orders")
FINANCE_REVENUE=$($CLICKHOUSE_CLIENT --query="SELECT sum(credit_amount) FROM eurostyle_finance.gl_journal_lines WHERE account_id = '4000'")

echo "  • Operational revenue: €$OPERATIONAL_REVENUE"  
echo "  • Finance GL revenue: €$FINANCE_REVENUE"

if [[ "$OPERATIONAL_REVENUE" == "$FINANCE_REVENUE" ]]; then
    echo "  ✅ PERFECT MATCH: Operations revenue = Finance GL revenue"
else
    echo "  ❌ MISMATCH: Revenue inconsistency detected"
    echo "  Difference: €$((OPERATIONAL_REVENUE - FINANCE_REVENUE))"
fi

echo "🎯 Universal Data Generation with Perfect Consistency - COMPLETE!"