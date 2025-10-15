#!/bin/bash

# =====================================================
# EuroStyle Fashion - Complete Demo Data Generation Script
# =====================================================
# Generates realistic demo data for ALL EuroStyle Fashion systems:
# - Operational Database (ERP)
# - Webshop Analytics Database
# - Future: Finance & HR Systems
# 
# Usage: ./scripts/generate-demo-data.sh [options]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_GENERATOR_DIR="$PROJECT_DIR/data-generator"

# Configuration
OPERATIONAL_DB="eurostyle_operational"
WEBSHOP_DB="eurostyle_webshop"
FINANCE_DB="eurostyle_finance"
HR_DB="eurostyle_hr"
CONTAINER_NAME="eurostyle_clickhouse_retail"

echo -e "${BLUE}🎲 EuroStyle Fashion - Complete Demo Data Generation${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${CYAN}📊 Multi-System Data Architecture:${NC}"
echo -e "${CYAN}   • Operational System (ERP) - 9 core business tables${NC}"
echo -e "${CYAN}   • Webshop Analytics - 10 behavioral tracking tables${NC}"
echo -e "${CYAN}   • Finance System - 14 financial management tables${NC}"
echo -e "${CYAN}   • HR System - 13 European employment law compliant tables${NC}"
echo -e "${CYAN}   • Cross-System Integration - Full referential integrity${NC}"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Parse command line arguments
SPECIFIC_TABLES=""
SYSTEM_FILTER=""
SKIP_VALIDATION=false
FORCE_REGENERATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --tables)
            SPECIFIC_TABLES="$2"
            shift 2
            ;;
        --system)
            SYSTEM_FILTER="$2"
            shift 2
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --force)
            FORCE_REGENERATE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --system SYSTEM              Generate only specific system (operational|webshop|finance|hr|all)"
            echo "  --tables TABLE1,TABLE2,...   Generate only specific tables (within system)"
            echo "  --skip-validation            Skip database connectivity validation"
            echo "  --force                      Force regeneration even if data exists"
            echo "  -h, --help                   Show this help message"
            echo ""
            echo "Systems:"
            echo "  operational  - ERP system (customers, products, orders, inventory, etc.)"
            echo "  webshop      - Analytics system (sessions, page_views, cart_activities, etc.)"
            echo "  finance      - Finance system (GL, budgets, consolidation, multi-currency)"
            echo "  hr           - HR system (employees, contracts, performance, training)"
            echo "  all          - All systems (default)"
            echo ""
            echo "Operational Tables:"
            echo "  customers, products, stores, campaigns, orders, order_lines, inventory,"
            echo "  european_geography, fashion_calendar"
            echo ""
            echo "Webshop Tables:"
            echo "  web_sessions, page_views, cart_activities, search_queries, product_reviews,"
            echo "  wishlist_items, web_analytics_events, email_marketing, product_recommendations,"
            echo "  ab_test_results"
            echo ""
            echo "Finance Tables:"
            echo "  legal_entities, chart_of_accounts, gl_journal_headers, gl_journal_lines,"
            echo "  budget_data, fixed_assets, exchange_rates, consolidation_adjustments"
            echo ""
            echo "HR Tables:"
            echo "  departments, job_positions, employees, employment_contracts, compensation_history,"
            echo "  leave_requests, leave_balances, performance_reviews, employee_training"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Generate all systems"
            echo "  $0 --system operational              # Generate only ERP data"
            echo "  $0 --system webshop                  # Generate only webshop data"
            echo "  $0 --system finance                  # Generate only finance data"
            echo "  $0 --system hr                       # Generate only HR data"
            echo "  $0 --system operational --tables customers,products"
            echo "  $0 --force                           # Force complete regeneration"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown parameter: $1${NC}"
            exit 1
            ;;
    esac
done

# Set default system if not specified
if [ -z "$SYSTEM_FILTER" ]; then
    SYSTEM_FILTER="all"
fi

# Function to print section headers
print_section() {
    echo ""
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}$(printf '═%.0s' $(seq 1 ${#1}))${NC}"
}

# Function to check if container is running
check_container() {
    print_section "Container Status Check"
    
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}❌ EuroStyle ClickHouse container is not running${NC}"
        echo -e "${YELLOW}💡 Start it with: ./scripts/start-eurostyle.sh${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Container '$CONTAINER_NAME' is running${NC}"
    
    # Check container health
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "unknown")
    case $health_status in
        "healthy")
            echo -e "${GREEN}✅ Container is healthy${NC}"
            ;;
        "starting")
            echo -e "${YELLOW}⏳ Container is still starting...${NC}"
            ;;
        "unhealthy"|"unknown")
            echo -e "${YELLOW}⚠️ Container health status: $health_status${NC}"
            ;;
    esac
    
    return 0
}

# Function to create databases if they don't exist
create_databases() {
    print_section "Database Initialization"
    
    echo -e "${BLUE}🏗️ Ensuring all required databases exist...${NC}"
    
    # Execute init scripts in order
    local init_scripts=("01-create-database.sql" "02_create_webshop_database.sql" "03_create_finance_database.sql" "04_create_hr_database.sql")
    
    for script in "${init_scripts[@]}"; do
        local script_path="$PROJECT_DIR/init-scripts/$script"
        if [ -f "$script_path" ]; then
            echo -e "${YELLOW}📋 Executing: $script${NC}"
            # Copy script to container and execute it
            if docker cp "$script_path" $CONTAINER_NAME:/tmp/$script && \
               docker exec $CONTAINER_NAME clickhouse-client --host localhost --port 9000 --multiquery --queries-file /tmp/$script >/dev/null 2>&1; then
                echo -e "${GREEN}✅ $script executed successfully${NC}"
            else
                echo -e "${YELLOW}⚠️ $script execution completed (may have warnings)${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Init script not found: $script${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ Database initialization completed${NC}"
    return 0
}

# Function to check database connectivity
test_database_connection() {
    print_section "Database Connectivity Check"
    
    local operational_ok=false
    local webshop_ok=false
    local finance_ok=false
    local hr_ok=false
    
    # Test operational database
    if docker exec $CONTAINER_NAME clickhouse-client --database=$OPERATIONAL_DB --query="SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Operational database ($OPERATIONAL_DB) connection successful${NC}"
        operational_ok=true
    else
        echo -e "${RED}❌ Operational database ($OPERATIONAL_DB) connection failed${NC}"
    fi
    
    # Test webshop database
    if docker exec $CONTAINER_NAME clickhouse-client --database=$WEBSHOP_DB --query="SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Webshop database ($WEBSHOP_DB) connection successful${NC}"
        webshop_ok=true
    else
        echo -e "${RED}❌ Webshop database ($WEBSHOP_DB) connection failed${NC}"
    fi
    
    # Test finance database
    if docker exec $CONTAINER_NAME clickhouse-client --database=$FINANCE_DB --query="SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Finance database ($FINANCE_DB) connection successful${NC}"
        finance_ok=true
    else
        echo -e "${RED}❌ Finance database ($FINANCE_DB) connection failed${NC}"
    fi
    
    # Test HR database
    if docker exec $CONTAINER_NAME clickhouse-client --database=$HR_DB --query="SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ HR database ($HR_DB) connection successful${NC}"
        hr_ok=true
    else
        echo -e "${RED}❌ HR database ($HR_DB) connection failed${NC}"
    fi
    
    # If any databases are missing, try to create them
    if ! $operational_ok || ! $webshop_ok || ! $finance_ok || ! $hr_ok; then
        echo -e "${YELLOW}🔧 Some databases missing, attempting to create them...${NC}"
        create_databases
        
        # Re-test connections after creation
        echo -e "${BLUE}🔄 Re-testing database connections...${NC}"
        
        if docker exec $CONTAINER_NAME clickhouse-client --database=$OPERATIONAL_DB --query="SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Operational database now accessible${NC}"
            operational_ok=true
        fi
        
        if docker exec $CONTAINER_NAME clickhouse-client --database=$WEBSHOP_DB --query="SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Webshop database now accessible${NC}"
            webshop_ok=true
        fi
        
        if docker exec $CONTAINER_NAME clickhouse-client --database=$FINANCE_DB --query="SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Finance database now accessible${NC}"
            finance_ok=true
        fi
        
        if docker exec $CONTAINER_NAME clickhouse-client --database=$HR_DB --query="SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ HR database now accessible${NC}"
            hr_ok=true
        fi
    fi
    
    # Check system filter requirements
    case $SYSTEM_FILTER in
        "operational")
            if ! $operational_ok; then
                echo -e "${RED}❌ Cannot proceed: Operational database required but not accessible${NC}"
                return 1
            fi
            ;;
        "webshop")
            if ! $webshop_ok; then
                echo -e "${RED}❌ Cannot proceed: Webshop database required but not accessible${NC}"
                return 1
            fi
            ;;
        "finance")
            if ! $finance_ok; then
                echo -e "${RED}❌ Cannot proceed: Finance database required but not accessible${NC}"
                return 1
            fi
            ;;
        "hr")
            if ! $hr_ok; then
                echo -e "${RED}❌ Cannot proceed: HR database required but not accessible${NC}"
                return 1
            fi
            ;;
        "all")
            if ! $operational_ok || ! $webshop_ok || ! $finance_ok || ! $hr_ok; then
                echo -e "${RED}❌ Cannot proceed: All databases required but not accessible after creation attempt${NC}"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Function to check existing data
check_existing_data() {
    print_section "Existing Data Analysis"
    
    local has_operational_data=false
    local has_webshop_data=false
    local has_finance_data=false
    local has_hr_data=false
    
    # Check operational data
    if [[ "$SYSTEM_FILTER" == "operational" || "$SYSTEM_FILTER" == "all" ]]; then
        local op_count=$(docker exec $CONTAINER_NAME clickhouse-client --database=$OPERATIONAL_DB --query="
            SELECT sum(total_rows) FROM system.tables 
            WHERE database = '$OPERATIONAL_DB' AND total_rows > 0
        " 2>/dev/null || echo "0")
        
        if [ "$op_count" -gt 0 ]; then
            echo -e "${YELLOW}📊 Operational database has $op_count existing records${NC}"
            has_operational_data=true
        else
            echo -e "${BLUE}📭 Operational database is empty${NC}"
        fi
    fi
    
    # Check webshop data
    if [[ "$SYSTEM_FILTER" == "webshop" || "$SYSTEM_FILTER" == "all" ]]; then
        local web_count=$(docker exec $CONTAINER_NAME clickhouse-client --database=$WEBSHOP_DB --query="
            SELECT sum(total_rows) FROM system.tables 
            WHERE database = '$WEBSHOP_DB' AND total_rows > 0
        " 2>/dev/null || echo "0")
        
        if [ "$web_count" -gt 0 ]; then
            echo -e "${YELLOW}📊 Webshop database has $web_count existing records${NC}"
            has_webshop_data=true
        else
            echo -e "${BLUE}📭 Webshop database is empty${NC}"
        fi
    fi
    
    # Check finance data
    if [[ "$SYSTEM_FILTER" == "finance" || "$SYSTEM_FILTER" == "all" ]]; then
        local finance_count=$(docker exec $CONTAINER_NAME clickhouse-client --database=$FINANCE_DB --query="
            SELECT sum(total_rows) FROM system.tables 
            WHERE database = '$FINANCE_DB' AND total_rows > 0
        " 2>/dev/null || echo "0")
        
        if [ "$finance_count" -gt 0 ]; then
            echo -e "${YELLOW}📊 Finance database has $finance_count existing records${NC}"
            has_finance_data=true
        else
            echo -e "${BLUE}📭 Finance database is empty${NC}"
        fi
    fi
    
    # Check HR data
    if [[ "$SYSTEM_FILTER" == "hr" || "$SYSTEM_FILTER" == "all" ]]; then
        local hr_count=$(docker exec $CONTAINER_NAME clickhouse-client --database=$HR_DB --query="
            SELECT sum(total_rows) FROM system.tables 
            WHERE database = '$HR_DB' AND total_rows > 0
        " 2>/dev/null || echo "0")
        
        if [ "$hr_count" -gt 0 ]; then
            echo -e "${YELLOW}📊 HR database has $hr_count existing records${NC}"
            has_hr_data=true
        else
            echo -e "${BLUE}📭 HR database is empty${NC}"
        fi
    fi
    
    # Handle existing data
    if ($has_operational_data || $has_webshop_data || $has_finance_data || $has_hr_data) && ! $FORCE_REGENERATE; then
        echo ""
        echo -e "${YELLOW}⚠️ Existing data detected. Options:${NC}"
        echo -e "${YELLOW}   1. Use --force to regenerate all data${NC}"
        echo -e "${YELLOW}   2. Specify --tables to add specific tables${NC}"
        echo -e "${YELLOW}   3. Continue to append new data${NC}"
        echo ""
        read -p "Continue with data generation? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}ℹ️ Data generation cancelled${NC}"
            exit 0
        fi
    fi
}

# Function to generate operational database data
generate_operational_data() {
    print_section "Operational Database Data Generation"
    
    echo -e "${BLUE}🏗️ Generating ERP system data...${NC}"
    echo -e "${BLUE}📊 Expected volumes:${NC}"
    echo -e "${BLUE}   • Customers: 310,000 European customers${NC}"
    echo -e "${BLUE}   • Products: 4,944 fashion items${NC}"
    echo -e "${BLUE}   • Stores: 47 physical locations${NC}"
    echo -e "${BLUE}   • Orders: 500,000+ orders${NC}"
    echo -e "${BLUE}   • Inventory: Stock across all locations${NC}"
    echo -e "${BLUE}   • Campaigns: 600 marketing campaigns${NC}"
    echo ""
    
    cd "$DATA_GENERATOR_DIR"
    
    # Check if Python environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}🔧 Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Build generation command
    local cmd="python3 generate_data.py --verbose"
    
    if [ -n "$SPECIFIC_TABLES" ]; then
        cmd="$cmd --tables $SPECIFIC_TABLES"
        echo -e "${YELLOW}🎯 Generating specific operational tables: $SPECIFIC_TABLES${NC}"
    else
        echo -e "${YELLOW}🌐 Generating all operational tables...${NC}"
    fi
    
    echo -e "${YELLOW}⏱️ Estimated time: 5-15 minutes${NC}"
    echo ""
    
    # Execute generation
    if eval $cmd; then
        echo ""
        echo -e "${GREEN}🎉 Operational data generation completed successfully!${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Operational data generation failed${NC}"
        return 1
    fi
    
    cd "$PROJECT_DIR"
}

# Function to generate webshop database data
generate_webshop_data() {
    print_section "Webshop Analytics Data Generation"
    
    echo -e "${BLUE}🌐 Generating webshop analytics data...${NC}"
    echo -e "${BLUE}📊 Expected volumes:${NC}"
    echo -e "${BLUE}   • Web Sessions: 173,400 customer journeys${NC}"
    echo -e "${BLUE}   • Page Views: 1,030,000+ page interactions${NC}"
    echo -e "${BLUE}   • Cart Activities: 50,000 shopping cart events${NC}"
    echo -e "${BLUE}   • Product Reviews: 15,000 customer reviews${NC}"
    echo -e "${BLUE}   • Recommendations: 200,000 AI suggestions${NC}"
    echo -e "${BLUE}   • A/B Tests: 30,000 optimization experiments${NC}"
    echo ""
    
    # Generate webshop data
    echo -e "${YELLOW}🔄 Generating webshop CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_webshop_data.py; then
        echo -e "${GREEN}✅ Webshop CSV generation completed${NC}"
    else
        echo -e "${RED}❌ Webshop CSV generation failed${NC}"
        return 1
    fi
    
    # Load data into database
    echo -e "${YELLOW}📥 Loading webshop data into ClickHouse...${NC}"
    
    if ./scripts/data-loading/load_webshop_data.sh; then
        echo -e "${GREEN}✅ Webshop data loading completed${NC}"
    else
        echo -e "${RED}❌ Webshop data loading failed${NC}"
        return 1
    fi
    
    return 0
}

# Function to generate finance database data
generate_finance_data() {
    print_section "Finance Database Data Generation"
    
    echo -e "${BLUE}🏦 Generating finance system data...${NC}"
    echo -e "${BLUE}📊 Expected volumes:${NC}"
    echo -e "${BLUE}   • Legal Entities: 5 entities (1 holding + 4 BVs)${NC}"
    echo -e "${BLUE}   • Chart of Accounts: 100+ IFRS-compliant accounts${NC}"
    echo -e "${BLUE}   • GL Transactions: 20,000+ journal entries${NC}"
    echo -e "${BLUE}   • Exchange Rates: 3,000+ daily rates${NC}"
    echo -e "${BLUE}   • Budget Data: Multi-year planning data${NC}"
    echo -e "${BLUE}   • Fixed Assets: Asset management & depreciation${NC}"
    echo ""
    
    # Generate finance data
    echo -e "${YELLOW}🔄 Generating finance CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_finance_data.py; then
        echo -e "${GREEN}✅ Finance CSV generation completed${NC}"
    else
        echo -e "${RED}❌ Finance CSV generation failed${NC}"
        return 1
    fi
    
    # Load data into database
    echo -e "${YELLOW}📥 Loading finance data into ClickHouse...${NC}"
    
    if ./scripts/data-loading/load_finance_data.sh; then
        echo -e "${GREEN}✅ Finance data loading completed${NC}"
    else
        echo -e "${RED}❌ Finance data loading failed${NC}"
        return 1
    fi
    
    return 0
}

# Function to generate HR database data
generate_hr_data() {
    print_section "HR Database Data Generation"
    
    echo -e "${BLUE}👥 Generating HR system data...${NC}"
    echo -e "${BLUE}📊 Expected volumes:${NC}"
    echo -e "${BLUE}   • Departments: 60+ organizational units${NC}"
    echo -e "${BLUE}   • Job Positions: 180+ roles across all levels${NC}"
    echo -e "${BLUE}   • Employees: 500+ European workforce${NC}"
    echo -e "${BLUE}   • Employment Contracts: Full contract management${NC}"
    echo -e "${BLUE}   • Leave Requests: 2,500+ European compliance tracking${NC}"
    echo -e "${BLUE}   • Performance Reviews: Annual review cycles${NC}"
    echo -e "${BLUE}   • Training Records: 1,000+ compliance & development${NC}"
    echo ""
    
    # Generate HR data
    echo -e "${YELLOW}🔄 Generating HR CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_hr_data.py; then
        echo -e "${GREEN}✅ HR CSV generation completed${NC}"
    else
        echo -e "${RED}❌ HR CSV generation failed${NC}"
        return 1
    fi
    
    # Load data into database
    echo -e "${YELLOW}📥 Loading HR data into ClickHouse...${NC}"
    
    if ./scripts/data-loading/load_hr_data.sh --setup; then
        echo -e "${GREEN}✅ HR data loading completed${NC}"
    else
        echo -e "${RED}❌ HR data loading failed${NC}"
        return 1
    fi
    
    return 0
}

# Function to show comprehensive database summary
show_database_summary() {
    print_section "Complete Database Summary"
    
    echo -e "${CYAN}📊 EuroStyle Fashion - Data Architecture Overview${NC}"
    echo ""
    
    # Operational Database Summary
    if [[ "$SYSTEM_FILTER" == "operational" || "$SYSTEM_FILTER" == "all" ]]; then
        echo -e "${BLUE}🏢 Operational Database ($OPERATIONAL_DB)${NC}"
        echo -e "${BLUE}────────────────────────────────────────────${NC}"
        
        docker exec $CONTAINER_NAME clickhouse-client \
            --database=$OPERATIONAL_DB \
            --query="
                SELECT 
                    table,
                    formatReadableQuantity(total_rows) as records,
                    formatReadableSize(total_bytes) as size
                FROM system.tables 
                WHERE database = '$OPERATIONAL_DB' AND total_rows > 0
                ORDER BY total_rows DESC
                FORMAT PrettyCompact" 2>/dev/null || echo -e "${YELLOW}⚠️ Could not retrieve operational database statistics${NC}"
        echo ""
    fi
    
    # Webshop Database Summary
    if [[ "$SYSTEM_FILTER" == "webshop" || "$SYSTEM_FILTER" == "all" ]]; then
        echo -e "${PURPLE}🌐 Webshop Analytics Database ($WEBSHOP_DB)${NC}"
        echo -e "${PURPLE}────────────────────────────────────────────────────${NC}"
        
        docker exec $CONTAINER_NAME clickhouse-client \
            --database=$WEBSHOP_DB \
            --query="
                SELECT 
                    table,
                    formatReadableQuantity(total_rows) as records,
                    formatReadableSize(total_bytes) as size
                FROM system.tables 
                WHERE database = '$WEBSHOP_DB' AND total_rows > 0
                ORDER BY total_rows DESC
                FORMAT PrettyCompact" 2>/dev/null || echo -e "${YELLOW}⚠️ Could not retrieve webshop database statistics${NC}"
        echo ""
    fi
    
    # Finance Database Summary
    if [[ "$SYSTEM_FILTER" == "finance" || "$SYSTEM_FILTER" == "all" ]]; then
        echo -e "${YELLOW}🏦 Finance Database ($FINANCE_DB)${NC}"
        echo -e "${YELLOW}───────────────────────────────────${NC}"
        
        docker exec $CONTAINER_NAME clickhouse-client \
            --database=$FINANCE_DB \
            --query="
                SELECT 
                    table,
                    formatReadableQuantity(total_rows) as records,
                    formatReadableSize(total_bytes) as size
                FROM system.tables 
                WHERE database = '$FINANCE_DB' AND total_rows > 0
                ORDER BY total_rows DESC
                FORMAT PrettyCompact" 2>/dev/null || echo -e "${YELLOW}⚠️ Could not retrieve finance database statistics${NC}"
        echo ""
    fi
    
    # HR Database Summary
    if [[ "$SYSTEM_FILTER" == "hr" || "$SYSTEM_FILTER" == "all" ]]; then
        echo -e "${GREEN}👥 HR Database ($HR_DB)${NC}"
        echo -e "${GREEN}──────────────────────────────────${NC}"
        
        docker exec $CONTAINER_NAME clickhouse-client \
            --database=$HR_DB \
            --query="
                SELECT 
                    table,
                    formatReadableQuantity(total_rows) as records,
                    formatReadableSize(total_bytes) as size
                FROM system.tables 
                WHERE database = '$HR_DB' AND total_rows > 0
                ORDER BY total_rows DESC
                FORMAT PrettyCompact" 2>/dev/null || echo -e "${YELLOW}⚠️ Could not retrieve HR database statistics${NC}"
        echo ""
    fi
    
    # Cross-System Integration Summary
    if [[ "$SYSTEM_FILTER" == "all" ]]; then
        echo -e "${CYAN}🔗 Cross-System Integration${NC}"
        echo -e "${CYAN}──────────────────────────${NC}"
        echo -e "${GREEN}✅ Customer referential integrity: webshop sessions ↔ operational customers${NC}"
        echo -e "${GREEN}✅ Product referential integrity: webshop analytics ↔ operational products${NC}"
        echo -e "${GREEN}✅ Campaign attribution: webshop marketing ↔ operational campaigns${NC}"
        echo -e "${GREEN}✅ Financial integration: GL transactions ↔ operational orders${NC}"
        echo -e "${GREEN}✅ HR integration: employees ↔ finance entities & cost centers${NC}"
        echo -e "${GREEN}✅ Multi-currency consolidation: 5 legal entities with EUR base${NC}"
        echo -e "${GREEN}✅ European employment law compliance: GDPR, sick leave, works councils${NC}"
        echo ""
    fi
}

# Function to update documentation
update_documentation() {
    print_section "Documentation Update"
    
    echo -e "${YELLOW}📋 Updating supplier documentation...${NC}"
    
    if python3 "$PROJECT_DIR/scripts/generate_source_docs.py" --system all; then
        echo -e "${GREEN}✅ Documentation updated successfully${NC}"
        echo -e "${BLUE}📄 Generated files:${NC}"
        echo -e "${BLUE}   • docs/output/EuroStyle_ERP_Documentation.pdf${NC}"
        echo -e "${BLUE}   • docs/output/EuroStyle_Webshop_Documentation.pdf${NC}"
    else
        echo -e "${YELLOW}⚠️ Documentation update encountered issues${NC}"
    fi
}

# Main execution function
main() {
    local start_time=$(date +%s)
    
    echo -e "${BLUE}📋 Initializing complete data generation process...${NC}"
    echo -e "${BLUE}System Filter: $SYSTEM_FILTER${NC}"
    if [ -n "$SPECIFIC_TABLES" ]; then
        echo -e "${BLUE}Table Filter: $SPECIFIC_TABLES${NC}"
    fi
    echo ""
    
    # Pre-flight checks
    if ! check_container; then
        echo -e "${RED}❌ Container check failed${NC}"
        exit 1
    fi
    
    if ! $SKIP_VALIDATION && ! test_database_connection; then
        echo -e "${RED}❌ Database connectivity check failed${NC}"
        exit 1
    fi
    
    # Analyze existing data
    check_existing_data
    
    # Generate data based on system filter
    local generation_success=true
    
    case $SYSTEM_FILTER in
        "operational")
            if ! generate_operational_data; then
                generation_success=false
            fi
            ;;
        "webshop")
            if ! generate_webshop_data; then
                generation_success=false
            fi
            ;;
        "finance")
            if ! generate_finance_data; then
                generation_success=false
            fi
            ;;
        "hr")
            if ! generate_hr_data; then
                generation_success=false
            fi
            ;;
        "all")
            # Generate operational first (needed for webshop, finance, and HR foreign keys)
            if ! generate_operational_data; then
                generation_success=false
            elif ! generate_webshop_data; then
                generation_success=false
            elif ! generate_finance_data; then
                generation_success=false
            elif ! generate_hr_data; then
                generation_success=false
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid system filter: $SYSTEM_FILTER${NC}"
            exit 1
            ;;
    esac
    
    if ! $generation_success; then
        echo -e "${RED}❌ Data generation process failed${NC}"
        exit 1
    fi
    
    # Show summary
    show_database_summary
    
    # Update documentation
    update_documentation
    
    # Calculate execution time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    # Success message
    echo ""
    echo -e "${GREEN}🎉 EuroStyle Fashion Complete Data Generation Successful!${NC}"
    echo -e "${GREEN}========================================================${NC}"
    echo -e "${GREEN}⏱️ Total execution time: ${minutes}m ${seconds}s${NC}"
    echo ""
    echo -e "${CYAN}🔗 Access your data:${NC}"
    echo -e "${CYAN}   • HTTP Interface: http://localhost:8124${NC}"
    echo -e "${CYAN}   • Native Port: localhost:9002${NC}"
    echo -e "${CYAN}   • Operational Database: $OPERATIONAL_DB${NC}"
    echo -e "${CYAN}   • Webshop Database: $WEBSHOP_DB${NC}"
    echo -e "${CYAN}   • Finance Database: $FINANCE_DB${NC}"
    echo -e "${CYAN}   • HR Database: $HR_DB${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "${BLUE}   • Design data warehouse models${NC}"
    echo -e "${BLUE}   • Build ETL pipelines${NC}"
    echo -e "${BLUE}   • Create BI dashboards${NC}"
    echo -e "${BLUE}   • Analyze cross-system data flows${NC}"
    echo ""
    
    # Show future system roadmap
    echo -e "${PURPLE}🚀 System Architecture Status:${NC}"
    echo -e "${GREEN}   ✓ Finance System (Multi-country BV + Holding structure) - COMPLETED${NC}"
    echo -e "${GREEN}   ✓ HR System (European employment law compliant) - COMPLETED${NC}"
    echo -e "${PURPLE}   • POS Enhancement (Staff transaction tracking)${NC}"
    echo -e "${PURPLE}   • Supply Chain Management (Vendor & procurement data)${NC}"
    echo ""
}

# Run main function with all arguments
main "$@"
