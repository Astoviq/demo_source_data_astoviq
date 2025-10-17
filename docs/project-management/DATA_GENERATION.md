# EuroStyle Fashion - Complete Data Generation Guide

This document describes the comprehensive data generation system for EuroStyle Fashion's multi-system architecture.

## Overview

The EuroStyle Fashion system consists of multiple integrated databases:

- **Operational Database** (`eurostyle_operational`) - Core ERP system
- **Webshop Analytics Database** (`eurostyle_webshop`) - Customer behavior tracking
- **Future Systems** - Finance, HR, and enhanced POS systems

## Master Generation Script

### Location
```bash
./scripts/generate-demo-data.sh
```

### Usage

```bash
# Generate all systems (default)
./scripts/generate-demo-data.sh

# Generate specific system only
./scripts/generate-demo-data.sh --system operational
./scripts/generate-demo-data.sh --system webshop

# Generate specific tables within a system
./scripts/generate-demo-data.sh --system operational --tables customers,products
./scripts/generate-demo-data.sh --system webshop --tables web_sessions,page_views

# Force regeneration (replace existing data)
./scripts/generate-demo-data.sh --force

# Skip database validation (for testing)
./scripts/generate-demo-data.sh --skip-validation

# Show help
./scripts/generate-demo-data.sh --help
```

### System Architecture

#### Operational Database (ERP System)
- **Records**: 620,000+ business entities
- **Tables**: 9 core business tables
- **Data Source**: `data-generator/` Python system

**Tables:**
- `european_geography` - 158 European cities/regions
- `fashion_calendar` - 497 seasonal events (2 years)
- `stores` - 94 physical locations
- `products` - 4,944 fashion items
- `customers` - 310,000 European customers
- `campaigns` - 600 marketing campaigns
- `orders` - 500,000+ orders (2 years)
- `order_lines` - 1.2M individual items
- `inventory` - Stock across all locations

#### Webshop Analytics Database
- **Records**: 1.7M+ behavioral events
- **Tables**: 10 analytics tables
- **Data Source**: `scripts/generate_complete_webshop_data.py`

**Tables:**
- `web_sessions` - 173,400 customer journeys
- `page_views` - 1,030,000+ page interactions
- `cart_activities` - 50,000 shopping cart events
- `search_queries` - 25,000 search interactions
- `product_reviews` - 15,000 customer reviews
- `wishlist_items` - 35,000 wishlist additions
- `web_analytics_events` - 100,000 behavioral events
- `email_marketing` - 75,000 campaign interactions
- `product_recommendations` - 200,000 AI suggestions
- `ab_test_results` - 30,000 optimization experiments

### Cross-System Integration

The system maintains referential integrity between databases:

- **Customer Integration**: Webshop sessions reference operational customers
- **Product Integration**: Webshop analytics reference operational products
- **Campaign Integration**: Webshop marketing references operational campaigns

### Generation Process

1. **Pre-flight Checks**
   - Container status verification
   - Database connectivity testing
   - Existing data analysis

2. **Operational Data Generation**
   - Python virtual environment setup
   - Dependency installation
   - ERP data generation (5-15 minutes)

3. **Webshop Data Generation**
   - CSV file generation with referential integrity
   - Data loading into ClickHouse
   - Cross-system validation

4. **Post-generation Tasks**
   - Database summary reporting
   - Documentation updates
   - System integration verification

### Performance Metrics

**Operational System Generation:**
- **Duration**: 5-15 minutes
- **Data Volume**: ~620K records
- **Storage**: ~23 MiB

**Webshop System Generation:**
- **Duration**: 30-60 seconds
- **Data Volume**: ~1.7M records
- **Storage**: ~50 MiB

**Complete System Generation:**
- **Duration**: 5-16 minutes
- **Total Records**: ~2.3M records
- **Total Storage**: ~73 MiB

### Error Handling

The script includes comprehensive error handling:

- Container availability checks
- Database connectivity validation
- Data dependency verification
- Graceful failure recovery
- Detailed logging and progress reporting

### Advanced Features

#### Existing Data Management
```bash
# Check existing data without overwriting
./scripts/generate-demo-data.sh

# Force complete regeneration
./scripts/generate-demo-data.sh --force

# Add specific tables to existing data
./scripts/generate-demo-data.sh --tables new_table1,new_table2
```

#### System Isolation
```bash
# Test operational system independently
./scripts/generate-demo-data.sh --system operational

# Test webshop system independently
./scripts/generate-demo-data.sh --system webshop
```

#### Development Mode
```bash
# Skip validation for development
./scripts/generate-demo-data.sh --skip-validation --system webshop
```

## System Requirements

### Dependencies
- Docker (for ClickHouse container)
- Python 3.8+ (for data generation)
- Bash 4.0+ (for orchestration script)

### Container Requirements
- **Container Name**: `eurostyle_clickhouse_retail`
- **Status**: Running and healthy
- **Databases**: `eurostyle_operational`, `eurostyle_webshop`

### Resource Requirements
- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ free space
- **Network**: Internet access for Python dependencies

## Output and Access

### Database Access
```bash
# HTTP Interface
http://localhost:8124

# Native Port
localhost:9002

# Databases
- eurostyle_operational
- eurostyle_webshop
```

### Generated Documentation
```bash
# PDF Documentation
docs/source_systems/EuroStyle_ERP_Documentation.pdf
docs/source_systems/EuroStyle_Webshop_Documentation.pdf
```

### Data Files (CSV)
```bash
# Webshop CSV files (temporary)
eurostyle_webshop.web_sessions.csv
eurostyle_webshop.page_views.csv
eurostyle_webshop.cart_activities.csv
# ... (additional CSV files)
```

## Future Roadmap

### Planned Systems
1. **Finance System**
   - Multi-country BV structure
   - Holding company relationships
   - Financial consolidation data

2. **HR System**
   - SAP SuccessFactors-like structure
   - Sick leave tracking
   - Performance management data

3. **Enhanced POS System**
   - Staff transaction tracking
   - Individual sales attribution
   - Performance analytics

### Integration Plans
- Cross-system data warehouse
- Real-time ETL pipelines
- Advanced analytics dashboards
- Machine learning feature stores

## Troubleshooting

### Common Issues

**Container Not Running**
```bash
# Start the EuroStyle container
./scripts/start-eurostyle.sh
```

**Database Connection Failed**
```bash
# Check container health
docker ps --filter name=eurostyle_clickhouse_retail
docker logs eurostyle_clickhouse_retail
```

**Generation Failure**
```bash
# Check logs for specific errors
./scripts/generate-demo-data.sh --system operational 2>&1 | tee generation.log
```

**Data Loading Issues**
```bash
# Check CSV file format
head -5 eurostyle_webshop.*.csv

# Manual data loading
./eurostyle.sh demo-fast  # Load all systems including webshop
```

### Performance Tuning

**Large Dataset Generation**
```bash
# Generate in stages
./scripts/generate-demo-data.sh --system operational
./scripts/generate-demo-data.sh --system webshop

# Use specific tables for testing
./scripts/generate-demo-data.sh --tables customers --system operational
```

**Resource Optimization**
```bash
# Monitor resource usage
docker stats eurostyle_clickhouse_retail

# Adjust container resources if needed
docker update --memory=8g --cpus=4 eurostyle_clickhouse_retail
```

## Development Guide

### Adding New Tables

1. **Operational Tables**
   - Add generation logic to `data-generator/`
   - Update table lists in master script
   - Test with `--tables new_table_name`

2. **Webshop Tables**
   - Add generation logic to `scripts/data-generation/universal_data_generator_v2.py`
   - Tables are loaded automatically via `./eurostyle.sh demo-fast` or `demo-full`
   - Test with `./eurostyle.sh demo-fast`

### Script Customization

The master script is designed for extensibility:
- **Configuration Variables** at the top
- **Modular Functions** for each system
- **Error Handling** at each stage
- **Progress Reporting** throughout

### Testing Framework

```bash
# Test individual components
./scripts/generate-demo-data.sh --system operational --tables customers
./scripts/generate-demo-data.sh --system webshop --skip-validation

# Full system integration test
./scripts/generate-demo-data.sh --force

# Validation test
./scripts/generate-demo-data.sh --skip-validation --system all
```

## Conclusion

The EuroStyle Fashion data generation system provides a comprehensive, scalable, and maintainable approach to creating realistic demo data across multiple integrated business systems. The master script orchestrates complex data generation workflows while maintaining data integrity and system performance.

For support or questions, refer to the project documentation or contact the development team.