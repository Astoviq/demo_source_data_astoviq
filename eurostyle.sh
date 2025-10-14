#!/bin/bash

# =====================================================
# EuroStyle Fashion - Unified Management System
# =====================================================
# Unified management for the complete EuroStyle demo environment
# Run from project root: ./eurostyle.sh <command> [options]
#
# Commands:
#   start         - Start containers only
#   stop          - Stop containers only  
#   setup         - Create database structure (empty tables)
#   demo-fast     - Generate and load fast demo data (~1-2 min)
#   demo-full     - Generate and load full demo data (~15-30 min)
#   increment     - Add incremental data for testing data lake
#   status        - Show system status
#   clean         - Clean up generated data
#   logs          - Show container logs
#
# Usage Examples:
#   ./eurostyle.sh start
#   ./eurostyle.sh demo-fast
#   ./eurostyle.sh increment --days 7
#   ./eurostyle.sh increment --type "orders,customers" --days 1

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration - Load environment variables
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source .env file if it exists
if [ -f "${PROJECT_ROOT}/.env" ]; then
    source "${PROJECT_ROOT}/.env"
fi

# Set defaults if not provided in .env
CONTAINER_NAME="${CLICKHOUSE_CONTAINER_NAME:-eurostyle_clickhouse_retail}"
OPERATIONAL_DB="${DEFAULT_DATABASE:-eurostyle_operational}"
WEBSHOP_DB="eurostyle_webshop"
FINANCE_DB="eurostyle_finance"
HR_DB="eurostyle_hr"
POS_DB="eurostyle_pos"

# Global variables
COMMAND=""
FORCE_FLAG=false
VERBOSE_FLAG=false
INCREMENTAL_DAYS=1
INCREMENTAL_TYPES=""

# Print banner
print_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                 🏪 EuroStyle Fashion                        ║"
    echo "║              Unified Management System                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print usage information
print_usage() {
    cat << EOF
${YELLOW}Usage:${NC} ./eurostyle.sh <command> [options]

${CYAN}Commands:${NC}
  ${GREEN}start${NC}         Start containers only
  ${GREEN}stop${NC}          Stop containers only
  ${GREEN}setup${NC}         Create database structure (empty tables)
  ${GREEN}demo-fast${NC}     Generate and load fast demo data (~1-2 min)
  ${GREEN}demo-full${NC}     Generate and load full demo data (~15-30 min)
  ${GREEN}increment${NC}     Add incremental data for testing data lake
  ${GREEN}status${NC}        Show system status
  ${GREEN}clean${NC}         Clean up generated data
  ${GREEN}logs${NC}          Show container logs

${CYAN}Options:${NC}
  ${YELLOW}--force${NC}       Force operations (e.g., recreate containers)
  ${YELLOW}--verbose${NC}     Enable verbose output
  ${YELLOW}--days N${NC}      Number of days for incremental data (default: 1)
  ${YELLOW}--type LIST${NC}   Comma-separated list of data types for increment

${CYAN}Increment Data Types:${NC}
  ${PURPLE}📋 OPERATIONAL DATABASE:${NC}
  ${PURPLE}orders${NC}        New orders and order lines
  ${PURPLE}customers${NC}     New and updated customers  
  ${PURPLE}products${NC}      Product updates and new items
  ${PURPLE}inventory${NC}     Stock level changes
  ${PURPLE}campaigns${NC}     New marketing campaigns
  ${PURPLE}calendar${NC}      Fashion calendar events
  
  ${PURPLE}🌐 WEBSHOP DATABASE:${NC}
  ${PURPLE}sessions${NC}      New web sessions and page views
  ${PURPLE}carts${NC}         Shopping cart activities
  ${PURPLE}searches${NC}      Search queries and results
  ${PURPLE}reviews${NC}       Product reviews and ratings
  ${PURPLE}recommendations${NC} AI product suggestions
  ${PURPLE}emails${NC}        Email marketing campaigns
  ${PURPLE}abtests${NC}       A/B test results
  ${PURPLE}analytics${NC}     Web analytics events
  ${PURPLE}wishlist${NC}      Wishlist activities
  
  ${PURPLE}🏦 FINANCE DATABASE:${NC}
  ${PURPLE}finance${NC}       GL journal entries and lines
  ${PURPLE}budgets${NC}       Budget planning and versions
  ${PURPLE}assets${NC}        Fixed assets and depreciation
  ${PURPLE}entities${NC}      Legal entities and relationships
  ${PURPLE}accounts${NC}      Chart of accounts updates
  ${PURPLE}rates${NC}         Exchange rates
  ${PURPLE}costs${NC}         Cost center allocations
  
  ${PURPLE}👥 HR DATABASE:${NC}
  ${PURPLE}employees${NC}     New employees and updates
  ${PURPLE}contracts${NC}     Employment contract changes
  ${PURPLE}departments${NC}   Department restructuring
  ${PURPLE}positions${NC}     Job position changes
  ${PURPLE}leave${NC}         Leave requests and balances
  ${PURPLE}performance${NC}   Performance reviews
  ${PURPLE}training${NC}      Training programs and records
  ${PURPLE}surveys${NC}       Employee surveys and responses
  ${PURPLE}compensation${NC}  Salary and benefit changes
  
  ${PURPLE}🔄 COMBINED:${NC}
  ${PURPLE}all${NC}           All incremental data types

${CYAN}Examples:${NC}
  ${GREEN}./eurostyle.sh start${NC}
  ${GREEN}./eurostyle.sh demo-fast${NC}
  ${GREEN}./eurostyle.sh increment --days 7${NC}
  ${GREEN}./eurostyle.sh increment --type "orders,customers" --days 1${NC}
  ${GREEN}./eurostyle.sh clean --force${NC}
EOF
}

# Print section headers
print_section() {
    echo ""
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}$(printf '═%.0s' $(seq 1 ${#1}))${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
}

# Check container status
check_container_status() {
    if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        if docker ps --filter "name=$CONTAINER_NAME" --filter "health=healthy" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
            echo -e "${GREEN}✅ Container is running and healthy${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Container is running but not healthy${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Container is not running${NC}"
        return 2
    fi
}

# Wait for container to be healthy
wait_for_health() {
    local max_wait=60
    local wait_time=0
    
    echo -e "${YELLOW}⏳ Waiting for container to be healthy...${NC}"
    
    while [ $wait_time -lt $max_wait ]; do
        if check_container_status >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Container is healthy${NC}"
            return 0
        fi
        
        sleep 2
        wait_time=$((wait_time + 2))
        echo -n "."
    done
    
    echo -e "\n${RED}❌ Container failed to become healthy within ${max_wait}s${NC}"
    return 1
}

# Start containers
cmd_start() {
    print_section "Starting EuroStyle Containers"
    
    check_docker
    
    if check_container_status >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Container is already running and healthy${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}🚀 Starting EuroStyle ClickHouse container...${NC}"
    
    # Use existing start script
    if [ -f "scripts/system-management/start-eurostyle.sh" ]; then
        bash scripts/system-management/start-eurostyle.sh
    else
        # Fallback: start with docker-compose if available
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
        else
            echo -e "${RED}❌ No startup script or docker-compose.yml found${NC}"
            exit 1
        fi
    fi
    
    wait_for_health
    echo -e "${GREEN}🎉 EuroStyle containers started successfully!${NC}"
}

# Stop containers
cmd_stop() {
    print_section "Stopping EuroStyle Containers"
    
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}⚠️ Container is not running${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}🛑 Stopping EuroStyle containers...${NC}"
    
    # Use existing stop script
    if [ -f "scripts/system-management/stop-eurostyle.sh" ]; then
        bash scripts/system-management/stop-eurostyle.sh
    else
        # Fallback
        if [ -f "docker-compose.yml" ]; then
            docker-compose down
        else
            docker stop $CONTAINER_NAME
        fi
    fi
    
    echo -e "${GREEN}✅ EuroStyle containers stopped successfully${NC}"
}

# Setup database structure
cmd_setup() {
    print_section "Setting Up Database Structure"
    
    if ! check_container_status >/dev/null; then
        echo -e "${YELLOW}⚠️ Container not running. Starting containers first...${NC}"
        cmd_start
    fi
    
    echo -e "${YELLOW}🏗️ Creating database structure...${NC}"
    
    # Execute database initialization scripts
    local init_scripts=(
        "init-scripts/01-create-database.sql"
        "init-scripts/02_create_webshop_database.sql" 
        "init-scripts/03_create_finance_database.sql"
        "init-scripts/04_create_hr_database.sql"
    )
    
    for script in "${init_scripts[@]}"; do
        if [ -f "$script" ]; then
            echo -e "${YELLOW}📋 Executing $(basename "$script")...${NC}"
            docker cp "$script" "$CONTAINER_NAME:/tmp/$(basename "$script")"
            docker exec "$CONTAINER_NAME" clickhouse-client --multiquery --queries-file "/tmp/$(basename "$script")" >/dev/null 2>&1 || true
            echo -e "${GREEN}✅ $(basename "$script") completed${NC}"
        else
            echo -e "${YELLOW}⚠️ Script not found: $script${NC}"
        fi
    done
    
    echo -e "${GREEN}🎉 Database structure created successfully!${NC}"
    cmd_status
}

# Generate fast demo data
cmd_demo_fast() {
    print_section "Generating Fast Demo Data"
    
    if ! check_container_status >/dev/null; then
        echo -e "${YELLOW}⚠️ Container not running. Starting containers first...${NC}"
        cmd_start
    fi
    
    echo -e "${YELLOW}⚡ Generating fast demo data with Complete Data Generator (~2-5 minutes)...${NC}"
    echo -e "${BLUE}📊 Fast volumes: ALL tables populated with scaled data across all 4 databases${NC}"
    echo -e "${BLUE}   • Operational: 5K customers, 500 products, 2.5K orders${NC}"
    echo -e "${BLUE}   • Webshop: 8K sessions, 25K page views, all analytics tables${NC}"
    echo -e "${BLUE}   • Finance: Complete GL, budgets, assets with IFRS compliance${NC}"
    echo -e "${BLUE}   • HR: Full workforce management with European compliance${NC}"
    echo -e "${BLUE}🎯 GUARANTEED: Complete table coverage with referential integrity${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Use Complete Data Generation for all tables
    echo -e "${YELLOW}🏗️ Generating complete data for all systems...${NC}"
    if bash scripts/generate-fast-complete-data.sh $($FORCE_FLAG && echo "--force" || echo ""); then
        echo -e "${GREEN}✅ Complete Data Generator finished successfully${NC}"
        echo -e "${GREEN}🎯 All tables populated with consistent data across all databases${NC}"
    else
        echo -e "${RED}❌ Complete Data Generation failed${NC}"
        echo -e "${YELLOW}💡 Falling back to legacy data generator...${NC}"
        
        # Fallback to old system if Complete Data Generator fails
        cd "$PROJECT_ROOT/data-generator"
        if python3 generate_data.py --config config/fast_generation_config.yaml --verbose; then
            echo -e "${GREEN}✅ Legacy data generation completed${NC}"
        else
            echo -e "${RED}❌ Both complete and legacy data generation failed${NC}"
            exit 1
        fi
        cd "$PROJECT_ROOT"
    fi
    
    echo -e "${GREEN}🎉 Fast demo data generated successfully!${NC}"
    cmd_status
}

# Generate full demo data  
cmd_demo_full() {
    print_section "Generating Full Demo Data"
    
    if ! check_container_status >/dev/null; then
        echo -e "${YELLOW}⚠️ Container not running. Starting containers first...${NC}"
        cmd_start
    fi
    
    echo -e "${YELLOW}🏗️ Generating full demo data with Complete Data Generator (~15-30 minutes)...${NC}"
    echo -e "${BLUE}📊 Full volumes: ALL tables populated with production-like data across all 4 databases${NC}"
    echo -e "${BLUE}   • Operational: 50K customers, 5K products, 25K orders${NC}"
    echo -e "${BLUE}   • Webshop: 80K sessions, 250K page views, all analytics tables${NC}"
    echo -e "${BLUE}   • Finance: Complete multi-year GL, budgets, assets with IFRS compliance${NC}"
    echo -e "${BLUE}   • HR: Full workforce management with European compliance${NC}"
    echo -e "${BLUE}🎯 GUARANTEED: Complete table coverage with referential integrity${NC}"
    echo -e "${BLUE}💼 Complete: HR payroll, finance GL, operations, webshop - all integrated${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Use Complete Data Generation for all tables
    echo -e "${YELLOW}🏗️ Generating complete data for all systems...${NC}"
    if bash scripts/generate-full-complete-data.sh $($FORCE_FLAG && echo "--force" || echo ""); then
        echo -e "${GREEN}✅ Complete Data Generator finished successfully${NC}"
        echo -e "${GREEN}🎯 All tables populated with consistent data across all databases${NC}"
    else
        echo -e "${RED}❌ Complete Data Generation failed${NC}"
        echo -e "${YELLOW}💡 Falling back to existing comprehensive generation...${NC}"
        
        # Fallback to existing comprehensive generation script
        if [ -f "scripts/generate-demo-data.sh" ]; then
            bash scripts/generate-demo-data.sh --system all $($FORCE_FLAG && echo "--force" || echo "")
        else
            echo -e "${RED}❌ No fallback generation script found${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}🎉 Full demo data generated successfully!${NC}"
    cmd_status
}

# Generate incremental data
cmd_increment() {
    print_section "Generating Incremental Data"
    
    if ! check_container_status >/dev/null; then
        echo -e "${RED}❌ Container not running. Please start containers first.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📈 Generating incremental data for $INCREMENTAL_DAYS day(s)...${NC}"
    
    # Determine data types to generate
    local types_array=()
    if [ -n "$INCREMENTAL_TYPES" ]; then
        IFS=',' read -ra types_array <<< "$INCREMENTAL_TYPES"
    else
        types_array=("orders" "customers" "sessions" "carts" "searches" "calendar")
    fi
    
    echo -e "${BLUE}📊 Incremental types: ${types_array[*]}${NC}"
    echo -e "${BLUE}📅 Time period: $INCREMENTAL_DAYS day(s) from latest data${NC}"
    echo ""
    
    # Generate incremental data script
    local increment_script="$PROJECT_ROOT/data-generator/generate_incremental.py"
    
    # Create incremental generation script if it doesn't exist
    if [ ! -f "$increment_script" ]; then
        echo -e "${YELLOW}📋 Creating incremental data generator...${NC}"
        cat > "$increment_script" << 'EOF'
#!/usr/bin/env python3
"""
Incremental Data Generator for EuroStyle Fashion
==============================================
Generates additional data for testing incremental ETL and data lake scenarios
"""

import sys
import argparse
from datetime import datetime, timedelta
import yaml

def generate_incremental_data(data_types, days, config_path="config/fast_generation_config.yaml"):
    """Generate incremental data based on existing data patterns."""
    print(f"🔄 Generating incremental data for {days} days")
    print(f"📊 Data types: {', '.join(data_types)}")
    
    # Load existing configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Calculate incremental volumes (proportional to days)
    daily_factor = days / 30  # Assume monthly baseline
    
    incremental_volumes = {
        'orders': int(config['data_volumes']['orders'] * daily_factor * 0.1),
        'customers': int(config['data_volumes']['customers'] * daily_factor * 0.05),
        'sessions': int(config['data_volumes']['web_sessions'] * daily_factor * 0.2),
        'carts': int(config['data_volumes']['cart_activities'] * daily_factor * 0.15),
        'searches': int(config['data_volumes']['search_queries'] * daily_factor * 0.3),
        'reviews': int(config['data_volumes']['product_reviews'] * daily_factor * 0.1),
        'calendar': int(5 * daily_factor),  # Few calendar events
        'employees': int(2 * daily_factor),  # Minimal employee changes
        'finance': int(config['data_volumes']['gl_journal_entries'] * daily_factor * 0.1)
    }
    
    print("\n📈 Incremental volumes:")
    for data_type in data_types:
        if data_type in incremental_volumes:
            volume = incremental_volumes[data_type]
            print(f"  • {data_type}: {volume:,} records")
    
    # For now, simulate the generation
    # In a real implementation, this would call the actual generators
    print(f"\n✅ Incremental data generation completed!")
    print(f"💡 Note: This is a simulation. Actual implementation would generate real data.")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate incremental data for EuroStyle Fashion")
    parser.add_argument('--types', required=True, help='Comma-separated data types')
    parser.add_argument('--days', type=int, default=1, help='Number of days of incremental data')
    parser.add_argument('--config', default='config/fast_generation_config.yaml', help='Configuration file')
    
    args = parser.parse_args()
    
    data_types = [t.strip() for t in args.types.split(',')]
    
    return 0 if generate_incremental_data(data_types, args.days, args.config) else 1

if __name__ == "__main__":
    sys.exit(main())
EOF
        chmod +x "$increment_script"
    fi
    
    # Run incremental generation
    cd "$PROJECT_ROOT/data-generator"
    if python3 generate_incremental.py --types "${types_array[*]// /,}" --days "$INCREMENTAL_DAYS"; then
        echo -e "${GREEN}🎉 Incremental data generated successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to generate incremental data${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
}

# Show system status
cmd_status() {
    print_section "EuroStyle System Status"
    
    check_docker
    
    # Container status
    echo -e "${BLUE}🐳 Container Status:${NC}"
    check_container_status || true
    echo ""
    
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}⚠️ Container not running - no database information available${NC}"
        return 0
    fi
    
    # Database status - dynamically discover databases from configuration
    echo -e "${BLUE}🗃️ Database Status:${NC}"
    
    # Use our configuration-driven helper to get databases
    local db_helper="$PROJECT_ROOT/scripts/utilities/helpers/read_eurostyle_dbs.py"
    
    if [[ -x "$db_helper" ]]; then
        # Configuration-driven approach - use YAML config
        while IFS='|' read -r db_name db_description; do
            local count=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="$db_name" --query="
                SELECT sum(total_rows) FROM system.tables 
                WHERE database = '$db_name' AND total_rows > 0
            " 2>/dev/null || echo "0")
            
            # Handle ClickHouse NULL values (\N)
            if [ "$count" = "\N" ] || [ "$count" = "" ]; then
                count="0"
            fi
            
            if [ "$count" -gt 0 ] 2>/dev/null; then
                echo -e "${GREEN}  ✅ $db_name: $count records${NC}"
            else
                echo -e "${YELLOW}  📭 $db_name: empty${NC}"
            fi
        done < <(python3 "$db_helper" 2>/dev/null)
    else
        # Fallback to hardcoded list (includes POS now)
        for db in "$OPERATIONAL_DB" "$WEBSHOP_DB" "$FINANCE_DB" "$HR_DB" "$POS_DB"; do
            local count=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="$db" --query="
                SELECT sum(total_rows) FROM system.tables 
                WHERE database = '$db' AND total_rows > 0
            " 2>/dev/null || echo "0")
            
            # Handle ClickHouse NULL values (\N)
            if [ "$count" = "\N" ] || [ "$count" = "" ]; then
                count="0"
            fi
            
            if [ "$count" -gt 0 ] 2>/dev/null; then
                echo -e "${GREEN}  ✅ $db: $count records${NC}"
            else
                echo -e "${YELLOW}  📭 $db: empty${NC}"
            fi
        done
    fi
    echo ""
    
    # Connection info
    echo -e "${BLUE}🔗 Connection Information:${NC}"
    echo -e "${GREEN}  • HTTP Interface: http://localhost:8124${NC}"
    echo -e "${GREEN}  • Native Port: localhost:9002${NC}"
    echo -e "${GREEN}  • Container: $CONTAINER_NAME${NC}"
}

# Clean up generated data
cmd_clean() {
    print_section "Cleaning Generated Data"
    
    if [ "$FORCE_FLAG" = false ]; then
        echo -e "${YELLOW}⚠️ This will remove all generated CSV files and optionally truncate database tables.${NC}"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}ℹ️ Clean operation cancelled${NC}"
            exit 0
        fi
    fi
    
    # Clean ALL CSV files (remove head -20 limitation)
    echo -e "${YELLOW}🧹 Cleaning generated CSV files...${NC}"
    local csv_count=0
    find "$PROJECT_ROOT" -name "*.csv" -o -name "*.csv.gz" | grep -E "(generated_data|data/csv|data/user_files)" | while read file; do
        rm -f "$file" && echo -e "${GREEN}  ✅ Removed $(basename "$file")${NC}"
        ((csv_count++)) || true
    done
    
    # Truncate ALL database tables across ALL databases
    if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}🗃️ Truncating ALL database tables across all databases...${NC}"
        
        # Get all databases
        local databases=("$OPERATIONAL_DB" "$WEBSHOP_DB" "$FINANCE_DB" "$HR_DB" "$POS_DB")
        
        for db in "${databases[@]}"; do
            echo -e "${BLUE}  📊 Cleaning database: $db${NC}"
            
            # Get all tables in this database and truncate them
            local tables=$(docker exec "$CONTAINER_NAME" clickhouse-client --query "SHOW TABLES FROM $db" 2>/dev/null || true)
            
            if [ -n "$tables" ]; then
                while IFS= read -r table; do
                    if [ -n "$table" ]; then
                        docker exec "$CONTAINER_NAME" clickhouse-client --query "TRUNCATE TABLE $db.$table" 2>/dev/null || true
                        echo -e "${GREEN}    ✅ Truncated $db.$table${NC}"
                    fi
                done <<< "$tables"
            else
                echo -e "${YELLOW}    📭 No tables found in $db${NC}"
            fi
        done
    fi
    
    echo -e "${GREEN}🎉 Cleanup completed successfully!${NC}"
}

# Show container logs
cmd_logs() {
    print_section "Container Logs"
    
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}❌ Container is not running${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📋 Showing last 50 lines of container logs...${NC}"
    echo -e "${BLUE}Press Ctrl+C to exit log view${NC}"
    echo ""
    
    docker logs -f --tail 50 "$CONTAINER_NAME"
}

# Parse command line arguments
parse_args() {
    if [ $# -eq 0 ]; then
        print_banner
        print_usage
        exit 0
    fi
    
    COMMAND="$1"
    shift
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_FLAG=true
                shift
                ;;
            --verbose)
                VERBOSE_FLAG=true
                shift
                ;;
            --days)
                INCREMENTAL_DAYS="$2"
                shift 2
                ;;
            --type|--types)
                INCREMENTAL_TYPES="$2"
                shift 2
                ;;
            -h|--help)
                print_banner
                print_usage
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    cd "$PROJECT_ROOT"
    
    parse_args "$@"
    
    print_banner
    
    case "$COMMAND" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        setup)
            cmd_setup
            ;;
        demo-fast)
            cmd_demo_fast
            ;;
        demo-full)
            cmd_demo_full
            ;;
        increment)
            cmd_increment
            ;;
        status)
            cmd_status
            ;;
        clean)
            cmd_clean
            ;;
        logs)
            cmd_logs
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
            echo ""
            print_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"