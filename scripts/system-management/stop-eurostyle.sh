#!/bin/bash

# =====================================================
# EuroStyle Fashion - Container Stop Script
# =====================================================
# Stops the EuroStyle ClickHouse source system
# Usage: ./scripts/stop-eurostyle.sh [--remove-data]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🏪 EuroStyle Fashion - Source System Shutdown${NC}"
echo -e "${BLUE}==============================================${NC}"

# Change to project directory
cd "$PROJECT_DIR"

# Parse command line arguments
REMOVE_DATA=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --remove-data)
            REMOVE_DATA=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--remove-data]"
            echo ""
            echo "Options:"
            echo "  --remove-data      Remove all data volumes and generated data"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown parameter: $1${NC}"
            exit 1
            ;;
    esac
done

# Main shutdown process
main() {
    echo -e "${BLUE}📋 Stopping EuroStyle Fashion source system...${NC}"
    
    # Check if containers exist
    if ! docker ps -a --filter "name=eurostyle_clickhouse_retail" --format "table {{.Names}}" | grep -q "eurostyle_clickhouse_retail"; then
        echo -e "${YELLOW}⚠️ No EuroStyle containers found${NC}"
        exit 0
    fi
    
    # Stop containers
    echo -e "${YELLOW}🛑 Stopping Docker containers...${NC}"
    docker-compose down
    
    # Remove data if requested
    if [ "$REMOVE_DATA" = true ]; then
        echo -e "${RED}🗑️ Removing all data and volumes...${NC}"
        
        # Confirm data removal
        echo -e "${YELLOW}⚠️ This will permanently delete all EuroStyle data!${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove Docker volumes
            docker-compose down -v
            
            # Remove local data directories
            if [ -d "data" ]; then
                echo -e "${YELLOW}📁 Removing data directory...${NC}"
                rm -rf data
            fi
            
            if [ -d "logs" ]; then
                echo -e "${YELLOW}📁 Removing logs directory...${NC}"
                rm -rf logs
            fi
            
            if [ -d "generated_data" ]; then
                echo -e "${YELLOW}📁 Removing generated_data directory...${NC}"
                rm -rf generated_data
            fi
            
            echo -e "${GREEN}✅ All data removed${NC}"
        else
            echo -e "${BLUE}📊 Data preserved${NC}"
        fi
    fi
    
    # Success message
    echo ""
    echo -e "${GREEN}🎉 EuroStyle Fashion source system stopped successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    
    if [ "$REMOVE_DATA" = false ]; then
        echo -e "${YELLOW}📝 Note: Data volumes preserved. Use --remove-data to delete all data.${NC}"
        echo -e "${BLUE}💡 To restart: ./scripts/start-eurostyle.sh${NC}"
    else
        echo -e "${BLUE}💡 To restart with fresh data: ./scripts/start-eurostyle.sh --generate-data${NC}"
    fi
    echo ""
}

# Run main function
main "$@"