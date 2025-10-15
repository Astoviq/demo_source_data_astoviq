#!/usr/bin/env bash
# =====================================================
# EuroStyle Schema Inspector
# =====================================================
# Quick commands to inspect CSV files, database schemas, and row counts
# without manual checking or remembering ClickHouse queries

set -euo pipefail

# ClickHouse client command
CH_CLI="docker exec -i eurostyle_clickhouse_retail clickhouse-client"

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
  cat <<EOF
${BLUE}EuroStyle Schema Inspector${NC}

Usage:
  $0 csv:columns <path/to/file.csv[.gz]>     - Show CSV column headers
  $0 db:tables <database>                    - List tables in database
  $0 db:columns <database>                   - Show all columns in database
  $0 db:counts <database>                    - Show row counts for all tables
  $0 table:describe <database> <table>       - Describe table structure
  $0 table:count <database> <table>          - Show row count for specific table
  $0 system:overview                         - Complete system overview
  $0 system:counts                           - Row counts across all databases

Examples:
  $0 csv:columns data/csv/eurostyle_hr.employees.csv.gz
  $0 db:tables eurostyle_operational
  $0 db:counts eurostyle_operational
  $0 table:describe eurostyle_operational orders
  $0 system:overview
EOF
}

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ClickHouse container is running
check_clickhouse() {
  if ! docker ps --format "table {{.Names}}" | grep -q "eurostyle_clickhouse_retail"; then
    log_error "ClickHouse container 'eurostyle_clickhouse_retail' is not running"
    log_info "Start it with: ./eurostyle.sh start"
    exit 1
  fi
}

cmd="${1:-}"; shift || true

case "$cmd" in
  csv:columns)
    file_path="${1:-}"
    if [ -z "$file_path" ]; then
      log_error "File path required"
      usage
      exit 1
    fi
    
    if [ ! -f "$file_path" ]; then
      log_error "File not found: $file_path"
      exit 1
    fi
    
    log_info "CSV columns in: $file_path"
    echo
    
    if [[ "$file_path" == *.gz ]]; then
      gzip -cd "$file_path" | head -n1 | tr ',' '\n' | nl -v0
    else
      head -n1 "$file_path" | tr ',' '\n' | nl -v0
    fi
    ;;
    
  db:tables)
    database="${1:-}"
    if [ -z "$database" ]; then
      log_error "Database name required"
      usage
      exit 1
    fi
    
    check_clickhouse
    log_info "Tables in database: $database"
    echo
    
    $CH_CLI --query "SELECT name FROM system.tables WHERE database='${database}' ORDER BY name" 2>/dev/null || {
      log_error "Database '$database' not found or not accessible"
      exit 1
    }
    ;;
    
  db:columns)
    database="${1:-}"
    if [ -z "$database" ]; then
      log_error "Database name required"
      usage
      exit 1
    fi
    
    check_clickhouse
    log_info "All columns in database: $database"
    echo
    
    $CH_CLI --query "
    SELECT 
        table as Table,
        position as Pos,
        name as Column,
        type as Type
    FROM system.columns 
    WHERE database='${database}' 
    ORDER BY table, position
    FORMAT PrettyCompact
    " 2>/dev/null || {
      log_error "Database '$database' not found or not accessible"
      exit 1
    }
    ;;
    
  db:counts)
    database="${1:-}"
    if [ -z "$database" ]; then
      log_error "Database name required"
      usage
      exit 1
    fi
    
    check_clickhouse
    log_info "Row counts for all tables in: $database"
    echo
    
    # Get all tables first, then count each one
    tables=$($CH_CLI --query "SELECT name FROM system.tables WHERE database='${database}' ORDER BY name" 2>/dev/null) || {
      log_error "Database '$database' not found or not accessible"
      exit 1
    }
    
    total_rows=0
    printf "%-30s %15s\n" "Table" "Row Count"
    printf "%-30s %15s\n" "$(printf '%*s' 30 | tr ' ' '-')" "$(printf '%*s' 15 | tr ' ' '-')"
    
    while IFS= read -r table; do
      if [ -n "$table" ]; then
        count=$($CH_CLI --query "SELECT count(*) FROM ${database}.${table}" 2>/dev/null || echo "ERROR")
        printf "%-30s %15s\n" "$table" "$count"
        if [[ "$count" =~ ^[0-9]+$ ]]; then
          total_rows=$((total_rows + count))
        fi
      fi
    done <<< "$tables"
    
    printf "%-30s %15s\n" "$(printf '%*s' 30 | tr ' ' '-')" "$(printf '%*s' 15 | tr ' ' '-')"
    printf "%-30s %15s\n" "TOTAL" "$total_rows"
    ;;
    
  table:describe)
    database="${1:-}"
    table="${2:-}"
    if [ -z "$database" ] || [ -z "$table" ]; then
      log_error "Database and table name required"
      usage
      exit 1
    fi
    
    check_clickhouse
    log_info "Structure of table: $database.$table"
    echo
    
    $CH_CLI --query "DESCRIBE TABLE ${database}.${table} FORMAT PrettyCompact" 2>/dev/null || {
      log_error "Table '$database.$table' not found or not accessible"
      exit 1
    }
    ;;
    
  table:count)
    database="${1:-}"
    table="${2:-}"
    if [ -z "$database" ] || [ -z "$table" ]; then
      log_error "Database and table name required"
      usage
      exit 1
    fi
    
    check_clickhouse
    log_info "Row count for table: $database.$table"
    echo
    
    count=$($CH_CLI --query "SELECT count(*) FROM ${database}.${table}" 2>/dev/null) || {
      log_error "Table '$database.$table' not found or not accessible"
      exit 1
    }
    
    printf "%-30s %15s\n" "Table" "Row Count"
    printf "%-30s %15s\n" "$(printf '%*s' 30 | tr ' ' '-')" "$(printf '%*s' 15 | tr ' ' '-')"
    printf "%-30s %15s\n" "$database.$table" "$count"
    ;;
    
  system:overview)
    check_clickhouse
    log_info "EuroStyle Multi-Database System Overview"
    echo
    
    databases=("eurostyle_operational" "eurostyle_webshop" "eurostyle_finance" "eurostyle_hr" "eurostyle_pos")
    
    for db in "${databases[@]}"; do
      echo -e "${BLUE}=== $db ===${NC}"
      
      # Check if database exists
      db_exists=$($CH_CLI --query "SELECT count() FROM system.databases WHERE name='$db'" 2>/dev/null || echo "0")
      
      if [ "$db_exists" = "0" ]; then
        echo -e "${RED}Database not found${NC}"
        echo
        continue
      fi
      
      # Get table count and total rows
      table_count=$($CH_CLI --query "SELECT count() FROM system.tables WHERE database='$db'" 2>/dev/null || echo "0")
      
      if [ "$table_count" = "0" ]; then
        echo "No tables found"
        echo
        continue
      fi
      
      # Get total rows across all tables
      tables=$($CH_CLI --query "SELECT name FROM system.tables WHERE database='$db' ORDER BY name" 2>/dev/null || echo "")
      total_rows=0
      
      while IFS= read -r table; do
        if [ -n "$table" ]; then
          count=$($CH_CLI --query "SELECT count(*) FROM ${db}.${table}" 2>/dev/null || echo "0")
          if [[ "$count" =~ ^[0-9]+$ ]]; then
            total_rows=$((total_rows + count))
          fi
        fi
      done <<< "$tables"
      
      echo "Tables: $table_count"
      echo "Total Records: $(printf "%'d" $total_rows)"
      
      # Show top 5 tables by row count
      echo "Largest Tables:"
      while IFS= read -r table; do
        if [ -n "$table" ]; then
          count=$($CH_CLI --query "SELECT count(*) FROM ${db}.${table}" 2>/dev/null || echo "0")
          echo "$table $count"
        fi
      done <<< "$tables" | sort -k2 -nr | head -5 | while read table count; do
        printf "  %-25s %10s\n" "$table" "$(printf "%'d" $count)"
      done
      
      echo
    done
    ;;
    
  system:counts)
    check_clickhouse
    log_info "Row counts across all EuroStyle databases"
    echo
    
    databases=("eurostyle_operational" "eurostyle_webshop" "eurostyle_finance" "eurostyle_hr" "eurostyle_pos")
    grand_total=0
    
    printf "%-20s %-25s %15s\n" "Database" "Table" "Row Count"
    printf "%-20s %-25s %15s\n" "$(printf '%*s' 20 | tr ' ' '=')" "$(printf '%*s' 25 | tr ' ' '=')" "$(printf '%*s' 15 | tr ' ' '=')"
    
    for db in "${databases[@]}"; do
      # Check if database exists
      db_exists=$($CH_CLI --query "SELECT count() FROM system.databases WHERE name='$db'" 2>/dev/null || echo "0")
      
      if [ "$db_exists" = "0" ]; then
        printf "%-20s %-25s %15s\n" "$db" "NOT FOUND" "-"
        continue
      fi
      
      # Get all tables
      tables=$($CH_CLI --query "SELECT name FROM system.tables WHERE database='$db' ORDER BY name" 2>/dev/null || echo "")
      db_total=0
      first_table=true
      
      while IFS= read -r table; do
        if [ -n "$table" ]; then
          count=$($CH_CLI --query "SELECT count(*) FROM ${db}.${table}" 2>/dev/null || echo "0")
          
          if $first_table; then
            printf "%-20s %-25s %15s\n" "$db" "$table" "$(printf "%'d" $count)"
            first_table=false
          else
            printf "%-20s %-25s %15s\n" "" "$table" "$(printf "%'d" $count)"
          fi
          
          if [[ "$count" =~ ^[0-9]+$ ]]; then
            db_total=$((db_total + count))
            grand_total=$((grand_total + count))
          fi
        fi
      done <<< "$tables"
      
      if [ "$db_total" -gt 0 ]; then
        printf "%-20s %-25s %15s\n" "" "SUBTOTAL" "$(printf "%'d" $db_total)"
      fi
      
      printf "%-20s %-25s %15s\n" "" "" ""
    done
    
    printf "%-20s %-25s %15s\n" "$(printf '%*s' 20 | tr ' ' '=')" "$(printf '%*s' 25 | tr ' ' '=')" "$(printf '%*s' 15 | tr ' ' '=')"
    printf "%-20s %-25s %15s\n" "SYSTEM TOTAL" "" "$(printf "%'d" $grand_total)"
    ;;
    
  *)
    usage
    exit 1
    ;;
esac