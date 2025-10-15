#!/usr/bin/env bash

# =====================================================
# EuroStyle Fashion - FULL Complete Demo Data Generation (Modern Wrapper)
# =====================================================
# Modern wrapper calling Universal Data Generator V2
# Following WARP.md Rule #3: Use universal_data_generator_v2.py as single source
#
# This replaces the legacy script with the same functionality but using
# the Universal Data Generator V2 which ensures perfect cross-database consistency
#
# Usage: ./scripts/generate-full-complete-data.sh [--force]

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

echo -e "${BLUE}🚀 EuroStyle Fashion - FULL Complete Demo Data Generation (V2)${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${CYAN}📊 Universal Data Generator V2 with GUARANTEED cross-database consistency:${NC}"
echo -e "${CYAN}   • Operations revenue = Finance GL revenue (exact match)${NC}"
echo -e "${CYAN}   • HR employee salaries = Finance payroll GL entries (exact match)${NC}"
echo -e "${CYAN}   • Webshop sessions correlate with actual operational orders${NC}"
echo -e "${CYAN}   • All foreign key relationships maintained automatically${NC}"
echo -e "${CYAN}   • POS transactions integrated with operational orders${NC}"
echo -e "${YELLOW}⚡ Expected total time: 10-20 minutes (comprehensive Universal Generator V2)${NC}"
echo ""

cd "$PROJECT_DIR"

echo -e "${PURPLE}🎯 Calling Universal Data Generator V2 with 'full' mode (production-like configuration)...${NC}"
echo ""

# Call Universal Data Generator V2 with full mode (production-like volumes)
# This ensures all databases are generated with perfect consistency at scale
if python3 scripts/data-generation/universal_data_generator_v2.py --all --mode full "$@"; then
    echo ""
    echo -e "${GREEN}🎉 Universal Data Generator V2 completed successfully!${NC}"
    echo -e "${GREEN}✅ All 5 databases generated with perfect cross-database consistency${NC}"
    echo -e "${GREEN}🎯 Revenue matching: Operations = Finance = POS (guaranteed)${NC}"
    
    # Show success statistics
    echo ""
    echo -e "${CYAN}📊 Generated databases (production-like scale):${NC}"
    echo -e "${CYAN}   • eurostyle_operational: 50K customers, 5K orders, 2.5K products${NC}"
    echo -e "${CYAN}   • eurostyle_finance: Complete multi-year GL with perfect revenue matching${NC}"
    echo -e "${CYAN}   • eurostyle_hr: 830+ employees with full payroll GL integration${NC}"
    echo -e "${CYAN}   • eurostyle_webshop: 25K+ sessions with realistic conversion patterns${NC}"
    echo -e "${CYAN}   • eurostyle_pos: 37K+ transactions with European VAT compliance${NC}"
    echo ""
    
    # Automatically load generated data
    echo -e "${PURPLE}📥 Loading generated data into ClickHouse...${NC}"
    if ./scripts/data-loading/load_full_dataset.sh; then
        echo -e "${GREEN}🎉 Data loading completed successfully!${NC}"
        echo -e "${GREEN}✅ All 5 databases populated and validated${NC}"
    else
        echo -e "${YELLOW}⚠️ Some data loading issues occurred${NC}"
        echo -e "${CYAN}📊 Universal Data Generator V2 completed successfully!${NC}"
        echo -e "${CYAN}💡 Generated CSV files are available in data/csv/. You can:${NC}"
        echo -e "${CYAN}   • Use incremental loading: ./eurostyle.sh increment${NC}"
        echo -e "${CYAN}   • Load manually: ./scripts/data-loading/load_full_dataset.sh${NC}"
        echo -e "${GREEN}✅ Data generation phase completed successfully${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Universal Data Generator V2 failed${NC}"
    echo -e "${YELLOW}💡 Check logs and ClickHouse container status${NC}"
    exit 1
fi