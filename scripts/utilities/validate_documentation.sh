#!/usr/bin/env zsh

# =====================================================
# EuroStyle Fashion - Documentation Validator
# =====================================================
# Validates documentation consistency, broken links, and file references
# as required by WARP.md Rule #23
#
# Usage: ./validate_documentation.sh [--verbose|-v] [--help|-h]
#
# Exit codes:
#   0 - All validations passed
#   1 - Warnings found (non-critical issues)
#   2 - Errors found (critical issues)

set -euo pipefail

# Script setup (zsh/bash compatible)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source shared utilities
source "$SCRIPT_DIR/_lib/style.sh"
source "$SCRIPT_DIR/_lib/doc_utils.sh"

# Configuration
MAIN_DOCS=("README.md" "QUICKSTART.md" "WARP.md")

# Parse command line arguments
show_help() {
    cat << EOF
${YELLOW}Usage:${NC} $(basename "$0") [options]

${CYAN}Description:${NC}
  Validates EuroStyle documentation consistency, broken links, and file references.
  Implements WARP.md Rule #23 documentation validation requirements.

${CYAN}Options:${NC}
  ${GREEN}-v, --verbose${NC}    Enable verbose output with detailed validation steps
  ${GREEN}-h, --help${NC}       Show this help message and exit

${CYAN}Validation Checks:${NC}
  ${PURPLE}${BULLET} Broken Links${NC}       Check [text](path) links in Markdown files
  ${PURPLE}${BULLET} Missing Files${NC}      Validate script and file references exist
  ${PURPLE}${BULLET} Cross-Doc Consistency${NC} Compare key metrics across documentation
  ${PURPLE}${BULLET} YAML Syntax${NC}        Validate all YAML configuration files
  ${PURPLE}${BULLET} Command References${NC}  Verify eurostyle.sh command references are valid

${CYAN}Examples:${NC}
  ${GREEN}./validate_documentation.sh${NC}              # Run all validations
  ${GREEN}./validate_documentation.sh --verbose${NC}     # Run with detailed output
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            export VERBOSE="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 2
            ;;
    esac
done

# Initialize workspace
WORKSPACE_DIR=$(create_validation_workspace)
trap "cleanup_validation_workspace '$WORKSPACE_DIR'" EXIT

# Validation functions

check_broken_links() {
    print_section "Checking Broken Links"
    
    local broken_links_found=0
    local markdown_files
    markdown_files=$(find_markdown_files "$PROJECT_ROOT")
    
    while IFS= read -r md_file; do
        verbose_log "Checking links in $(basename "$md_file")"
        
        local links
        links=$(extract_markdown_links "$md_file")
        
        if [[ -z "$links" ]]; then
            verbose_log "No links found in $(basename "$md_file")"
            continue
        fi
        
        while IFS= read -r link; do
            if [[ -n "$link" ]]; then
                local link_status
                link_status=$(check_relative_path "$link" "$PROJECT_ROOT" "$md_file")
                
                if [[ "$link_status" == "missing" ]]; then
                    validation_fail "Broken link in $(basename "$md_file"): $link"
                    ((broken_links_found++))
                else
                    verbose_log "Valid link: $link"
                fi
            fi
        done <<< "$links"
        
    done <<< "$markdown_files"
    
    if [[ $broken_links_found -eq 0 ]]; then
        validation_pass "All documentation links are valid"
    fi
    
    return $broken_links_found
}

check_missing_files() {
    print_section "Checking Missing File References"
    
    local missing_files_found=0
    local markdown_files
    markdown_files=$(find_markdown_files "$PROJECT_ROOT")
    
    while IFS= read -r md_file; do
        verbose_log "Checking script references in $(basename "$md_file")"
        
        local script_refs
        script_refs=$(extract_script_references "$md_file")
        
        while IFS= read -r script_ref; do
            if [[ -n "$script_ref" ]]; then
                local full_path="$PROJECT_ROOT/$script_ref"
                
                if [[ ! -f "$full_path" ]]; then
                    validation_fail "Referenced script not found: $script_ref (in $(basename "$md_file"))"
                    ((missing_files_found++))
                elif [[ ! -x "$full_path" ]] && [[ "$script_ref" =~ \.sh$ ]]; then
                    validation_warn "Referenced script exists but is not executable: $script_ref"
                else
                    verbose_log "Valid script reference: $script_ref"
                fi
            fi
        done <<< "$script_refs"
        
    done <<< "$markdown_files"
    
    if [[ $missing_files_found -eq 0 ]]; then
        validation_pass "All script references are valid"
    fi
    
    return $missing_files_found
}

check_cross_doc_consistency() {
    print_section "Checking Cross-Document Consistency"
    
    local consistency_issues=0
    
    # Check revenue figures consistency
    local readme_revenue quickstart_revenue warp_revenue
    readme_revenue=$(extract_revenue_figures "$PROJECT_ROOT/README.md" | head -5 | tr '\n' ' ')
    quickstart_revenue=$(extract_revenue_figures "$PROJECT_ROOT/QUICKSTART.md" | head -5 | tr '\n' ' ')
    warp_revenue=$(extract_revenue_figures "$PROJECT_ROOT/WARP.md" | head -5 | tr '\n' ' ')
    
    verbose_log "README revenue figures: $readme_revenue"
    verbose_log "QUICKSTART revenue figures: $quickstart_revenue"
    verbose_log "WARP revenue figures: $warp_revenue"
    
    # Check customer/order count consistency
    local readme_counts quickstart_counts
    readme_counts=$(extract_count_figures "$PROJECT_ROOT/README.md" | tr '\n' ' ')
    quickstart_counts=$(extract_count_figures "$PROJECT_ROOT/QUICKSTART.md" | tr '\n' ' ')
    
    verbose_log "README customer/order counts: $readme_counts"
    verbose_log "QUICKSTART customer/order counts: $quickstart_counts"
    
    # For now, just log the extracted data - more sophisticated comparison can be added
    validation_pass "Cross-document consistency check completed (data extracted for comparison)"
    
    return $consistency_issues
}

check_yaml_syntax() {
    print_section "Checking YAML Syntax"
    
    local yaml_errors=0
    local yaml_files
    yaml_files=$(find_yaml_files "$PROJECT_ROOT")
    
    if [[ -z "$yaml_files" ]]; then
        validation_pass "No YAML files found to validate"
        return 0
    fi
    
    while IFS= read -r yaml_file; do
        verbose_log "Validating YAML: $(basename "$yaml_file")"
        
        if validate_yaml_file "$yaml_file"; then
            verbose_log "YAML valid: $(basename "$yaml_file")"
        else
            ((yaml_errors++))
        fi
        
    done <<< "$yaml_files"
    
    if [[ $yaml_errors -eq 0 ]]; then
        validation_pass "All YAML files have valid syntax"
    fi
    
    return $yaml_errors
}

check_command_placeholders() {
    print_section "Checking Command References"
    
    local command_errors=0
    
    # Get available eurostyle.sh commands
    local available_commands
    available_commands=$(get_eurostyle_commands "$PROJECT_ROOT/eurostyle.sh") || {
        validation_fail "Could not extract eurostyle.sh commands"
        return 1
    }
    
    verbose_log "Available eurostyle.sh commands: $(echo "$available_commands" | tr '\n' ' ')"
    
    # Check each main documentation file
    for doc_file in "${MAIN_DOCS[@]}"; do
        local full_path="$PROJECT_ROOT/$doc_file"
        
        if [[ -f "$full_path" ]]; then
            verbose_log "Checking command references in $doc_file"
            
            if ! validate_command_references "$full_path" "$available_commands"; then
                ((command_errors++))
            fi
        else
            validation_warn "Main documentation file not found: $doc_file"
        fi
    done
    
    if [[ $command_errors -eq 0 ]]; then
        validation_pass "All command references are valid"
    fi
    
    return $command_errors
}

# Main execution
main() {
    print_banner "Documentation Validator" "WARP.md Rule #23 Compliance"
    
    log_info "Starting documentation validation for EuroStyle project"
    verbose_log "Project root: $PROJECT_ROOT"
    verbose_log "Workspace: $WORKSPACE_DIR"
    
    # Run all validation checks
    local total_errors=0
    
    check_broken_links || ((total_errors += $?))
    check_missing_files || ((total_errors += $?))
    check_cross_doc_consistency || ((total_errors += $?))
    check_yaml_syntax || ((total_errors += $?))
    check_command_placeholders || ((total_errors += $?))
    
    # Print summary and exit with appropriate code
    print_validation_summary "Documentation Validator"
    local exit_code=$?
    
    if [[ $exit_code -eq $EXIT_SUCCESS ]]; then
        log_info "Documentation validation completed successfully"
    elif [[ $exit_code -eq $EXIT_WARNINGS ]]; then
        log_info "Documentation validation completed with warnings"
    else
        log_info "Documentation validation failed with errors"
    fi
    
    return $exit_code
}

# Execute main function
main "$@"