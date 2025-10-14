#!/bin/bash

# EuroStyle Fashion - HR Data Loader
# ==================================
# Loads HR CSV data into ClickHouse database
# Includes schema setup and data validation
#
# Usage: ./load_hr_data.sh [options]
# Options:
#   --setup     Create database schema first
#   --validate  Validate data after loading
#   --help      Show this help message
#
# Author: EuroStyle Fashion Data Team
# Date: 2024-10-10

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"  # Go up two levels
SCHEMA_DIR="$PROJECT_ROOT/init-scripts"
DATA_DIR="$PROJECT_ROOT/data/csv"

# ClickHouse configuration
CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-9000}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
CLICKHOUSE_DB="eurostyle_hr"
CONTAINER_NAME="${CONTAINER_NAME:-eurostyle_clickhouse_retail}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_section() {
    echo
    echo -e "${BLUE}📋 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Function to run ClickHouse query
run_clickhouse_query() {
    local query="$1"
    local description="$2"
    
    log_info "$description"
    
    docker exec "$CONTAINER_NAME" clickhouse-client \
        --multiquery \
        --query="$query"
}

# Function to load CSV file into ClickHouse table
load_csv_to_table() {
    local csv_file="$1"
    local table_name="$2"
    local description="$3"
    
    if [[ ! -f "$csv_file" ]]; then
        log_error "CSV file not found: $csv_file"
        return 1
    fi
    
    log_info "$description"
    
    # Get file size for progress indication
    local file_size=$(du -h "$csv_file" | cut -f1)
    log_info "Loading $csv_file ($file_size) into $table_name"
    
    # Load CSV data using docker exec (handle compressed files and schema)
    if [[ "$csv_file" == *.gz ]]; then
        # For compressed files, decompress and pipe to ClickHouse
        # Use CSVWithNames format to match columns by name instead of position
        gunzip -c "$csv_file" | docker exec -i "$CONTAINER_NAME" clickhouse-client \
            --format_csv_delimiter="," \
            --input_format_csv_empty_as_default=1 \
            --query="INSERT INTO $table_name FORMAT CSVWithNames"
    else
        # For uncompressed files
        docker exec -i "$CONTAINER_NAME" clickhouse-client \
            --format_csv_delimiter="," \
            --input_format_csv_empty_as_default=1 \
            --query="INSERT INTO $table_name FORMAT CSVWithNames" \
            < "$csv_file"
    fi
    
    # Get row count
    local row_count
    row_count=$(docker exec "$CONTAINER_NAME" clickhouse-client \
        --query="SELECT count() FROM $table_name")
    
    log_success "Loaded $(echo "$row_count" | tr -d ' ') rows into $table_name"
}

# Function to setup HR database schema
setup_schema() {
    log_section "Setting Up HR Database Schema"
    
    local schema_file="$SCHEMA_DIR/04_create_hr_database.sql"
    
    if [[ ! -f "$schema_file" ]]; then
        log_error "Schema file not found: $schema_file"
        exit 1
    fi
    
    log_info "Creating HR database and tables from $schema_file"
    
    # Execute the schema file
    docker exec -i "$CONTAINER_NAME" clickhouse-client \
        --multiquery \
        < "$schema_file"
    
    log_success "HR database schema created successfully"
}

# Function to load all HR data files
load_hr_data() {
    log_section "Loading HR Data Files"
    
    # Define the loading order with table and CSV file pairs (compressed files)
    local hr_files=(
        "eurostyle_hr.departments:eurostyle_hr.departments.csv.gz"
        "eurostyle_hr.job_positions:eurostyle_hr.job_positions.csv.gz"
        "eurostyle_hr.employees:eurostyle_hr.employees.csv.gz"
        "eurostyle_hr.employment_contracts:eurostyle_hr.employment_contracts.csv.gz"
        "eurostyle_hr.compensation_history:eurostyle_hr.compensation_history.csv.gz"
        "eurostyle_hr.leave_balances:eurostyle_hr.leave_balances.csv.gz"
        "eurostyle_hr.leave_requests:eurostyle_hr.leave_requests.csv.gz"
        "eurostyle_hr.performance_cycles:eurostyle_hr.performance_cycles.csv.gz"
        "eurostyle_hr.performance_reviews:eurostyle_hr.performance_reviews.csv.gz"
        "eurostyle_hr.training_programs:eurostyle_hr.training_programs.csv.gz"
        "eurostyle_hr.employee_training:eurostyle_hr.employee_training.csv.gz"
        "eurostyle_hr.employee_surveys:eurostyle_hr.employee_surveys.csv.gz"
        "eurostyle_hr.survey_responses:eurostyle_hr.survey_responses.csv.gz"
    )
    
    local loaded_files=0
    local total_files=${#hr_files[@]}
    
    for file_mapping in "${hr_files[@]}"; do
        local table_name="${file_mapping%:*}"
        local csv_file="${file_mapping#*:}"
        local csv_path="$DATA_DIR/$csv_file"
        
        if [[ -f "$csv_path" ]]; then
            load_csv_to_table "$csv_path" "$table_name" "Loading ${csv_file} into ${table_name}"
            ((loaded_files++))
        else
            log_warning "CSV file not found: $csv_path (skipping)"
        fi
    done
    
    log_success "Loaded $loaded_files/$total_files HR data files"
}

# Function to validate loaded data
validate_data() {
    log_section "Validating HR Data"
    
    log_info "Running data validation checks..."
    
    # Run validation queries directly
    local query result
    
    query="SELECT count() FROM eurostyle_hr.employees WHERE employee_status = 'ACTIVE'"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Active Employees: Query failed"
    else
        log_info "Active Employees: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.employment_contracts WHERE contract_status = 'ACTIVE'"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Active Contracts: Query failed"
    else
        log_info "Active Contracts: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.departments WHERE is_active = true"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Departments: Query failed"
    else
        log_info "Departments: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.job_positions WHERE is_active = true"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Job Positions: Query failed"
    else
        log_info "Job Positions: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.training_programs WHERE is_active = true"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Training Programs: Query failed"
    else
        log_info "Training Programs: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.performance_reviews WHERE review_status = 'FINAL'"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Performance Reviews: Query failed"
    else
        log_info "Performance Reviews: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.leave_requests WHERE request_status = 'APPROVED'"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Leave Requests: Query failed"
    else
        log_info "Leave Requests: $(echo "$result" | tr -d ' ') records"
    fi
    
    query="SELECT count() FROM eurostyle_hr.leave_balances WHERE balance_year = 2024"
    result=$(docker exec "$CONTAINER_NAME" clickhouse-client --query="$query" 2>/dev/null || echo "ERROR")
    if [[ "$result" == "ERROR" ]]; then
        log_error "Current Year Leave Balances: Query failed"
    else
        log_info "Current Year Leave Balances: $(echo "$result" | tr -d ' ') records"
    fi
    
    # Check for data consistency
    log_info "Checking data consistency..."
    
    # Check if all employees have contracts
    local employees_without_contracts
    employees_without_contracts=$(docker exec "$CONTAINER_NAME" clickhouse-client \
        --query="SELECT count() FROM eurostyle_hr.employees e LEFT JOIN eurostyle_hr.employment_contracts c ON e.employee_id = c.employee_id WHERE c.employee_id IS NULL AND e.employee_status = 'ACTIVE'" 2>/dev/null || echo "ERROR")
    
    if [[ "$employees_without_contracts" == "0" ]]; then
        log_success "All active employees have employment contracts"
    elif [[ "$employees_without_contracts" == "ERROR" ]]; then
        log_warning "Could not check employee-contract consistency"
    else
        log_warning "$employees_without_contracts active employees without contracts"
    fi
    
    log_success "Data validation completed"
}

# Function to show HR database summary
show_summary() {
    log_section "HR Database Summary"
    
    # Get table sizes
    local tables=(
        "departments"
        "job_positions"
        "employees"
        "employment_contracts"
        "compensation_history"
        "leave_balances"
        "leave_requests"
        "performance_cycles"
        "performance_reviews"
        "training_programs"
        "employee_training"
        "employee_surveys"
        "survey_responses"
    )
    
    local total_rows=0
    
    log_info "HR Database Table Summary:"
    printf "%-25s %15s\n" "Table" "Row Count"
    printf "%-25s %15s\n" "$(printf '%.0s-' {1..25})" "$(printf '%.0s-' {1..15})"
    
    for table in "${tables[@]}"; do
        local row_count
        row_count=$(docker exec "$CONTAINER_NAME" clickhouse-client \
            --query="SELECT count() FROM eurostyle_hr.$table" 2>/dev/null || echo "N/A")
        
        printf "%-25s %15s\n" "$table" "$row_count"
        
        if [[ "$row_count" != "N/A" && "$row_count" =~ ^[0-9]+$ ]]; then
            total_rows=$((total_rows + row_count))
        fi
    done
    
    printf "%-25s %15s\n" "$(printf '%.0s-' {1..25})" "$(printf '%.0s-' {1..15})"
    printf "%-25s %15s\n" "TOTAL" "$total_rows"
    
    log_success "HR database loaded with $(printf "%'d" $total_rows) total records"
}

# Function to display help
show_help() {
    cat << EOF
EuroStyle Fashion - HR Data Loader
==================================

This script loads HR CSV data into ClickHouse database with European employment law compliance.

Usage: $0 [options]

Options:
    --setup         Create database schema before loading data
    --validate      Validate data consistency after loading
    --summary       Show database summary after loading
    --help          Show this help message

Environment Variables:
    CLICKHOUSE_HOST     ClickHouse server host (default: localhost)
    CLICKHOUSE_PORT     ClickHouse server port (default: 9000)
    CLICKHOUSE_USER     ClickHouse username (default: default)
    CLICKHOUSE_PASSWORD ClickHouse password (default: empty)

Examples:
    $0 --setup                    # Setup schema and load data
    $0 --validate --summary       # Load data with validation and summary
    $0 --setup --validate         # Full setup, load, and validation

Files Required:
    - schemas/eurostyle_hr_schema.sql
    - eurostyle_hr.*.csv (13 files)

EOF
}

# Main function
main() {
    local setup_schema=false
    local validate_after=false
    local show_summary_after=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --setup)
                setup_schema=true
                shift
                ;;
            --validate)
                validate_after=true
                shift
                ;;
            --summary)
                show_summary_after=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "Starting HR data loading process..."
    log_info "ClickHouse: $CLICKHOUSE_USER@$CLICKHOUSE_HOST:$CLICKHOUSE_PORT"
    
    # Check if Docker container is available
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        log_error "EuroStyle ClickHouse container '$CONTAINER_NAME' is not running"
        log_info "Start it with: ./scripts/start-eurostyle.sh"
        exit 1
    fi
    
    # Test ClickHouse connection
    if ! run_clickhouse_query "SELECT 1" "Testing ClickHouse connection"; then
        log_error "Cannot connect to ClickHouse server"
        exit 1
    fi
    
    log_success "Connected to ClickHouse successfully"
    
    # Setup schema if requested
    if [[ "$setup_schema" == true ]]; then
        setup_schema
    fi
    
    # Load HR data
    load_hr_data
    
    # Validate data if requested
    if [[ "$validate_after" == true ]]; then
        validate_data
    fi
    
    # Show summary if requested
    if [[ "$show_summary_after" == true ]]; then
        show_summary
    fi
    
    log_success "HR data loading completed successfully! 🎉"
    log_info "HR database is ready for analysis and reporting."
}

# Run main function with all arguments
main "$@"