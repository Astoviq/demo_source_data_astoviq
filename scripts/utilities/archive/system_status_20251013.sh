#!/bin/bash

# EuroStyle Source - Universal System Status
# ==========================================
# Configuration-driven status reporting following WARP.md rules
# Shows unified status across all 4 databases: operational, finance, hr, webshop
#
# Usage: ./system_status.sh [options]
# Options:
#   --format json     Output in JSON format
#   --detailed        Show detailed table information
#   --validate        Run validation checks
#   --help            Show this help message
#
# Author: EuroStyle Data Team
# Date: 2024-10-12
# Following WARP.md configuration-driven development rules

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONFIG_DIR="$PROJECT_ROOT/config"

# Load environment configuration
ENV_FILE="$CONFIG_DIR/environments/development.yaml"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Environment config not found: $ENV_FILE"
    exit 1
fi

# Extract ClickHouse configuration (simple YAML parsing)
CONTAINER_NAME=$(grep -A 10 "clickhouse:" "$ENV_FILE" | grep "container_name:" | sed 's/.*container_name: *"\(.*\)".*/\1/')
HTTP_PORT=$(grep -A 10 "clickhouse:" "$ENV_FILE" | grep "http_port:" | sed 's/.*http_port: *\([0-9]*\).*/\1/')
NATIVE_PORT=$(grep -A 10 "clickhouse:" "$ENV_FILE" | grep "native_port:" | sed 's/.*native_port: *\([0-9]*\).*/\1/')

# Default values if parsing fails
CONTAINER_NAME="${CONTAINER_NAME:-eurostyle_clickhouse_retail}"
HTTP_PORT="${HTTP_PORT:-8124}"
NATIVE_PORT="${NATIVE_PORT:-9002}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}📊 $1${NC}"
}

log_section() {
    echo
    echo -e "${CYAN}$1${NC}"
    echo "$(printf '=%.0s' {1..60})"
}

# Function to check ClickHouse connectivity
check_clickhouse_connection() {
    log_info "Testing ClickHouse connection..."
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        log_error "ClickHouse container '$CONTAINER_NAME' is not running"
        return 1
    fi
    
    # Test connection with simple query
    if docker exec "$CONTAINER_NAME" clickhouse-client --query "SELECT 1" >/dev/null 2>&1; then
        log_success "Connected to ClickHouse successfully"
        return 0
    else
        log_error "Failed to connect to ClickHouse"
        return 1
    fi
}

# Function to get database information
get_database_info() {
    local db_name="$1"
    
    # Get table count and total records
    local query="
    SELECT 
        database,
        count(*) as table_count,
        sum(total_rows) as total_records,
        formatReadableSize(sum(total_bytes)) as total_size
    FROM system.tables 
    WHERE database = '$db_name'
    GROUP BY database
    FORMAT TabSeparated
    "
    
    local result
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query "$query" 2>/dev/null || echo "ERROR")
    
    if [[ "$result" == "ERROR" || -z "$result" ]]; then
        echo "N/A	0	0	0 B"
    else
        echo "$result"
    fi
}

# Function to get detailed table information
get_table_details() {
    local db_name="$1"
    
    local query="
    SELECT 
        name as table_name,
        formatReadableQuantity(total_rows) as rows,
        formatReadableSize(total_bytes) as size,
        engine,
        metadata_modification_time
    FROM system.tables 
    WHERE database = '$db_name' AND engine NOT LIKE '%View'
    ORDER BY total_rows DESC
    FORMAT TabSeparated
    "
    
    docker exec "$CONTAINER_NAME" clickhouse-client --query "$query" 2>/dev/null || echo "ERROR"
}

# Function to check database status
get_database_status() {
    local db_name="$1"
    local description="$2"
    
    local info
    info=$(get_database_info "$db_name")
    
    if [[ "$info" == *"ERROR"* ]] || [[ "$info" == *"N/A"* ]]; then
        echo "❌ MISSING"
        return 1
    fi
    
    local table_count
    local total_records
    local total_size
    
    table_count=$(echo "$info" | cut -f2)
    total_records=$(echo "$info" | cut -f3)
    total_size=$(echo "$info" | cut -f4)
    
    if [[ "$total_records" -eq 0 ]]; then
        echo "⚠️  EMPTY ($table_count tables)"
        return 2
    else
        echo "✅ ACTIVE ($total_records records across $table_count tables, $total_size)"
        return 0
    fi
}

# Function to show system overview
show_system_overview() {
    log_header "EuroStyle Multi-Database System Status"
    
    # Container information
    local container_status
    if docker ps | grep -q "$CONTAINER_NAME"; then
        container_status="✅ Running"
        local uptime
        uptime=$(docker ps --format "table {{.Status}}" | grep "$CONTAINER_NAME" | head -1 || echo "Unknown")
        log_info "Container: $CONTAINER_NAME ($uptime)"
    else
        container_status="❌ Stopped"
        log_error "Container: $CONTAINER_NAME (not running)"
    fi
    
    log_info "HTTP Port: localhost:$HTTP_PORT"
    log_info "Native Port: localhost:$NATIVE_PORT"
    echo
}

# Function to show database statuses
show_database_statuses() {
    log_section "Database Status Overview"
    
    # Define databases with descriptions
    declare -A databases
    databases["eurostyle_operational"]="Customer orders, products, stores, inventory"
    databases["eurostyle_finance"]="General ledger, budgets, entities, depreciation"
    databases["eurostyle_hr"]="Employees, contracts, performance, leave management"
    databases["eurostyle_webshop"]="Web analytics, sessions, events, campaigns"
    
    local overall_status=0
    local total_records=0
    
    for db_name in "${!databases[@]}"; do
        local description="${databases[$db_name]}"
        local status_text
        status_text=$(get_database_status "$db_name" "$description")
        local status_code=$?
        
        # Extract record count for total
        if [[ "$status_text" == *"records"* ]]; then
            local records
            records=$(echo "$status_text" | sed -n 's/.*(\([0-9,]*\) records.*/\1/p' | tr -d ',')
            total_records=$((total_records + records))
        fi
        
        # Tree-style output with proper alignment
        local display_name
        display_name=$(echo "$db_name" | sed 's/eurostyle_//')
        printf "├── %-15s %s\n" "$display_name:" "$status_text"
        
        if [[ $status_code -gt 0 ]]; then
            overall_status=$status_code
        fi
    done
    
    echo
    log_info "Total Records: $(printf "%'d" $total_records)"
    
    return $overall_status
}

# Function to show detailed table information
show_detailed_tables() {
    if [[ "${DETAILED:-false}" != "true" ]]; then
        return 0
    fi
    
    log_section "Detailed Table Information"
    
    declare -A databases
    databases["eurostyle_operational"]="Operational Database"
    databases["eurostyle_finance"]="Finance Database"
    databases["eurostyle_hr"]="HR Database"
    databases["eurostyle_webshop"]="Webshop Analytics Database"
    
    for db_name in "${!databases[@]}"; do
        local description="${databases[$db_name]}"
        echo
        log_info "$description ($db_name)"
        echo "$(printf '─%.0s' {1..50})"
        
        local table_info
        table_info=$(get_table_details "$db_name")
        
        if [[ "$table_info" == "ERROR" || -z "$table_info" ]]; then
            echo "No tables found or database not accessible"
        else
            printf "%-25s %15s %10s %20s\n" "TABLE" "ROWS" "SIZE" "ENGINE"
            echo "$(printf '─%.0s' {1..75})"
            echo "$table_info" | while IFS=$'\t' read -r table_name rows size engine modification_time; do
                printf "%-25s %15s %10s %20s\n" "$table_name" "$rows" "$size" "$engine"
            done
        fi
    done
}

# Function to run validation checks
run_validation_checks() {
    if [[ "${VALIDATE:-false}" != "true" ]]; then
        return 0
    fi
    
    log_section "Cross-Database Validation"
    
    log_info "Running referential integrity checks..."
    
    # Check if related data exists across databases
    local checks_passed=0
    local total_checks=0
    
    # Check 1: HR employees should have corresponding legal entities in Finance
    total_checks=$((total_checks + 1))
    local hr_finance_check
    hr_finance_check=$(docker exec "$CONTAINER_NAME" clickhouse-client --query "
        SELECT count(*) 
        FROM eurostyle_hr.employees e
        LEFT JOIN eurostyle_finance.legal_entities le ON e.entity_id = le.entity_id
        WHERE le.entity_id IS NULL
    " 2>/dev/null || echo "ERROR")
    
    if [[ "$hr_finance_check" == "0" ]]; then
        log_success "HR-Finance entity integrity: PASSED"
        checks_passed=$((checks_passed + 1))
    else
        log_warning "HR-Finance entity integrity: $hr_finance_check orphaned records"
    fi
    
    # Check 2: Operational stores should exist for HR store assignments
    total_checks=$((total_checks + 1))
    local hr_ops_check
    hr_ops_check=$(docker exec "$CONTAINER_NAME" clickhouse-client --query "
        SELECT count(*) 
        FROM eurostyle_hr.employment_contracts ec
        LEFT JOIN eurostyle_operational.stores s ON ec.store_id = s.store_id
        WHERE ec.store_id IS NOT NULL AND s.store_id IS NULL
    " 2>/dev/null || echo "ERROR")
    
    if [[ "$hr_ops_check" == "0" ]]; then
        log_success "HR-Operational store integrity: PASSED"
        checks_passed=$((checks_passed + 1))
    else
        log_warning "HR-Operational store integrity: $hr_ops_check orphaned records"
    fi
    
    # Check 3: CRITICAL - Revenue consistency between operational and finance
    total_checks=$((total_checks + 1))
    log_info "🔍 Checking revenue consistency between operational orders and finance GL..."
    
    local revenue_check
    revenue_check=$(docker exec "$CONTAINER_NAME" clickhouse-client --query "
        WITH operational_total AS (
          SELECT coalesce(sum(total_amount_eur), 0) as ops_revenue
          FROM eurostyle_operational.orders
        ),
        finance_total AS (
          SELECT coalesce(sum(credit_amount_eur), 0) as fin_revenue  
          FROM eurostyle_finance.gl_journal_lines
          WHERE account_code = '4000'
        )
        SELECT 
          ops_revenue,
          fin_revenue,
          abs(ops_revenue - fin_revenue) as variance,
          CASE WHEN ops_revenue > 0 
               THEN (abs(ops_revenue - fin_revenue) / ops_revenue * 100)
               ELSE 0 END as variance_percent
        FROM operational_total CROSS JOIN finance_total
        FORMAT TabSeparated
    " 2>/dev/null || echo "ERROR")
    
    if [[ "$revenue_check" == "ERROR" ]]; then
        log_warning "Revenue consistency check: Unable to validate (missing data)"
    else
        local ops_revenue=$(echo "$revenue_check" | cut -f1)
        local fin_revenue=$(echo "$revenue_check" | cut -f2) 
        local variance=$(echo "$revenue_check" | cut -f3)
        local variance_percent=$(echo "$revenue_check" | cut -f4)
        
        # Convert to integer for comparison (variance_percent as decimal)
        local variance_int=$(echo "$variance_percent" | cut -d. -f1)
        
        if [[ "$variance_int" -le 5 ]]; then
            log_success "Revenue consistency: PASSED ($(printf "%.1f" "$variance_percent")% variance)"
            checks_passed=$((checks_passed + 1))
        else
            log_warning "Revenue consistency: FAILED ($(printf "%.1f" "$variance_percent")% variance > 5% threshold)"
            log_warning "  Operational revenue: €$(printf "%'.2f" "$ops_revenue")"
            log_warning "  Finance GL revenue: €$(printf "%'.2f" "$fin_revenue")"
        fi
    fi
    
    echo
    log_info "Validation Summary: $checks_passed/$total_checks checks passed"
    
    if [[ $checks_passed -eq $total_checks ]]; then
        return 0
    else
        return 1
    fi
}

# Function to output JSON format
output_json() {
    if [[ "${FORMAT:-}" != "json" ]]; then
        return 0
    fi
    
    echo "{"
    echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
    echo "  \"system\": {"
    echo "    \"container\": \"$CONTAINER_NAME\","
    echo "    \"http_port\": $HTTP_PORT,"
    echo "    \"native_port\": $NATIVE_PORT"
    echo "  },"
    echo "  \"databases\": ["
    
    declare -A databases
    databases["eurostyle_operational"]="Customer orders, products, stores, inventory"
    databases["eurostyle_finance"]="General ledger, budgets, entities, depreciation"  
    databases["eurostyle_hr"]="Employees, contracts, performance, leave management"
    databases["eurostyle_webshop"]="Web analytics, sessions, events, campaigns"
    
    local first=true
    for db_name in "${!databases[@]}"; do
        if [[ "$first" == "false" ]]; then
            echo ","
        fi
        first=false
        
        local info
        info=$(get_database_info "$db_name")
        local table_count
        local total_records
        local total_size
        
        table_count=$(echo "$info" | cut -f2)
        total_records=$(echo "$info" | cut -f3)
        total_size=$(echo "$info" | cut -f4)
        
        echo "    {"
        echo "      \"name\": \"$db_name\","
        echo "      \"description\": \"${databases[$db_name]}\","
        echo "      \"table_count\": $table_count,"
        echo "      \"total_records\": $total_records,"
        echo "      \"total_size\": \"$total_size\""
        echo "    }"
    done
    
    echo "  ]"
    echo "}"
}

# Function to show help
show_help() {
    cat << EOF
EuroStyle Source - Universal System Status

USAGE:
    ./system_status.sh [OPTIONS]

OPTIONS:
    --format json     Output status information in JSON format
    --detailed        Show detailed table-level information
    --validate        Run cross-database validation checks
    --help           Show this help message

EXAMPLES:
    ./system_status.sh                    # Basic status overview
    ./system_status.sh --detailed         # Include table details
    ./system_status.sh --validate         # Include validation checks
    ./system_status.sh --format json      # JSON output for automation

DESCRIPTION:
    Universal status reporting script that shows the health and data volume
    across all 4 EuroStyle databases: operational, finance, hr, and webshop.
    
    Follows WARP.md configuration-driven development rules by reading
    database configuration from YAML files.

EOF
}

# Main execution function
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --format)
                FORMAT="$2"
                shift 2
                ;;
            --detailed)
                DETAILED="true"
                shift
                ;;
            --validate)
                VALIDATE="true" 
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # JSON output mode
    if [[ "${FORMAT:-}" == "json" ]]; then
        output_json
        exit 0
    fi
    
    # Standard output mode
    local overall_status=0
    
    show_system_overview
    
    # Check connectivity first
    if ! check_clickhouse_connection; then
        exit 1
    fi
    
    # Show database statuses
    if ! show_database_statuses; then
        overall_status=1
    fi
    
    # Show detailed information if requested
    show_detailed_tables
    
    # Run validation if requested
    if [[ "${VALIDATE:-false}" == "true" ]]; then
        if ! run_validation_checks; then
            overall_status=1
        fi
    fi
    
    echo
    if [[ $overall_status -eq 0 ]]; then
        log_success "System status: All databases operational"
    else
        log_warning "System status: Some issues detected"
    fi
    
    exit $overall_status
}

# Execute main function
main "$@"