#!/bin/bash

# =====================================================
# EuroStyle Fashion - FULL Complete Demo Data Generation Script  
# =====================================================
# Generates comprehensive realistic demo data for ALL EuroStyle Fashion systems:
# - Operational Database (ERP) - 9 core business tables
# - Webshop Analytics Database - 10 behavioral tracking tables  
# - Finance System - 14 financial management tables
# - HR System - 13 European employment law compliant tables
# 
# COMPREHENSIVE COVERAGE: All tables with full production-like volumes
#
# Usage: ./scripts/generate-full-complete-data.sh [--force]

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
FULL_CONFIG="config/full_generation_config.yaml"

echo -e "${BLUE}🚀 EuroStyle Fashion - FULL Complete Demo Data Generation${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${CYAN}📊 Multi-System Data Architecture (FULL VOLUMES):${NC}"
echo -e "${CYAN}   • Operational System (ERP) - 9 tables, ~230K records${NC}"
echo -e "${CYAN}   • Webshop Analytics - 10 tables, ~550K records${NC}"
echo -e "${CYAN}   • Finance System - 14 tables, ~120K records${NC}"
echo -e "${CYAN}   • HR System - 13 tables, ~30K records${NC}"
echo -e "${CYAN}   • Cross-System Integration - Full referential integrity${NC}"
echo -e "${YELLOW}⚡ Expected total time: 15-30 minutes (comprehensive generation)${NC}"
echo ""

# Parse command line arguments
FORCE_REGENERATE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_REGENERATE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --force                      Force regeneration even if data exists"
            echo "  -h, --help                   Show this help message"
            echo ""
            echo "This script generates ALL EuroStyle systems with full production-like data volumes:"
            echo "  • Complete business scenario coverage"
            echo "  • 100% functional completeness maintained"
            echo "  • All business relationships preserved"
            echo "  • Multi-year historical data"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown parameter: $1${NC}"
            exit 1
            ;;
    esac
done

# Change to project directory
cd "$PROJECT_DIR"

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
    return 0
}

# Function to check existing data
check_existing_data() {
    print_section "Existing Data Analysis"
    
    local total_records=0
    
    # Check all databases
    for db in "$OPERATIONAL_DB" "$WEBSHOP_DB" "$FINANCE_DB" "$HR_DB"; do
        local db_count=$(docker exec $CONTAINER_NAME clickhouse-client --database=$db --query="
            SELECT sum(total_rows) FROM system.tables 
            WHERE database = '$db' AND total_rows > 0
        " 2>/dev/null || echo "0")
        
        if [ "$db_count" -gt 0 ]; then
            echo -e "${YELLOW}📊 $db has $db_count existing records${NC}"
            total_records=$((total_records + db_count))
        else
            echo -e "${BLUE}📭 $db is empty${NC}"
        fi
    done
    
    # Handle existing data
    if [ $total_records -gt 0 ] && ! $FORCE_REGENERATE; then
        echo ""
        echo -e "${YELLOW}⚠️ Found $total_records existing records across all databases.${NC}"
        echo -e "${YELLOW}   Use --force to regenerate all data, or continue to append.${NC}"
        echo ""
        read -p "Continue with data generation? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}ℹ️ Data generation cancelled${NC}"
            exit 0
        fi
    fi
}

# Function to generate operational database data (FULL)
generate_operational_data() {
    print_section "Operational Database Data Generation (FULL)"
    
    echo -e "${BLUE}🏗️ Generating ERP system data with full configuration...${NC}"
    echo -e "${BLUE}📊 Full volumes:${NC}"
    echo -e "${BLUE}   • Customers: 50,000 European customers${NC}"
    echo -e "${BLUE}   • Products: 5,000 fashion items${NC}"
    echo -e "${BLUE}   • Stores: 50 locations${NC}"
    echo -e "${BLUE}   • Orders: 25,000 orders${NC}"
    echo -e "${BLUE}   • Inventory: Full stock management${NC}"
    echo -e "${BLUE}   • Campaigns: 100+ marketing campaigns${NC}"
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
    
    echo -e "${YELLOW}⏱️ Estimated time: 10-15 minutes${NC}"
    echo ""
    
    # Execute generation with full config
    if python3 generate_data.py --config "$FULL_CONFIG" --verbose; then
        echo ""
        echo -e "${GREEN}🎉 Operational data generation completed successfully!${NC}"
        cd "$PROJECT_DIR"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Operational data generation failed${NC}"
        cd "$PROJECT_DIR"
        return 1
    fi
}

# Function to generate complete webshop database data (FULL)
generate_webshop_data() {
    print_section "Webshop Analytics Data Generation (FULL)"
    
    echo -e "${BLUE}🌐 Generating webshop analytics data with full configuration...${NC}"
    echo -e "${BLUE}📊 Full volumes:${NC}"
    echo -e "${BLUE}   • Web Sessions: 80,000 customer journeys${NC}"
    echo -e "${BLUE}   • Page Views: 250,000 page interactions${NC}"
    echo -e "${BLUE}   • Cart Activities: 15,000 shopping cart events${NC}"
    echo -e "${BLUE}   • Product Reviews: 5,000 customer reviews${NC}"
    echo -e "${BLUE}   • Search Queries: 30,000 search events${NC}"
    echo -e "${BLUE}   • All other webshop tables: Full production volumes${NC}"
    echo ""
    
    # Generate webshop data with full config
    echo -e "${YELLOW}🔄 Generating full webshop CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_webshop_data.py --full-config; then
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

# Function to generate finance database data (FULL)
generate_finance_data() {
    print_section "Finance Database Data Generation (FULL)"
    
    echo -e "${BLUE}🏦 Generating finance system data with full configuration...${NC}"
    echo -e "${BLUE}📊 Full volumes:${NC}"
    echo -e "${BLUE}   • Legal Entities: 20 entities (1 holding + 19 subsidiaries)${NC}"
    echo -e "${BLUE}   • Chart of Accounts: 500 IFRS-compliant accounts${NC}"
    echo -e "${BLUE}   • GL Transactions: 30,000 journal entries${NC}"
    echo -e "${BLUE}   • Exchange Rates: 5,000 daily rates${NC}"
    echo -e "${BLUE}   • Budget Data: Multi-year comprehensive planning${NC}"
    echo -e "${BLUE}   • Fixed Assets: 1,500 asset records${NC}"
    echo ""
    
    # Generate finance data with full config
    echo -e "${YELLOW}🔄 Generating full finance CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_finance_data.py --full-config; then
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

# Function to generate HR database data (FULL)
generate_hr_data() {
    print_section "HR Database Data Generation (FULL)"
    
    echo -e "${BLUE}👥 Generating HR system data with full configuration...${NC}"
    echo -e "${BLUE}📊 Full volumes:${NC}"
    echo -e "${BLUE}   • Departments: 100 organizational units${NC}"
    echo -e "${BLUE}   • Job Positions: 500 roles across all levels${NC}"
    echo -e "${BLUE}   • Employees: 1,500 European workforce${NC}"
    echo -e "${BLUE}   • Employment Contracts: 1,500 contract records${NC}"
    echo -e "${BLUE}   • Leave Requests: 8,000 European compliance tracking${NC}"
    echo -e "${BLUE}   • Performance Reviews: 4,000 review cycles${NC}"
    echo -e "${BLUE}   • Training Records: 3,000 compliance & development${NC}"
    echo ""
    
    # Generate HR data with full config
    echo -e "${YELLOW}🔄 Generating full HR CSV files...${NC}"
    
    if python3 scripts/data-generation/generate_complete_hr_data.py --full-config; then
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
    print_section "Complete Full Database Summary"
    
    echo -e "${CYAN}📊 EuroStyle Fashion - Full Data Architecture Overview${NC}"
    echo ""
    
    # Operational Database Summary
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
    
    # Webshop Database Summary
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
    
    # Finance Database Summary
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
    
    # HR Database Summary
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
}

# Main execution function
main() {
    local start_time=$(date +%s)
    
    echo -e "${BLUE}📋 Initializing full complete data generation process...${NC}"
    echo ""
    
    # Pre-flight checks
    if ! check_container; then
        echo -e "${RED}❌ Container check failed${NC}"
        exit 1
    fi
    
    # Analyze existing data
    check_existing_data
    
    # Generate all systems in order (operational first for foreign keys)
    local generation_success=true
    
    if ! generate_operational_data; then
        generation_success=false
    elif ! generate_webshop_data; then
        generation_success=false
    elif ! generate_finance_data; then
        generation_success=false
    elif ! generate_hr_data; then
        generation_success=false
    fi
    
    if ! $generation_success; then
        echo -e "${RED}❌ Full data generation process failed${NC}"
        exit 1
    fi
    
    # Show summary
    show_database_summary
    
    # Calculate execution time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    # Success message
    echo ""
    echo -e "${GREEN}🎉 EuroStyle Fashion FULL Complete Data Generation Successful!${NC}"
    echo -e "${GREEN}=============================================================${NC}"
    echo -e "${GREEN}⚡ Total execution time: ${minutes}m ${seconds}s (comprehensive generation)${NC}"
    echo -e "${GREEN}📊 Complete production-like dataset${NC}"
    echo ""
    echo -e "${CYAN}🔗 Access your data:${NC}"
    echo -e "${CYAN}   • HTTP Interface: http://localhost:8124${NC}"
    echo -e "${CYAN}   • Native Port: localhost:9002${NC}"
    echo -e "${CYAN}   • Operational Database: $OPERATIONAL_DB${NC}"
    echo -e "${CYAN}   • Webshop Database: $WEBSHOP_DB${NC}"
    echo -e "${CYAN}   • Finance Database: $FINANCE_DB${NC}"
    echo -e "${CYAN}   • HR Database: $HR_DB${NC}"
    echo ""
    echo -e "${YELLOW}💡 Full generation benefits:${NC}"
    echo -e "${BLUE}   ✓ Complete comprehensive database (all tables fully populated)${NC}"
    echo -e "${BLUE}   ✓ Full referential integrity maintained${NC}"
    echo -e "${BLUE}   ✓ All business patterns preserved${NC}"
    echo -e "${BLUE}   ✓ Production-like data volumes${NC}"
    echo -e "${BLUE}   ✓ Multi-year historical data${NC}"
    echo -e "${BLUE}   ✓ Perfect for comprehensive testing and demos${NC}"
    echo ""
}

# Run main function with all arguments
main "$@"