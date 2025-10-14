#!/usr/bin/env zsh

# =====================================================
# EuroStyle Fashion - Shared Style Utilities
# =====================================================
# Common styling, colors, and logging functions for all EuroStyle scripts
# Compatible with zsh and bash
#
# Usage: source "$(dirname "$0")/_lib/style.sh"

# Color codes (compatible with eurostyle.sh)
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export BOLD='\033[1m'
export NC='\033[0m' # No Color

# Common emoji and symbols
export CHECK="✅"
export CROSS="❌"
export WARNING="⚠️"
export INFO="ℹ️"
export ARROW="▶"
export BULLET="•"

# Exit codes (standardized across EuroStyle scripts)
export EXIT_SUCCESS=0
export EXIT_WARNINGS=1
export EXIT_ERRORS=2

# Logging functions with consistent formatting
log_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

log_step() {
    echo -e "${PURPLE}${ARROW} $1${NC}"
}

log_detail() {
    echo -e "${CYAN}  ${BULLET} $1${NC}"
}

# Print section headers (compatible with eurostyle.sh style)
print_section() {
    echo ""
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}$(printf '═%.0s' $(seq 1 ${#1}))${NC}"
}

# Print banner with consistent EuroStyle branding
print_banner() {
    local title="$1"
    local subtitle="$2"
    
    echo -e "${BLUE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                 🏪 EuroStyle Fashion                        ║"
    if [[ -n "$title" ]]; then
        printf "║%*s║\n" 60 "$(printf "%*s" $(( (60 - ${#title}) / 2 + ${#title} )) "$title")"
    fi
    if [[ -n "$subtitle" ]]; then
        printf "║%*s║\n" 60 "$(printf "%*s" $(( (60 - ${#subtitle}) / 2 + ${#subtitle} )) "$subtitle")"
    fi
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Progress tracking for validation scripts
declare -g VALIDATION_PASS_COUNT=0
declare -g VALIDATION_WARN_COUNT=0
declare -g VALIDATION_FAIL_COUNT=0

validation_pass() {
    ((VALIDATION_PASS_COUNT++))
    log_success "$1"
}

validation_warn() {
    ((VALIDATION_WARN_COUNT++))
    log_warning "$1"
}

validation_fail() {
    ((VALIDATION_FAIL_COUNT++))
    log_error "$1"
}

print_validation_summary() {
    local script_name="$1"
    
    echo ""
    print_section "Validation Summary for $script_name"
    
    echo -e "${GREEN}${CHECK} Passed: ${VALIDATION_PASS_COUNT}${NC}"
    echo -e "${YELLOW}${WARNING} Warnings: ${VALIDATION_WARN_COUNT}${NC}"
    echo -e "${RED}${CROSS} Failures: ${VALIDATION_FAIL_COUNT}${NC}"
    
    local total=$((VALIDATION_PASS_COUNT + VALIDATION_WARN_COUNT + VALIDATION_FAIL_COUNT))
    echo -e "${CYAN}Total checks: ${total}${NC}"
    
    if [[ $VALIDATION_FAIL_COUNT -gt 0 ]]; then
        echo -e "\n${RED}${BOLD}${CROSS} VALIDATION FAILED${NC}"
        return $EXIT_ERRORS
    elif [[ $VALIDATION_WARN_COUNT -gt 0 ]]; then
        echo -e "\n${YELLOW}${BOLD}${WARNING} VALIDATION COMPLETED WITH WARNINGS${NC}"
        return $EXIT_WARNINGS
    else
        echo -e "\n${GREEN}${BOLD}${CHECK} VALIDATION PASSED${NC}"
        return $EXIT_SUCCESS
    fi
}

# Verbose mode helper
is_verbose() {
    [[ "${VERBOSE:-}" == "true" ]]
}

verbose_log() {
    if is_verbose; then
        log_detail "$1"
    fi
}

# File existence checks with consistent error reporting
check_file_exists() {
    local file_path="$1"
    local description="${2:-file}"
    
    if [[ -f "$file_path" ]]; then
        verbose_log "$description exists: $file_path"
        return 0
    else
        validation_fail "$description not found: $file_path"
        return 1
    fi
}

check_executable_exists() {
    local file_path="$1"
    local description="${2:-executable}"
    
    if [[ -x "$file_path" ]]; then
        verbose_log "$description is executable: $file_path"
        return 0
    elif [[ -f "$file_path" ]]; then
        validation_warn "$description exists but is not executable: $file_path"
        return 1
    else
        validation_fail "$description not found: $file_path"
        return 2
    fi
}

# YAML validation helper
validate_yaml_file() {
    local yaml_file="$1"
    
    if ! check_file_exists "$yaml_file" "YAML file"; then
        return 1
    fi
    
    # Use Python to validate YAML syntax (following user's python3 rule)
    if python3 -c "
import yaml
import sys
try:
    with open('$yaml_file', 'r') as f:
        yaml.safe_load(f)
    print('Valid YAML')
except Exception as e:
    print(f'Invalid YAML: {e}')
    sys.exit(1)
" 2>/dev/null; then
        verbose_log "YAML syntax valid: $yaml_file"
        return 0
    else
        validation_fail "YAML syntax error in: $yaml_file"
        return 1
    fi
}

# Extract commands from markdown code blocks
extract_bash_commands() {
    local markdown_file="$1"
    
    # Extract bash code blocks using Python for reliable parsing
    python3 -c "
import re
import sys

with open('$markdown_file', 'r') as f:
    content = f.read()

# Find bash code blocks
pattern = r'\`\`\`bash\n(.*?)\n\`\`\`'
matches = re.findall(pattern, content, re.DOTALL)

for match in matches:
    # Split into individual commands and clean them
    commands = match.strip().split('\n')
    for cmd in commands:
        cmd = cmd.strip()
        # Skip comments, empty lines, and simple echo statements
        if cmd and not cmd.startswith('#') and not cmd.startswith('echo'):
            print(cmd)
" 2>/dev/null
}

# Initialize verbose mode from environment or parameters
if [[ "$*" =~ (--verbose|-v) ]] || [[ "${VERBOSE:-}" == "true" ]]; then
    export VERBOSE="true"
fi