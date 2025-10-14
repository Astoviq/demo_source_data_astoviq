#!/bin/bash

# =====================================================
# EuroStyle Fashion - Container Startup Script
# =====================================================
# Starts the EuroStyle ClickHouse source system
# Usage: ./scripts/start-eurostyle.sh [--generate-data]

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

echo -e "${BLUE}🏪 EuroStyle Fashion - Source System Startup${NC}"
echo -e "${BLUE}============================================${NC}"

# Change to project directory
cd "$PROJECT_DIR"

# Parse command line arguments
GENERATE_DATA=false
GENERATE_INTEGRATED_DEMO=false
FORCE_RECREATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --generate-data)
            GENERATE_DATA=true
            shift
            ;;
        --generate-integrated-demo)
            GENERATE_INTEGRATED_DEMO=true
            shift
            ;;
        --recreate)
            FORCE_RECREATE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--generate-data] [--generate-integrated-demo] [--recreate]"
            echo ""
            echo "Options:"
            echo "  --generate-data              Generate basic demo data after starting containers"
            echo "  --generate-integrated-demo   Generate complete integrated demo (HR+Finance+POS+Webshop)"
            echo "  --recreate                   Force recreate containers (removes existing data)"
            echo "  -h, --help                   Show this help message"
            echo ""
            echo "Integrated Demo Features:"
            echo "  • Complete cross-system integration (HR ↔ Operations ↔ Finance ↔ Webshop ↔ POS)"
            echo "  • Realistic business relationships and data volumes (~500MB+)"
            echo "  • Full audit trail and financial reconciliation"
            echo "  • Production-scale analytics capability"
            echo "  • Estimated time: 15-20 minutes"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown parameter: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
}

# Function to check if container is healthy
wait_for_health() {
    local container_name=$1
    local max_wait=60
    local wait_time=0
    
    echo -e "${YELLOW}⏳ Waiting for $container_name to be healthy...${NC}"
    
    while [ $wait_time -lt $max_wait ]; do
        if docker ps --filter "name=$container_name" --filter "health=healthy" --format "table {{.Names}}" | grep -q "$container_name"; then
            echo -e "${GREEN}✅ $container_name is healthy${NC}"
            return 0
        fi
        
        sleep 2
        wait_time=$((wait_time + 2))
        echo -n "."
    done
    
    echo -e "\n${RED}❌ $container_name failed to become healthy within ${max_wait}s${NC}"
    return 1
}

# Function to test database connection
test_connection() {
    echo -e "${YELLOW}🔗 Testing database connection...${NC}"
    
    # Wait a bit more for the database to be fully ready
    sleep 5
    
    if docker exec eurostyle_clickhouse_retail clickhouse-client --host=localhost --port=9000 --query="SELECT 1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
        
        # Check if eurostyle_operational database exists
        if docker exec eurostyle_clickhouse_retail clickhouse-client --host=localhost --port=9000 --query="SHOW DATABASES" | grep -q "eurostyle_operational"; then
            echo -e "${GREEN}✅ EuroStyle operational database found${NC}"
        else
            echo -e "${YELLOW}⚠️ EuroStyle operational database not found (will be created during initialization)${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Database connection failed${NC}"
        return 1
    fi
}

# Function to generate integrated demo data
generate_integrated_demo() {
    echo -e "${BLUE}🌭 Generating Complete Integrated Demo Environment${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo -e "${YELLOW}This will create a comprehensive integrated demo with:${NC}"
    echo -e "${YELLOW}  • HR system with 447 employees and payroll integration${NC}"
    echo -e "${YELLOW}  • Operations system with customers, orders, and products${NC}"
    echo -e "${YELLOW}  • Finance system with GL journals and reconciliation${NC}"
    echo -e "${YELLOW}  • Webshop system with realistic analytics data${NC}"
    echo -e "${YELLOW}  • POS system linking employees to sales transactions${NC}"
    echo -e "${YELLOW}  • Cross-system integrations and audit trails${NC}"
    echo ""
    echo -e "${YELLOW}Estimated time: 15-20 minutes${NC}"
    echo -e "${YELLOW}Data volume: ~500MB+${NC}"
    echo ""
    
    # Check if integrated demo scripts exist
    required_scripts=(
        "build_data_registry.py"
        "generate_webshop_with_registry.py"
        "generate_finance_optimized.py"
        "generate_hr_data.py"
        "generate_hr_finance_integration.py"
        "generate_pos_system.py"
        "generate_pos_finance_integration.py"
    )
    
    missing_scripts=()
    for script in "${required_scripts[@]}"; do
        if [ ! -f "scripts/$script" ]; then
            missing_scripts+=("$script")
        fi
    done
    
    if [ ${#missing_scripts[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required integration scripts:${NC}"
        for script in "${missing_scripts[@]}"; do
            echo -e "${RED}  • $script${NC}"
        done
        echo -e "${YELLOW}Please ensure all integration scripts are present.${NC}"
        return 1
    fi
    
    # Execute the integrated demo generation
    local start_time=$(date +%s)
    local current_step=1
    local total_steps=8
    
    # Step 1: Operational Data Generation
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: Operational Data Generation${NC}"
    if ! (cd data-generator && python3 generate_data.py); then
        echo -e "${RED}❌ Failed to generate operational data${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Operational data generated successfully${NC}"
    ((current_step++))
    
    # Step 2: Data Registry Build
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: Data Registry Build${NC}"
    if ! (cd scripts && python3 build_data_registry.py); then
        echo -e "${RED}❌ Failed to build data registry${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Data registry built successfully${NC}"
    ((current_step++))
    
    # Step 3: Webshop Data Generation
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: Webshop Data Generation${NC}"
    if ! (cd scripts && python3 generate_webshop_with_registry.py); then
        echo -e "${RED}❌ Failed to generate webshop data${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Webshop data generated successfully${NC}"
    ((current_step++))
    
    # Step 4: Finance Data Generation
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: Finance Data Generation${NC}"
    if ! (cd scripts && python3 generate_finance_optimized.py); then
        echo -e "${RED}❌ Failed to generate finance data${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Finance data generated successfully${NC}"
    ((current_step++))
    
    # Step 5: HR Data Generation
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: HR Data Generation${NC}"
    if ! (cd scripts && python3 generate_hr_data.py); then
        echo -e "${RED}❌ Failed to generate HR data${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ HR data generated successfully${NC}"
    ((current_step++))
    
    # Step 6: HR-Finance Integration
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: HR-Finance Integration${NC}"
    if ! (cd scripts && python3 generate_hr_finance_integration.py); then
        echo -e "${RED}❌ Failed to generate HR-Finance integration${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ HR-Finance integration completed successfully${NC}"
    ((current_step++))
    
    # Step 7: POS System Generation
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: POS System Generation${NC}"
    if ! (cd scripts && python3 generate_pos_system.py); then
        echo -e "${RED}❌ Failed to generate POS system${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ POS system generated successfully${NC}"
    ((current_step++))
    
    # Step 8: POS-Finance Integration
    echo -e "${BLUE}📍 STEP $current_step/$total_steps: POS-Finance Integration${NC}"
    if ! (cd scripts && python3 generate_pos_finance_integration.py); then
        echo -e "${RED}❌ Failed to generate POS-Finance integration${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ POS-Finance integration completed successfully${NC}"
    
    # Calculate total time
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))
    
    # Verify generated data
    echo -e "${BLUE}🔍 Verifying generated data...${NC}"
    local total_files=0
    local total_size=0
    
    if [ -d "generated_data" ] && [ -d "data-generator/generated_data" ]; then
        total_files=$(find generated_data data-generator/generated_data -type f 2>/dev/null | wc -l | tr -d ' ')
        total_size=$(find generated_data data-generator/generated_data -type f -exec du -c {} + 2>/dev/null | tail -1 | cut -f1)
        size_mb=$((total_size / 1024))
        
        echo -e "${GREEN}📈 Generated data summary:${NC}"
        echo -e "${GREEN}  • Total files: $total_files${NC}"
        echo -e "${GREEN}  • Total size: ${size_mb} MB${NC}"
        echo -e "${GREEN}  • Generation time: ${minutes}m ${seconds}s${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 COMPLETE INTEGRATED DEMO GENERATION SUCCESSFUL! 🎉${NC}"
    echo -e "${GREEN}==========================================================${NC}"
    echo ""
    echo -e "${BLUE}Your EuroStyle integrated demo now includes:${NC}"
    echo -e "${GREEN}  ✅ Complete cross-system integration (HR ↔ Operations ↔ Finance ↔ Webshop ↔ POS)${NC}"
    echo -e "${GREEN}  ✅ Realistic business relationships and data volumes${NC}"
    echo -e "${GREEN}  ✅ Full audit trail and financial reconciliation${NC}"
    echo -e "${GREEN}  ✅ Production-scale analytics capability${NC}"
    echo ""
    
    return 0
}

# Main startup process
main() {
    echo -e "${BLUE}📋 Starting EuroStyle Fashion source system...${NC}"
    
    # Check Docker
    check_docker
    
    # Handle existing containers
    if docker ps -a --filter "name=eurostyle_clickhouse_retail" --format "table {{.Names}}" | grep -q "eurostyle_clickhouse_retail"; then
        if [ "$FORCE_RECREATE" = true ]; then
            echo -e "${YELLOW}🔄 Stopping and removing existing containers...${NC}"
            docker-compose down -v
        else
            echo -e "${YELLOW}⚠️ EuroStyle container already exists. Use --recreate to force recreation.${NC}"
            
            # Check if it's running
            if docker ps --filter "name=eurostyle_clickhouse_retail" --format "table {{.Names}}" | grep -q "eurostyle_clickhouse_retail"; then
                echo -e "${GREEN}✅ Container is already running${NC}"
                test_connection
                
                if [ "$GENERATE_DATA" = true ]; then
                    echo -e "${BLUE}🎲 Generating demo data...${NC}"
                    ./scripts/generate-demo-data.sh
                elif [ "$GENERATE_INTEGRATED_DEMO" = true ]; then
                    generate_integrated_demo
                fi
                
                echo -e "${GREEN}🚀 EuroStyle Fashion source system is ready!${NC}"
                echo -e "${BLUE}📊 Access ClickHouse at: http://localhost:8124${NC}"
                echo -e "${BLUE}🔌 Native connection: localhost:9002${NC}"
                return 0
            fi
        fi
    fi
    
    # Create necessary directories
    echo -e "${YELLOW}📁 Creating required directories...${NC}"
    mkdir -p data logs generated_data
    
    # Start containers
    echo -e "${BLUE}🐳 Starting Docker containers...${NC}"
    if [ "$FORCE_RECREATE" = true ]; then
        docker-compose up -d --force-recreate
    else
        docker-compose up -d
    fi
    
    # Wait for container to be healthy
    if ! wait_for_health "eurostyle_clickhouse_retail"; then
        echo -e "${RED}❌ Failed to start containers${NC}"
        echo -e "${YELLOW}📋 Container logs:${NC}"
        docker logs eurostyle_clickhouse_retail --tail 20
        exit 1
    fi
    
    # Test database connection
    if ! test_connection; then
        echo -e "${RED}❌ Database connection failed${NC}"
        echo -e "${YELLOW}📋 Container logs:${NC}"
        docker logs eurostyle_clickhouse_retail --tail 20
        exit 1
    fi
    
    # Generate demo data if requested
    if [ "$GENERATE_DATA" = true ]; then
        echo -e "${BLUE}🎲 Generating demo data...${NC}"
        ./scripts/generate-demo-data.sh
    elif [ "$GENERATE_INTEGRATED_DEMO" = true ]; then
        generate_integrated_demo
    fi
    
    # Success message
    echo ""
    echo -e "${GREEN}🎉 EuroStyle Fashion source system started successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}📊 ClickHouse HTTP Interface:${NC} http://localhost:8124"
    echo -e "${BLUE}🔌 ClickHouse Native Port:${NC}    localhost:9002"
    echo -e "${BLUE}💾 Database:${NC}                  eurostyle_operational"
    echo -e "${BLUE}👤 Username:${NC}                  eurostyle_user"
    echo -e "${BLUE}🔑 Password:${NC}                  eurostyle_demo_2024"
    echo ""
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo -e "${BLUE}   ./scripts/stop-eurostyle.sh${NC}                    # Stop the system"
    echo -e "${BLUE}   ./scripts/generate-demo-data.sh${NC}                # Generate basic demo data"
    echo -e "${BLUE}   ./scripts/start-eurostyle.sh --generate-integrated-demo${NC}  # Generate complete integrated demo"
    echo -e "${BLUE}   ./scripts/validate-data.sh${NC}                     # Validate data quality"
    echo -e "${BLUE}   docker logs eurostyle_clickhouse_retail${NC}         # View logs"
    echo ""
    
    if [ "$GENERATE_DATA" = false ] && [ "$GENERATE_INTEGRATED_DEMO" = false ]; then
        echo -e "${YELLOW}📝 Note: No demo data generated.${NC}"
        echo -e "${YELLOW}   • Use --generate-data for basic demo data${NC}"
        echo -e "${YELLOW}   • Use --generate-integrated-demo for complete integrated demo (recommended)${NC}"
    fi
}

# Run main function
main "$@"