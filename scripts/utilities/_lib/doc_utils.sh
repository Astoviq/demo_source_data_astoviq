#!/usr/bin/env zsh

# =====================================================
# EuroStyle Fashion - Documentation Utilities
# =====================================================
# Helper functions for documentation validation scripts
# Compatible with zsh and bash
#
# Usage: source "$(dirname "$0")/_lib/doc_utils.sh"

# Project root detection
get_project_root() {
    local current_dir="$(pwd)"
    
    # Look for eurostyle.sh as project marker
    while [[ "$current_dir" != "/" ]]; do
        if [[ -f "$current_dir/eurostyle.sh" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done
    
    # Fallback to current directory if not found
    echo "$(pwd)"
}

# File discovery functions
find_markdown_files() {
    local project_root="${1:-$(get_project_root)}"
    
    find "$project_root" -name "*.md" -type f | \
    grep -v "/archive/" | \
    grep -v "/node_modules/" | \
    grep -v "/.git/" | \
    sort
}

find_executable_scripts() {
    local project_root="${1:-$(get_project_root)}"
    
    # Find shell scripts and Python scripts
    {
        find "$project_root" -name "*.sh" -type f
        find "$project_root" -name "*.py" -type f
        find "$project_root" -name "eurostyle.sh" -type f
    } | \
    grep -v "/archive/" | \
    grep -v "/node_modules/" | \
    grep -v "/.git/" | \
    sort | uniq
}

find_yaml_files() {
    local project_root="${1:-$(get_project_root)}"
    
    {
        find "$project_root" -name "*.yaml" -type f
        find "$project_root" -name "*.yml" -type f
    } | \
    grep -v "/archive/" | \
    grep -v "/node_modules/" | \
    grep -v "/.git/" | \
    sort | uniq
}

# Extract eurostyle.sh available commands
get_eurostyle_commands() {
    local eurostyle_script="${1:-$(get_project_root)/eurostyle.sh}"
    
    if [[ ! -f "$eurostyle_script" ]]; then
        echo "Error: eurostyle.sh not found" >&2
        return 1
    fi
    
    # Extract command names from the usage function by looking for colored command patterns
    grep -E "GREEN}[a-z-]+\$\{NC}" "$eurostyle_script" | \
    sed -E 's/.*GREEN\}([a-z-]+)\$\{NC\}.*/\1/' | \
    sort | uniq
}

# Parse markdown links [text](path)
extract_markdown_links() {
    local markdown_file="$1"
    
    if [[ ! -f "$markdown_file" ]]; then
        echo "Error: Markdown file not found: $markdown_file" >&2
        return 1
    fi
    
    # Extract [text](path) links using Python for reliable parsing
    python3 -c "
import re

with open('$markdown_file', 'r') as f:
    content = f.read()

# Find markdown links
pattern = r'\[([^\]]*)\]\(([^)]+)\)'
matches = re.findall(pattern, content)

for text, path in matches:
    # Skip external URLs
    if not (path.startswith('http://') or path.startswith('https://')):
        print(path)
" 2>/dev/null
}

# Check if a path exists relative to project root
check_relative_path() {
    local path="$1"
    local project_root="${2:-$(get_project_root)}"
    local base_file="$3"  # For relative path resolution
    
    # Handle relative paths
    if [[ "$path" =~ ^\.\.?/ ]]; then
        if [[ -n "$base_file" ]]; then
            local base_dir="$(dirname "$base_file")"
            path="$base_dir/$path"
        fi
    fi
    
    # Convert to absolute path
    if [[ ! "$path" =~ ^/ ]]; then
        path="$project_root/$path"
    fi
    
    # Check if file or directory exists
    if [[ -e "$path" ]]; then
        echo "exists"
        return 0
    else
        echo "missing"
        return 1
    fi
}

# Extract revenue figures from documentation for consistency checking
extract_revenue_figures() {
    local markdown_file="$1"
    
    if [[ ! -f "$markdown_file" ]]; then
        return 1
    fi
    
    # Extract revenue figures using grep and sed
    grep -oE '€[0-9,.]+(.[0-9]+)?' "$markdown_file" | \
    sed 's/,//g' | \
    sort | uniq
}

# Extract customer/order counts for consistency checking
extract_count_figures() {
    local markdown_file="$1"
    local pattern="${2:-customers|orders}"
    
    if [[ ! -f "$markdown_file" ]]; then
        return 1
    fi
    
    # Extract figures like "50K customers", "5,000 orders", etc.
    grep -iE '[0-9,.]+(K|k)?\s+(customers|orders)' "$markdown_file" | \
    sed -E 's/.*([0-9,.]+(K|k)?)\s+(customers|orders).*/\1 \3/i' | \
    sort | uniq
}

# Create temporary directory for validation work
create_validation_workspace() {
    local workspace_dir="$(get_project_root)/tmp/validation_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$workspace_dir"
    echo "$workspace_dir"
}

# Clean up validation workspace
cleanup_validation_workspace() {
    local workspace_dir="$1"
    
    if [[ -n "$workspace_dir" && "$workspace_dir" =~ /tmp/validation_ ]]; then
        rm -rf "$workspace_dir"
        verbose_log "Cleaned up workspace: $workspace_dir"
    fi
}

# Extract script references from documentation
extract_script_references() {
    local markdown_file="$1"
    
    if [[ ! -f "$markdown_file" ]]; then
        return 1
    fi
    
    # Extract script paths from common patterns
    python3 -c "
import re

with open('$markdown_file', 'r') as f:
    content = f.read()

patterns = [
    r'\\./([^\\s]+\\.sh)',           # ./scripts/something.sh
    r'python3\\s+([^\\s]+\\.py)',   # python3 scripts/something.py
    r'bash\\s+([^\\s]+\\.sh)',      # bash scripts/something.sh
]

script_refs = set()

for pattern in patterns:
    matches = re.findall(pattern, content)
    script_refs.update(matches)

for script in sorted(script_refs):
    print(script)
" 2>/dev/null
}

# Validate that documentation references match actual available commands
validate_command_references() {
    local markdown_file="$1"
    local available_commands="$2"
    
    if [[ ! -f "$markdown_file" ]]; then
        return 1
    fi
    
    # Extract eurostyle.sh command references
    local referenced_commands
    referenced_commands=$(grep -oE '\./eurostyle\.sh\s+([a-z-]+)' "$markdown_file" | \
                         sed 's|\./eurostyle\.sh\s*||' | sort | uniq)
    
    local invalid_commands=0
    
    while IFS= read -r cmd; do
        if [[ -n "$cmd" && ! "$available_commands" =~ $cmd ]]; then
            validation_fail "Invalid eurostyle.sh command '$cmd' referenced in $(basename "$markdown_file")"
            ((invalid_commands++))
        else
            verbose_log "Valid command reference: $cmd"
        fi
    done <<< "$referenced_commands"
    
    return $invalid_commands
}