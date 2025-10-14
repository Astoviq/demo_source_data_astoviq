#!/bin/bash

# EuroStyle Complete Demo Recreation Script
# =========================================
# 
# This script recreates the entire EuroStyle integrated demo environment.
# 
# Usage: ./recreate_demo.sh
# Time: ~15-20 minutes
# Data: ~500MB+

set -e  # Exit on any error

echo "🎬 EUROSTYLE COMPLETE DEMO RECREATION"
echo "===================================================="
echo "Starting complete recreation of integrated demo environment"
echo "Estimated time: 15-20 minutes"
echo "Estimated data volume: 500+ MB"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

START_TIME=$(date +%s)
STEP=1
TOTAL_STEPS=8

# Function to run a step with logging
run_step() {
    local step_name="$1"
    local command="$2"
    
    echo ""
    echo "📍 STEP $STEP/$TOTAL_STEPS: $step_name"
    echo "----------------------------------------------------"
    echo "🚀 Starting: $step_name"
    echo "   Command: $command"
    
    step_start=$(date +%s)
    
    if eval "$command"; then
        step_end=$(date +%s)
        step_duration=$((step_end - step_start))
        echo "✅ Completed: $step_name (${step_duration}s)"
    else
        echo "❌ Failed: $step_name"
        echo "Recreation stopped due to error."
        exit 1
    fi
    
    ((STEP++))
}

echo "🔍 Checking prerequisites..."
# Check if required files exist
required_files=(
    "../data-generator/generate_data.py"
    "build_data_registry.py"
    "generate_webshop_with_registry.py"
    "generate_finance_optimized.py"
    "generate_hr_data.py"
    "generate_hr_finance_integration.py"
    "generate_pos_system.py"
    "generate_pos_finance_integration.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        echo "Please ensure all generator scripts are present."
        exit 1
    fi
done

echo "✅ All prerequisite files found"
echo ""

# Execute recreation steps
run_step "Operational Data Generation" "cd ../data-generator && python3 generate_data.py"
run_step "Data Registry Build" "python3 build_data_registry.py"
run_step "Webshop Data Generation" "python3 generate_webshop_with_registry.py"
run_step "Finance Data Generation" "python3 generate_finance_optimized.py"
run_step "HR Data Generation" "python3 generate_hr_data.py"
run_step "HR-Finance Integration" "python3 generate_hr_finance_integration.py"
run_step "POS System Generation" "python3 generate_pos_system.py"
run_step "POS-Finance Integration" "python3 generate_pos_finance_integration.py"

# Calculate total time
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_DURATION / 60))
SECONDS=$((TOTAL_DURATION % 60))

echo ""
echo "🏁 RECREATION SUMMARY"
echo "===================================================="
echo "Total duration: ${TOTAL_DURATION}s (${MINUTES}m ${SECONDS}s)"
echo "All steps completed successfully!"

# Verify generated data
echo ""
echo "🔍 Verifying generated data..."
GENERATED_DATA="../generated_data"
OPERATIONAL_DATA="../data-generator/generated_data"

if [ -d "$GENERATED_DATA" ] && [ -d "$OPERATIONAL_DATA" ]; then
    file_count=$(find "$GENERATED_DATA" "$OPERATIONAL_DATA" -type f | wc -l)
    total_size=$(find "$GENERATED_DATA" "$OPERATIONAL_DATA" -type f -exec du -c {} + | tail -1 | cut -f1)
    size_mb=$((total_size / 1024))
    
    echo "📊 Generated data summary:"
    echo "   Total files: $file_count"
    echo "   Total size: ${size_mb} MB"
    
    # Check key files
    key_files=(
        "$OPERATIONAL_DATA/orders.csv:Operational Orders"
        "$OPERATIONAL_DATA/customers.csv:Operational Customers"
        "$GENERATED_DATA/eurostyle_webshop.sessions.csv.gz:Webshop Sessions"
        "$GENERATED_DATA/eurostyle_finance.gl_journal_headers.csv.gz:Finance GL Headers"
        "$GENERATED_DATA/eurostyle_hr.employees.csv.gz:HR Employees"
        "$GENERATED_DATA/eurostyle_pos.transactions.csv:POS Transactions"
    )
    
    echo ""
    echo "📋 Key file verification:"
    for key_file in "${key_files[@]}"; do
        file_path="${key_file%%:*}"
        file_desc="${key_file##*:}"
        
        if [ -f "$file_path" ]; then
            file_size=$(du -h "$file_path" | cut -f1)
            echo "   ✅ $file_desc: $file_size"
        else
            echo "   ❌ $file_desc: MISSING"
        fi
    done
fi

echo ""
echo "🎉 COMPLETE DEMO RECREATION SUCCESSFUL! 🎉"
echo ""
echo "The EuroStyle integrated demo environment has been successfully recreated with:"
echo "• Complete cross-system integration (HR ↔ Operations ↔ Finance ↔ Webshop ↔ POS)"
echo "• Realistic business relationships and data volumes"
echo "• Full audit trail and financial reconciliation" 
echo "• Production-scale analytics capability"
echo ""
echo "The demo is now ready for use!"