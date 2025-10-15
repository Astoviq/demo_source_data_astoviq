#!/bin/bash

# Populate Critical Missing Tables
# ===============================
# This script addresses the 31 empty tables identified in the data quality analysis
# by populating the most critical business tables first.
#
# Phase 1: Finance Core Tables (chart_of_accounts, cost_centers, currencies, exchange_rates)
# Phase 2: HR Core Tables (departments, job_positions)  
# Phase 3: Essential webshop analytics
#
# Follows WARP.md guidelines for configuration-driven approach

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="eurostyle_clickhouse_retail"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

execute_sql() {
    local database=$1
    local sql=$2
    local description=$3
    
    echo -e "${YELLOW}📊 $description${NC}"
    
    if docker exec "$CONTAINER_NAME" clickhouse-client --database="$database" --query="$sql"; then
        echo -e "${GREEN}✅ Success: $description${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed: $description${NC}"
        return 1
    fi
}

check_container() {
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}❌ ClickHouse container '$CONTAINER_NAME' is not running${NC}"
        echo -e "${YELLOW}💡 Start it with: ./eurostyle.sh start${NC}"
        exit 1
    fi
}

populate_chart_of_accounts() {
    print_section "Phase 1.1: Chart of Accounts"
    
    local sql="INSERT INTO chart_of_accounts (account_id, account_code, account_name, account_type, account_subtype, parent_account_id, is_detail_account, normal_balance, account_category, ifrs_classification, is_active, created_date) VALUES
    ('1000', '1000', 'Cash and Cash Equivalents', 'ASSET', 'CURRENT_ASSET', NULL, true, 'DEBIT', 'ASSETS', 'CASH_EQUIVALENTS', true, '2024-01-01'),
    ('1100', '1100', 'Accounts Receivable', 'ASSET', 'CURRENT_ASSET', NULL, true, 'DEBIT', 'ASSETS', 'TRADE_RECEIVABLES', true, '2024-01-01'), 
    ('1200', '1200', 'Inventory', 'ASSET', 'CURRENT_ASSET', NULL, true, 'DEBIT', 'ASSETS', 'INVENTORIES', true, '2024-01-01'),
    ('1300', '1300', 'Prepaid Expenses', 'ASSET', 'CURRENT_ASSET', NULL, true, 'DEBIT', 'ASSETS', 'OTHER_CURRENT_ASSETS', true, '2024-01-01'),
    ('1500', '1500', 'Fixed Assets', 'ASSET', 'NON_CURRENT_ASSET', NULL, true, 'DEBIT', 'ASSETS', 'PROPERTY_EQUIPMENT', true, '2024-01-01'),
    ('2000', '2000', 'Accounts Payable', 'LIABILITY', 'CURRENT_LIABILITY', NULL, true, 'CREDIT', 'LIABILITIES', 'TRADE_PAYABLES', true, '2024-01-01'),
    ('2100', '2100', 'Tax Payable', 'LIABILITY', 'CURRENT_LIABILITY', NULL, true, 'CREDIT', 'LIABILITIES', 'TAX_LIABILITIES', true, '2024-01-01'),
    ('2200', '2200', 'Accrued Expenses', 'LIABILITY', 'CURRENT_LIABILITY', NULL, true, 'CREDIT', 'LIABILITIES', 'OTHER_CURRENT_LIABILITIES', true, '2024-01-01'),
    ('3000', '3000', 'Share Capital', 'EQUITY', 'EQUITY', NULL, true, 'CREDIT', 'EQUITY', 'SHARE_CAPITAL', true, '2024-01-01'),
    ('3100', '3100', 'Retained Earnings', 'EQUITY', 'EQUITY', NULL, true, 'CREDIT', 'EQUITY', 'RETAINED_EARNINGS', true, '2024-01-01'),
    ('4000', '4000', 'Sales Revenue', 'REVENUE', 'OPERATING_REVENUE', NULL, true, 'CREDIT', 'REVENUE', 'REVENUE', true, '2024-01-01'),
    ('4100', '4100', 'Other Revenue', 'REVENUE', 'OTHER_REVENUE', NULL, true, 'CREDIT', 'REVENUE', 'OTHER_INCOME', true, '2024-01-01'),
    ('5000', '5000', 'Cost of Goods Sold', 'EXPENSE', 'OPERATING_EXPENSE', NULL, true, 'DEBIT', 'EXPENSES', 'COST_OF_SALES', true, '2024-01-01'),
    ('5100', '5100', 'Salaries and Wages', 'EXPENSE', 'OPERATING_EXPENSE', NULL, true, 'DEBIT', 'EXPENSES', 'EMPLOYEE_BENEFITS', true, '2024-01-01'),
    ('5200', '5200', 'Marketing Expenses', 'EXPENSE', 'OPERATING_EXPENSE', NULL, true, 'DEBIT', 'EXPENSES', 'MARKETING_ADVERTISING', true, '2024-01-01'),
    ('5300', '5300', 'Operating Expenses', 'EXPENSE', 'OPERATING_EXPENSE', NULL, true, 'DEBIT', 'EXPENSES', 'OTHER_EXPENSES', true, '2024-01-01')"
    
    execute_sql "eurostyle_finance" "$sql" "Creating chart of accounts structure"
}

populate_currencies() {
    print_section "Phase 1.2: Currencies & Exchange Rates"
    
    local currency_sql="INSERT INTO currencies (currency_code, currency_name, currency_symbol, decimal_places, is_active, created_date, updated_date) VALUES
    ('EUR', 'Euro', '€', 2, true, '2024-01-01', '2024-01-01'),
    ('USD', 'US Dollar', '\$', 2, true, '2024-01-01', '2024-01-01'),
    ('GBP', 'British Pound', '£', 2, true, '2024-01-01', '2024-01-01'),
    ('CHF', 'Swiss Franc', 'CHF', 2, true, '2024-01-01', '2024-01-01'),
    ('SEK', 'Swedish Krona', 'SEK', 2, true, '2024-01-01', '2024-01-01')"
    
    execute_sql "eurostyle_finance" "$currency_sql" "Creating currency master data"
    
    local exchange_sql="INSERT INTO exchange_rates (from_currency, to_currency, rate_date, exchange_rate, created_date, updated_date) VALUES
    ('USD', 'EUR', '2024-01-01', 0.85, '2024-01-01', '2024-01-01'),
    ('GBP', 'EUR', '2024-01-01', 1.15, '2024-01-01', '2024-01-01'),  
    ('CHF', 'EUR', '2024-01-01', 0.93, '2024-01-01', '2024-01-01'),
    ('SEK', 'EUR', '2024-01-01', 0.089, '2024-01-01', '2024-01-01'),
    ('USD', 'EUR', '2024-10-01', 0.91, '2024-10-01', '2024-10-01'),
    ('GBP', 'EUR', '2024-10-01', 1.19, '2024-10-01', '2024-10-01')"
    
    execute_sql "eurostyle_finance" "$exchange_sql" "Creating exchange rates"
}

populate_cost_centers() {
    print_section "Phase 1.3: Cost Centers"
    
    # First get actual employee IDs and legal entities
    local managers=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_hr" \
        --query="SELECT employee_id FROM employees ORDER BY employee_id LIMIT 10" --format=TabSeparated | tr '\n' ' ')
    
    local entities=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_finance" \
        --query="SELECT entity_id FROM legal_entities LIMIT 5" --format=TabSeparated | tr '\n' ' ')
    
    local manager_array=($managers)
    local entity_array=($entities)
    local entity_id=${entity_array[0]:-"HOLDING_EU"}
    
    local sql="INSERT INTO cost_centers (cost_center_id, cost_center_code, cost_center_name, entity_id, cost_center_type, manager_name, department, is_active, created_date) VALUES
    ('CC_SALES_NL', 'CC_SALES_NL', 'Sales Netherlands', '$entity_id', 'PROFIT_CENTER', 'Sales Manager NL', 'Sales', true, '2024-01-01'),
    ('CC_SALES_DE', 'CC_SALES_DE', 'Sales Germany', '$entity_id', 'PROFIT_CENTER', 'Sales Manager DE', 'Sales', true, '2024-01-01'),
    ('CC_SALES_FR', 'CC_SALES_FR', 'Sales France', '$entity_id', 'PROFIT_CENTER', 'Sales Manager FR', 'Sales', true, '2024-01-01'),
    ('CC_MARKETING', 'CC_MARKETING', 'Marketing Department', '$entity_id', 'COST_CENTER', 'Marketing Manager', 'Marketing', true, '2024-01-01'),
    ('CC_IT', 'CC_IT', 'Information Technology', '$entity_id', 'COST_CENTER', 'IT Manager', 'Technology', true, '2024-01-01'),
    ('CC_HR', 'CC_HR', 'Human Resources', '$entity_id', 'COST_CENTER', 'HR Manager', 'Human Resources', true, '2024-01-01'),
    ('CC_FINANCE', 'CC_FINANCE', 'Finance Department', '$entity_id', 'COST_CENTER', 'Finance Manager', 'Finance', true, '2024-01-01'),
    ('CC_OPERATIONS', 'CC_OPERATIONS', 'Operations', '$entity_id', 'COST_CENTER', 'Operations Manager', 'Operations', true, '2024-01-01')"
    
    execute_sql "eurostyle_finance" "$sql" "Creating cost centers with proper schema"
}

populate_departments() {
    print_section "Phase 2.1: HR Departments"
    
    # Get actual employee IDs and entity ID
    local managers=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_hr" \
        --query="SELECT employee_id FROM employees ORDER BY employee_id LIMIT 8" --format=TabSeparated | tr '\n' ' ')
    
    local entities=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_finance" \
        --query="SELECT entity_id FROM legal_entities LIMIT 1" --format=TabSeparated)
    
    local manager_array=($managers)
    local entity_id=${entities:-"HOLDING_EU"}
    
    local sql="INSERT INTO departments (department_id, department_code, department_name, entity_id, parent_department_id, manager_employee_id, cost_center_id, department_type, location, is_active, created_date) VALUES
    ('DEPT_SALES_NL', 'SALES_NL', 'Sales Netherlands', '$entity_id', NULL, '${manager_array[0]}', 'CC_SALES_NL', 'REVENUE_GENERATING', 'Amsterdam', true, '2024-01-01'),
    ('DEPT_SALES_DE', 'SALES_DE', 'Sales Germany', '$entity_id', NULL, '${manager_array[1]}', 'CC_SALES_DE', 'REVENUE_GENERATING', 'Berlin', true, '2024-01-01'),
    ('DEPT_SALES_FR', 'SALES_FR', 'Sales France', '$entity_id', NULL, '${manager_array[2]}', 'CC_SALES_FR', 'REVENUE_GENERATING', 'Paris', true, '2024-01-01'),
    ('DEPT_MARKETING', 'MARKETING', 'Marketing Department', '$entity_id', NULL, '${manager_array[3]}', 'CC_MARKETING', 'SUPPORT', 'Amsterdam', true, '2024-01-01'),
    ('DEPT_IT', 'IT', 'Information Technology', '$entity_id', NULL, '${manager_array[4]}', 'CC_IT', 'SUPPORT', 'Amsterdam', true, '2024-01-01'),
    ('DEPT_HR', 'HR', 'Human Resources', '$entity_id', NULL, '${manager_array[5]}', 'CC_HR', 'SUPPORT', 'Amsterdam', true, '2024-01-01'),
    ('DEPT_FINANCE', 'FINANCE', 'Finance', '$entity_id', NULL, '${manager_array[6]}', 'CC_FINANCE', 'SUPPORT', 'Amsterdam', true, '2024-01-01'),
    ('DEPT_OPERATIONS', 'OPERATIONS', 'Operations', '$entity_id', NULL, '${manager_array[7]}', 'CC_OPERATIONS', 'OPERATIONS', 'Amsterdam', true, '2024-01-01')"
    
    execute_sql "eurostyle_hr" "$sql" "Creating department structure"
}

populate_job_positions() {
    print_section "Phase 2.2: Job Positions"
    
    local sql="INSERT INTO job_positions (position_id, position_title, department_id, job_family, salary_min_eur, salary_max_eur, job_level, status, created_date, updated_date) VALUES
    ('JOB_SALES_REP', 'Sales Representative', 'DEPT_SALES_NL', 'Sales', 35000.00, 55000.00, 1, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_SALES_MANAGER', 'Sales Manager', 'DEPT_SALES_NL', 'Sales', 55000.00, 80000.00, 3, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_MARKETING_SPEC', 'Marketing Specialist', 'DEPT_MARKETING', 'Marketing', 40000.00, 60000.00, 2, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_MARKETING_MANAGER', 'Marketing Manager', 'DEPT_MARKETING', 'Marketing', 60000.00, 85000.00, 3, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_SOFTWARE_DEV', 'Software Developer', 'DEPT_IT', 'Technology', 50000.00, 80000.00, 2, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_SENIOR_DEV', 'Senior Software Developer', 'DEPT_IT', 'Technology', 70000.00, 100000.00, 3, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_HR_SPECIALIST', 'HR Specialist', 'DEPT_HR', 'Human Resources', 38000.00, 55000.00, 2, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_FINANCE_ANALYST', 'Finance Analyst', 'DEPT_FINANCE', 'Finance', 42000.00, 65000.00, 2, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_OPERATIONS_COORD', 'Operations Coordinator', 'DEPT_OPERATIONS', 'Operations', 35000.00, 50000.00, 1, 'ACTIVE', '2024-01-01', '2024-01-01'),
    ('JOB_OPERATIONS_MANAGER', 'Operations Manager', 'DEPT_OPERATIONS', 'Operations', 55000.00, 75000.00, 3, 'ACTIVE', '2024-01-01', '2024-01-01')"
    
    execute_sql "eurostyle_hr" "$sql" "Creating job position master data"
}

populate_webshop_core() {
    print_section "Phase 3: Essential Webshop Analytics"
    
    # Generate search queries based on existing products
    local search_sql="INSERT INTO search_queries (search_id, session_id, customer_id, search_term, search_timestamp, results_count, clicked_result, purchase_resulted, created_at) 
    SELECT 
        'SEARCH_' || toString(number) as search_id,
        'SESS_' || toString(number % 2500 + 1) as session_id,
        CASE WHEN number % 3 = 0 THEN 'CUST_EU_' || lpad(toString(number % 220 + 1), 6, '0') ELSE null END as customer_id,
        CASE number % 20 
            WHEN 0 THEN 'dress'
            WHEN 1 THEN 'jeans'  
            WHEN 2 THEN 'shoes'
            WHEN 3 THEN 'jacket'
            WHEN 4 THEN 'sweater'
            WHEN 5 THEN 'skirt'
            WHEN 6 THEN 'blouse'
            WHEN 7 THEN 'pants'
            WHEN 8 THEN 'coat'
            WHEN 9 THEN 'boots'
            WHEN 10 THEN 'handbag'
            WHEN 11 THEN 'scarf'
            WHEN 12 THEN 'hat'
            WHEN 13 THEN 'belt'
            WHEN 14 THEN 'sunglasses'
            WHEN 15 THEN 'jewelry'
            WHEN 16 THEN 'watch'
            WHEN 17 THEN 'perfume'
            WHEN 18 THEN 'makeup'
            ELSE 'accessories'
        END as search_term,
        now() - INTERVAL (number % 30) DAY - INTERVAL (number % 24) HOUR as search_timestamp,
        (number % 50) + 1 as results_count,
        number % 4 = 0 as clicked_result,
        number % 10 = 0 as purchase_resulted,
        now() as created_at
    FROM numbers(1000)"
    
    execute_sql "eurostyle_webshop" "$search_sql" "Generating search queries based on realistic patterns"
    
    # Generate cart activities
    local cart_sql="INSERT INTO cart_activities (activity_id, session_id, customer_id, product_id, activity_type, quantity, activity_timestamp, created_at)
    SELECT 
        'CART_' || toString(number) as activity_id,
        'SESS_' || toString(number % 2500 + 1) as session_id,
        CASE WHEN number % 4 = 0 THEN 'CUST_EU_' || lpad(toString(number % 220 + 1), 6, '0') ELSE null END as customer_id,
        'PROD_' || lpad(toString(number % 100 + 1), 6, '0') as product_id,
        CASE number % 3
            WHEN 0 THEN 'ADD_TO_CART'
            WHEN 1 THEN 'REMOVE_FROM_CART' 
            ELSE 'UPDATE_QUANTITY'
        END as activity_type,
        (number % 5) + 1 as quantity,
        now() - INTERVAL (number % 7) DAY - INTERVAL (number % 24) HOUR as activity_timestamp,
        now() as created_at
    FROM numbers(1500)"
    
    execute_sql "eurostyle_webshop" "$cart_sql" "Generating cart activities with realistic abandonment patterns"
}

show_results() {
    print_section "Data Population Results"
    
    echo -e "${BLUE}📊 Updated Table Counts:${NC}"
    
    # Finance tables
    echo -e "${YELLOW}Finance Database:${NC}"
    for table in chart_of_accounts cost_centers currencies exchange_rates; do
        local count=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_finance" \
            --query="SELECT count() FROM $table" 2>/dev/null || echo "0")
        echo -e "   • $table: $count records"
    done
    
    # HR tables  
    echo -e "${YELLOW}HR Database:${NC}"
    for table in departments job_positions; do
        local count=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_hr" \
            --query="SELECT count() FROM $table" 2>/dev/null || echo "0")
        echo -e "   • $table: $count records"
    done
    
    # Webshop tables
    echo -e "${YELLOW}Webshop Database:${NC}"
    for table in search_queries cart_activities; do
        local count=$(docker exec "$CONTAINER_NAME" clickhouse-client --database="eurostyle_webshop" \
            --query="SELECT count() FROM $table" 2>/dev/null || echo "0")
        echo -e "   • $table: $count records"
    done
}

main() {
    print_section "Critical Missing Tables Population"
    echo -e "${YELLOW}🎯 Addressing 31 empty tables identified in data quality analysis${NC}"
    echo -e "${BLUE}📋 Populating most critical business tables first${NC}"
    echo ""
    
    check_container
    
    # Phase 1: Finance Core Tables
    populate_chart_of_accounts
    populate_currencies  
    populate_cost_centers
    
    # Phase 2: HR Core Tables
    populate_departments
    populate_job_positions
    
    # Phase 3: Essential Webshop Analytics
    populate_webshop_core
    
    # Show results
    show_results
    
    echo ""
    echo -e "${GREEN}🎉 Critical table population completed!${NC}"
    echo -e "${BLUE}📈 System now has proper foundation for:${NC}"
    echo -e "   • Complete financial GL structure"
    echo -e "   • HR department and job management" 
    echo -e "   • Cost center updates in incremental system"
    echo -e "   • Enhanced webshop analytics"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "   • Run incremental updates to test cost center functionality"
    echo -e "   • Generate additional analytics tables"
    echo -e "   • Update Universal Data Generator V2 to include these tables"
}

main "$@"