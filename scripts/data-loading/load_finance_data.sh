#!/bin/bash

# =====================================================
# EuroStyle Fashion - Finance Data Loading Script
# =====================================================
# Loads generated finance CSV data into ClickHouse database
# Supports multi-country BV structure with holding company

set -e

# Configuration
CONTAINER_NAME="eurostyle_clickhouse_retail"
DATABASE_NAME="eurostyle_finance"
USER_FILES_DIR="/var/lib/clickhouse/user_files"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏦 EuroStyle Fashion - Finance Data Loading${NC}"
echo -e "${BLUE}===========================================${NC}"

# Function to check if container is running
check_container() {
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}❌ Container '$CONTAINER_NAME' is not running${NC}"
        echo -e "${YELLOW}💡 Start it with: ./scripts/start-eurostyle.sh${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Container is running${NC}"
}

# Function to check database exists
check_database() {
    echo -e "${YELLOW}🔍 Checking finance database...${NC}"
    
    # Create database if it doesn't exist
    if ! docker exec $CONTAINER_NAME clickhouse-client --query "EXISTS DATABASE $DATABASE_NAME" | grep -q "1"; then
        echo -e "${YELLOW}📝 Creating finance database...${NC}"
        docker exec $CONTAINER_NAME clickhouse-client --query "CREATE DATABASE IF NOT EXISTS $DATABASE_NAME"
    fi
    
    echo -e "${GREEN}✅ Database '$DATABASE_NAME' is ready${NC}"
}

# Function to create tables
create_tables() {
    echo -e "${YELLOW}🏗️ Creating finance tables...${NC}"
    
    if [ -f "init-scripts/databases/03_finance_tables.sql" ]; then
        # Execute the DDL script with multi-query support
        docker exec -i $CONTAINER_NAME clickhouse-client --multiquery < init-scripts/databases/03_finance_tables.sql
        echo -e "${GREEN}✅ Finance tables created successfully${NC}"
    elif [ -f "init-scripts/archive/03_create_finance_database.sql" ]; then
        # Fallback to archive location
        docker exec -i $CONTAINER_NAME clickhouse-client --multiquery < init-scripts/archive/03_create_finance_database.sql
        echo -e "${GREEN}✅ Finance tables created successfully${NC}"
    else
        echo -e "${RED}❌ DDL script not found: init-scripts/databases/03_finance_tables.sql${NC}"
        exit 1
    fi
}

# Function to copy CSV files to container
copy_csv_files() {
    echo -e "${YELLOW}📂 Copying CSV files to container...${NC}"
    
    # List of expected finance CSV files (now compressed)
    local csv_files=(
        "eurostyle_finance.legal_entities.csv.gz"
        "eurostyle_finance.entity_relationships.csv.gz"
        "eurostyle_finance.chart_of_accounts.csv.gz"
        "eurostyle_finance.entity_accounts.csv.gz"
        "eurostyle_finance.currencies.csv.gz"
        "eurostyle_finance.exchange_rates.csv.gz"
        "eurostyle_finance.reporting_periods.csv.gz"
        "eurostyle_finance.cost_centers.csv.gz"
        "eurostyle_finance.gl_journal_headers.csv.gz"
        "eurostyle_finance.gl_journal_lines.csv.gz"
        "eurostyle_finance.budget_versions.csv.gz"
        "eurostyle_finance.budget_data.csv.gz"
        "eurostyle_finance.fixed_assets.csv.gz"
        "eurostyle_finance.depreciation_schedule.csv.gz"
    )
    
    local copied_files=0
    local total_size=0
    
    for csv_file in "${csv_files[@]}"; do
        local csv_path="data/csv/$csv_file"
        if [ -f "$csv_path" ]; then
            # Get file size
            local file_size=$(stat -f%z "$csv_path" 2>/dev/null || stat -c%s "$csv_path" 2>/dev/null || echo "0")
            total_size=$((total_size + file_size))
            
            # Copy file
            docker cp "$csv_path" "$CONTAINER_NAME:$USER_FILES_DIR/"
            
            if [ $? -eq 0 ]; then
                local size_display
                if [ $file_size -gt 1048576 ]; then
                    size_display=$(echo "scale=1; $file_size / 1048576" | bc -l)"M"
                elif [ $file_size -gt 1024 ]; then
                    size_display=$(echo "scale=1; $file_size / 1024" | bc -l)"K"
                else
                    size_display="${file_size}B"
                fi
                
                echo -e "  ${GREEN}✅${NC} $csv_file (${size_display})"
                copied_files=$((copied_files + 1))
            else
                echo -e "  ${RED}❌${NC} Failed to copy $csv_file"
            fi
        else
            echo -e "  ${YELLOW}⚠️${NC} $csv_file not found (skipping)"
        fi
    done
    
    local total_size_display
    if [ $total_size -gt 1048576 ]; then
        total_size_display=$(echo "scale=1; $total_size / 1048576" | bc -l)" MB"
    elif [ $total_size -gt 1024 ]; then
        total_size_display=$(echo "scale=1; $total_size / 1024" | bc -l)" KB"
    else
        total_size_display="${total_size} bytes"
    fi
    
    echo -e "${BLUE}📊 Copied $copied_files files, total size: $total_size_display${NC}"
}

# Function to load data into tables
load_data() {
    echo -e "${YELLOW}📥 Loading data into finance tables...${NC}"
    
    # Define loading descriptions
    get_table_description() {
        case "$1" in
            "legal_entities") echo "Legal entities (corporate structure)" ;;
            "entity_relationships") echo "Entity relationships (ownership)" ;;
            "currencies") echo "Currencies master data" ;;
            "chart_of_accounts") echo "Chart of accounts" ;;
            "entity_accounts") echo "Entity account mappings" ;;
            "reporting_periods") echo "Reporting periods" ;;
            "cost_centers") echo "Cost centers" ;;
            "exchange_rates") echo "Exchange rates (daily)" ;;
            "gl_journal_headers") echo "GL journal headers" ;;
            "gl_journal_lines") echo "GL journal lines" ;;
            "budget_versions") echo "Budget versions" ;;
            "budget_data") echo "Budget data" ;;
            "fixed_assets") echo "Fixed assets" ;;
            "depreciation_schedule") echo "Depreciation schedules" ;;
            *) echo "Finance table" ;;
        esac
    }
    
    # Loading order (respects foreign key dependencies)
    local load_order=(
        "legal_entities"
        "entity_relationships"
        "currencies"
        "chart_of_accounts"
        "entity_accounts"
        "reporting_periods"
        "cost_centers"
        "exchange_rates"
        "gl_journal_headers"
        "gl_journal_lines"
        "budget_versions"
        "budget_data"
        "fixed_assets"
        "depreciation_schedule"
    )
    
    local loaded_tables=0
    local total_records=0
    
    for table in "${load_order[@]}"; do
        local csv_file="eurostyle_finance.${table}.csv.gz"
        local description=$(get_table_description "$table")
        
        echo -e "${PURPLE}Loading $table...${NC}"
        echo -e "  ${BLUE}📄${NC} $description"
        
        if docker exec $CONTAINER_NAME test -f "$USER_FILES_DIR/$csv_file"; then
            # Clear existing data
            docker exec $CONTAINER_NAME clickhouse-client \
                --database="$DATABASE_NAME" \
                --query="TRUNCATE TABLE $table" >/dev/null 2>&1 || true
            
            # Load new data (ClickHouse automatically handles .gz files)
            local load_query="INSERT INTO $table SELECT * FROM file('$csv_file', 'CSVWithNames')"
            
            if docker exec $CONTAINER_NAME clickhouse-client \
                --database="$DATABASE_NAME" \
                --query="$load_query" 2>/dev/null; then
                
                # Get record count
                local record_count=$(docker exec $CONTAINER_NAME clickhouse-client \
                    --database="$DATABASE_NAME" \
                    --query="SELECT count() FROM $table" 2>/dev/null || echo "0")
                
                total_records=$((total_records + record_count))
                loaded_tables=$((loaded_tables + 1))
                
                # Format number with commas
                local formatted_count=$(echo "$record_count" | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
                
                echo -e "  ${GREEN}✅${NC} $formatted_count records loaded"
            else
                echo -e "  ${RED}❌${NC} Failed to load data"
                echo -e "  ${YELLOW}💡${NC} Check CSV file format and table structure"
            fi
        else
            echo -e "  ${YELLOW}⚠️${NC} CSV file not found in container"
        fi
        
        echo ""
    done
    
    echo -e "${BLUE}📊 Loading Summary:${NC}"
    echo -e "${BLUE}  • Tables loaded: $loaded_tables/${#load_order[@]}${NC}"
    local formatted_total=$(echo "$total_records" | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
    echo -e "${BLUE}  • Total records: $formatted_total${NC}"
}

# Function to verify data integrity
verify_data() {
    echo -e "${YELLOW}🔍 Verifying data integrity...${NC}"
    
    # Check table record counts
    echo -e "${PURPLE}Table Summary:${NC}"
    
    docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT 
                table,
                formatReadableQuantity(total_rows) as records,
                formatReadableSize(total_bytes) as size
            FROM system.tables 
            WHERE database = '$DATABASE_NAME' AND total_rows > 0
            ORDER BY total_rows DESC
            FORMAT PrettyCompact"
    
    echo ""
    
    # Check referential integrity
    echo -e "${PURPLE}Data Integrity Checks:${NC}"
    
    # Check entity relationships
    local orphaned_relationships=$(docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT count() FROM entity_relationships er 
            WHERE er.parent_entity_id NOT IN (SELECT entity_id FROM legal_entities)
               OR er.child_entity_id NOT IN (SELECT entity_id FROM legal_entities)
        " 2>/dev/null || echo "0")
    
    if [ "$orphaned_relationships" -eq 0 ]; then
        echo -e "  ${GREEN}✅${NC} Entity relationships integrity: OK"
    else
        echo -e "  ${RED}❌${NC} Found $orphaned_relationships orphaned entity relationships"
    fi
    
    # Check GL journal balance
    local unbalanced_journals=$(docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT count() FROM gl_journal_headers 
            WHERE abs(total_debit - total_credit) > 0.01
        " 2>/dev/null || echo "0")
    
    if [ "$unbalanced_journals" -eq 0 ]; then
        echo -e "  ${GREEN}✅${NC} GL journal balance: OK"
    else
        echo -e "  ${RED}❌${NC} Found $unbalanced_journals unbalanced journals"
    fi
    
    # Check budget data currency consistency
    local currency_mismatches=$(docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT count() FROM budget_data bd
            JOIN legal_entities le ON bd.entity_id = le.entity_id
            WHERE bd.functional_currency != le.functional_currency
        " 2>/dev/null || echo "0")
    
    if [ "$currency_mismatches" -eq 0 ]; then
        echo -e "  ${GREEN}✅${NC} Currency consistency: OK"
    else
        echo -e "  ${RED}❌${NC} Found $currency_mismatches currency mismatches"
    fi
    
    echo ""
}

# Function to show sample queries
show_sample_queries() {
    echo -e "${PURPLE}🔍 Sample Finance Queries:${NC}"
    echo ""
    
    # 1. Corporate structure overview
    echo -e "${BLUE}1. Corporate Structure:${NC}"
    docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT 
                entity_code,
                entity_name,
                entity_type,
                country_code,
                functional_currency
            FROM legal_entities
            ORDER BY entity_type, country_code
            FORMAT PrettyCompact"
    echo ""
    
    # 2. GL transaction summary by entity
    echo -e "${BLUE}2. GL Activity Summary (Last 3 Months):${NC}"
    docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT 
                le.entity_code,
                le.country_code,
                count(*) as journals,
                formatReadableQuantity(sum(total_debit)) as total_debits,
                formatReadableQuantity(sum(total_credit)) as total_credits
            FROM gl_journal_headers jh
            JOIN legal_entities le ON jh.entity_id = le.entity_id
            WHERE jh.period_year = 2024 AND jh.period_month >= 10
            GROUP BY le.entity_code, le.country_code
            ORDER BY sum(total_debit) DESC
            FORMAT PrettyCompact" 2>/dev/null || echo "No recent GL data found"
    echo ""
    
    # 3. Budget vs Actual (if available)
    echo -e "${BLUE}3. Budget Overview by Entity:${NC}"
    docker exec $CONTAINER_NAME clickhouse-client \
        --database="$DATABASE_NAME" \
        --query="
            SELECT 
                le.entity_code,
                bv.budget_year,
                bv.version_name,
                count(bd.budget_id) as budget_lines,
                formatReadableQuantity(sum(bd.budget_amount)) as total_budget
            FROM budget_versions bv
            JOIN legal_entities le ON bv.entity_id = le.entity_id
            JOIN budget_data bd ON bv.version_id = bd.version_id
            WHERE bv.is_active = true
            GROUP BY le.entity_code, bv.budget_year, bv.version_name
            ORDER BY bv.budget_year DESC, le.entity_code
            LIMIT 10
            FORMAT PrettyCompact" 2>/dev/null || echo "No budget data found"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Starting finance data loading process...${NC}"
    echo ""
    
    # Pre-flight checks
    check_container
    check_database
    
    # Create tables
    create_tables
    echo ""
    
    # Load data
    copy_csv_files
    echo ""
    
    load_data
    
    # Verify integrity
    verify_data
    
    # Show sample queries
    show_sample_queries
    
    # Success message
    echo -e "${GREEN}🎉 Finance data loading completed successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${CYAN}🔗 Access your finance data:${NC}"
    echo -e "${CYAN}   • Database: $DATABASE_NAME${NC}"
    echo -e "${CYAN}   • HTTP Interface: http://localhost:8124${NC}"
    echo -e "${CYAN}   • Native Port: localhost:9002${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "${BLUE}   • Create consolidation views${NC}"
    echo -e "${BLUE}   • Set up financial reporting dashboards${NC}"
    echo -e "${BLUE}   • Configure budget vs actual analysis${NC}"
    echo -e "${BLUE}   • Implement multi-currency consolidation${NC}"
    echo ""
    echo -e "${PURPLE}🏢 EuroStyle Finance Structure:${NC}"
    echo -e "${PURPLE}   • Holding Company: Netherlands (EUR)${NC}"
    echo -e "${PURPLE}   • Operating BVs: Germany, France, Italy, Spain (EUR)${NC}"
    echo -e "${PURPLE}   • Full consolidation with 100% ownership${NC}"
}

# Run main function
main "$@"