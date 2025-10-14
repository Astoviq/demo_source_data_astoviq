#!/usr/bin/env bash

# =====================================================
# EuroStyle Fashion - FAST Complete Demo Data Generation (Modern Wrapper)
# =====================================================
# Modern wrapper calling Universal Data Generator V2
# Following WARP.md Rule #3: Use universal_data_generator_v2.py as single source
#
# This replaces the legacy script with the same functionality but using
# the Universal Data Generator V2 which ensures perfect cross-database consistency
#
# Usage: ./scripts/generate-fast-complete-data.sh [--force]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 EuroStyle Fashion - FAST Complete Demo Data Generation (V2)${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${CYAN}📊 Universal Data Generator V2 with GUARANTEED cross-database consistency:${NC}"
echo -e "${CYAN}   • Operations revenue = Finance GL revenue (exact match)${NC}"
echo -e "${CYAN}   • HR employee salaries = Finance payroll GL entries (exact match)${NC}"
echo -e "${CYAN}   • Webshop sessions correlate with actual operational orders${NC}"
echo -e "${CYAN}   • All foreign key relationships maintained automatically${NC}"
echo -e "${CYAN}   • POS transactions integrated with operational orders${NC}"
echo -e "${YELLOW}⚡ Expected total time: 2-5 minutes (optimized Universal Generator V2)${NC}"
echo ""

cd "$PROJECT_DIR"

echo -e "${PURPLE}🎯 Calling Universal Data Generator V2 with 'demo' mode (fast configuration)...${NC}"
echo ""

# Call Universal Data Generator V2 with demo mode (which is the fast configuration)
# This ensures all databases are generated with perfect consistency
if python3 scripts/data-generation/universal_data_generator_v2.py --all --mode demo "$@"; then
    echo ""
    echo -e "${GREEN}🎉 Universal Data Generator V2 completed successfully!${NC}"
    echo -e "${GREEN}✅ All 5 databases generated with perfect cross-database consistency${NC}"
    echo -e "${GREEN}🎯 Revenue matching: Operations = Finance = POS (guaranteed)${NC}"
    
    # Show success statistics
    echo ""
    echo -e "${CYAN}📊 Generated databases:${NC}"
    echo -e "${CYAN}   • eurostyle_operational: Customer orders, products, stores${NC}"
    echo -e "${CYAN}   • eurostyle_finance: GL entries with perfect revenue matching${NC}"
    echo -e "${CYAN}   • eurostyle_hr: Employee data with payroll GL integration${NC}"
    echo -e "${CYAN}   • eurostyle_webshop: Analytics sessions correlating with orders${NC}"
    echo -e "${CYAN}   • eurostyle_pos: Point of sales with European VAT compliance${NC}"
    echo ""
    
    # Automatically load generated data
    echo -e "${PURPLE}📥 Loading generated data into ClickHouse...${NC}"
    if ./scripts/data-loading/load_full_dataset.sh; then
        echo -e "${GREEN}🎉 Data loading completed successfully!${NC}"
        echo -e "${GREEN}✅ All 5 databases populated and validated${NC}"
    else
        echo -e "${RED}❌ Data loading failed${NC}"
        echo -e "${YELLOW}💡 Generated CSV files are available in data/csv/. Load manually with './scripts/data-loading/load_full_dataset.sh'${NC}"
        exit 1
    fi
else
    echo ""
    echo -e "${RED}❌ Universal Data Generator V2 failed${NC}"
    echo -e "${YELLOW}💡 Check logs and ClickHouse container status${NC}"
    exit 1
fi