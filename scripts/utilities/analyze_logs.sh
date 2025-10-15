#!/bin/bash
# EuroStyle Fashion - Log Analysis Utility
# ========================================
# Easily view and analyze EuroStyle logs with filtering and formatting

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

LOGS_DIR="logs"

print_usage() {
    echo -e "${BLUE}🔍 EuroStyle Log Analyzer${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  errors          Show only errors from all logs"
    echo "  warnings        Show only warnings from all logs"
    echo "  recent          Show recent activity (last 100 lines)"
    echo "  generation      Show data generation logs"
    echo "  incremental     Show incremental generation logs"
    echo "  loading         Show data loading logs"
    echo "  summary         Show summary of log files and sizes"
    echo "  tail [COMPONENT] Follow logs in real-time"
    echo "  search PATTERN  Search for specific pattern in logs"
    echo ""
    echo "Options:"
    echo "  --today         Only show today's logs"
    echo "  --count N       Show last N lines (default: 50)"
    echo ""
    echo "Examples:"
    echo "  $0 errors                     # Show all errors"
    echo "  $0 recent --count 200         # Show last 200 log entries"
    echo "  $0 search \"Failed to load\"    # Search for loading failures"
    echo "  $0 tail incremental           # Follow incremental logs live"
}

check_logs_exist() {
    if [ ! -d "$LOGS_DIR" ]; then
        echo -e "${RED}❌ Logs directory not found: $LOGS_DIR${NC}"
        echo -e "${YELLOW}💡 Run some data generation operations first${NC}"
        exit 1
    fi
}

get_log_files() {
    local component="$1"
    local today_only="$2"
    
    if [ "$today_only" = "true" ]; then
        local today=$(date +%Y%m%d)
        find "$LOGS_DIR" -name "*${component}*${today}*.log" 2>/dev/null
    else
        find "$LOGS_DIR" -name "*${component}*.log" 2>/dev/null
    fi
}

show_errors() {
    echo -e "${RED}🚨 ERROR LOGS${NC}"
    echo "=============="
    
    local log_files=$(get_log_files "" "$1")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No log files found${NC}"
        return
    fi
    
    echo "$log_files" | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local errors=$(grep -i "ERROR\|❌\|FAILED" "$logfile" 2>/dev/null || true)
            if [ ! -z "$errors" ]; then
                echo -e "\n${PURPLE}📄 $(basename "$logfile")${NC}"
                echo "$errors" | while read -r line; do
                    echo -e "${RED}  $line${NC}"
                done
            fi
        fi
    done
}

show_warnings() {
    echo -e "${YELLOW}⚠️ WARNING LOGS${NC}"
    echo "================"
    
    local log_files=$(get_log_files "" "$1")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No log files found${NC}"
        return
    fi
    
    echo "$log_files" | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local warnings=$(grep -i "WARNING\|⚠️" "$logfile" 2>/dev/null || true)
            if [ ! -z "$warnings" ]; then
                echo -e "\n${PURPLE}📄 $(basename "$logfile")${NC}"
                echo "$warnings" | while read -r line; do
                    echo -e "${YELLOW}  $line${NC}"
                done
            fi
        fi
    done
}

show_recent() {
    local count=${1:-50}
    local today_only="$2"
    
    echo -e "${BLUE}📋 RECENT ACTIVITY (last $count lines)${NC}"
    echo "======================================"
    
    local log_files=$(get_log_files "" "$today_only")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No log files found${NC}"
        return
    fi
    
    # Get most recent log entries across all files
    echo "$log_files" | xargs ls -t 2>/dev/null | head -5 | while read -r logfile; do
        if [ -f "$logfile" ]; then
            echo -e "\n${PURPLE}📄 $(basename "$logfile")${NC}"
            tail -n "$count" "$logfile" | while read -r line; do
                # Color code by log level
                if echo "$line" | grep -q "ERROR\|❌\|FAILED"; then
                    echo -e "${RED}  $line${NC}"
                elif echo "$line" | grep -q "WARNING\|⚠️"; then
                    echo -e "${YELLOW}  $line${NC}"
                elif echo "$line" | grep -q "✅\|COMPLETED\|SUCCESS"; then
                    echo -e "${GREEN}  $line${NC}"
                else
                    echo "  $line"
                fi
            done
        fi
    done
}

show_component_logs() {
    local component="$1"
    local today_only="$2"
    local count=${3:-100}
    
    echo -e "${BLUE}📊 $(echo $component | tr '[:lower:]' '[:upper:]') LOGS${NC}"
    echo "========================"
    
    local log_files=$(get_log_files "$component" "$today_only")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No $component logs found${NC}"
        return
    fi
    
    echo "$log_files" | while read -r logfile; do
        if [ -f "$logfile" ]; then
            echo -e "\n${PURPLE}📄 $(basename "$logfile")${NC}"
            tail -n "$count" "$logfile"
        fi
    done
}

show_summary() {
    echo -e "${BLUE}📈 LOG FILES SUMMARY${NC}"
    echo "===================="
    
    if [ ! -d "$LOGS_DIR" ]; then
        echo -e "${YELLOW}No logs directory found${NC}"
        return
    fi
    
    echo -e "${PURPLE}Directory: $LOGS_DIR${NC}"
    echo ""
    
    # Show file sizes and modification times
    ls -lah "$LOGS_DIR"/*.log 2>/dev/null | while read -r line; do
        echo "  $line"
    done || echo -e "${YELLOW}No log files found${NC}"
    
    echo ""
    echo -e "${BLUE}Quick Stats:${NC}"
    
    # Count errors across all logs
    local error_count=$(find "$LOGS_DIR" -name "*.log" -exec grep -c "ERROR\|❌\|FAILED" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    local warning_count=$(find "$LOGS_DIR" -name "*.log" -exec grep -c "WARNING\|⚠️" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    local success_count=$(find "$LOGS_DIR" -name "*.log" -exec grep -c "✅\|COMPLETED\|SUCCESS" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
    
    echo -e "  ${RED}Errors: ${error_count:-0}${NC}"
    echo -e "  ${YELLOW}Warnings: ${warning_count:-0}${NC}"
    echo -e "  ${GREEN}Successes: ${success_count:-0}${NC}"
}

tail_logs() {
    local component="$1"
    
    local log_files=$(get_log_files "$component" "false")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No $component logs found${NC}"
        return
    fi
    
    # Get the most recent log file
    local latest_log=$(echo "$log_files" | xargs ls -t 2>/dev/null | head -1)
    
    if [ -f "$latest_log" ]; then
        echo -e "${BLUE}📡 Following log: $(basename "$latest_log")${NC}"
        echo "Press Ctrl+C to stop"
        echo ""
        tail -f "$latest_log"
    else
        echo -e "${RED}No log file found to follow${NC}"
    fi
}

search_logs() {
    local pattern="$1"
    local today_only="$2"
    
    echo -e "${BLUE}🔍 SEARCHING FOR: '$pattern'${NC}"
    echo "=========================="
    
    local log_files=$(get_log_files "" "$today_only")
    if [ -z "$log_files" ]; then
        echo -e "${YELLOW}No log files found${NC}"
        return
    fi
    
    echo "$log_files" | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local matches=$(grep -n "$pattern" "$logfile" 2>/dev/null || true)
            if [ ! -z "$matches" ]; then
                echo -e "\n${PURPLE}📄 $(basename "$logfile")${NC}"
                echo "$matches" | while read -r line; do
                    echo -e "${GREEN}  $line${NC}"
                done
            fi
        fi
    done
}

# Main command processing
case "$1" in
    errors)
        check_logs_exist
        show_errors "$([[ "$2" == "--today" ]] && echo "true" || echo "false")"
        ;;
    warnings)
        check_logs_exist
        show_warnings "$([[ "$2" == "--today" ]] && echo "true" || echo "false")"
        ;;
    recent)
        check_logs_exist
        count=50
        today_only="false"
        shift
        while [[ $# -gt 0 ]]; do
            case $1 in
                --count)
                    count="$2"
                    shift 2
                    ;;
                --today)
                    today_only="true"
                    shift
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        show_recent "$count" "$today_only"
        ;;
    generation|incremental|loading)
        check_logs_exist
        show_component_logs "$1" "$([[ "$2" == "--today" ]] && echo "true" || echo "false")" "${3:-100}"
        ;;
    summary)
        show_summary
        ;;
    tail)
        check_logs_exist
        tail_logs "${2:-}"
        ;;
    search)
        check_logs_exist
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide a search pattern${NC}"
            print_usage
            exit 1
        fi
        search_logs "$2" "$([[ "$3" == "--today" ]] && echo "true" || echo "false")"
        ;;
    ""|help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac