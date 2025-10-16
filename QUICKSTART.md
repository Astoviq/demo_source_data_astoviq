# 🏪 EuroStyle Retail Demo - Quick Start Guide

## Unified Management System with Universal Data Generator

Run all commands from the project root: `/Users/kimvermeij/astoviq_projects/eurostyle-retail-demo`

```bash
# Make the script executable (one time only)
chmod +x eurostyle.sh

# Show all available commands
./eurostyle.sh

# 🎯 NEW: Universal Data Generator for perfect cross-database consistency
# Generate data with guaranteed Operations revenue = Finance GL revenue
```

## 🚀 Common Workflows

### 1. **Start Fresh Development Environment with Perfect Consistency**
```bash
./eurostyle.sh start          # Start containers
./eurostyle.sh setup          # Create database structure  
./eurostyle.sh demo-fast      # Generate fast demo data with Universal Data Generator (~1-2 min)
./eurostyle.sh status         # Verify everything is working + consistency check
```

### 2. **Production-like Demo Environment with Full Dataset**
```bash
./eurostyle.sh start          # Start containers
./eurostyle.sh demo-full      # Generate full demo data (50K customers, perfect GL matching)
./eurostyle.sh status         # Check final state + revenue consistency validation
```

### 3. **Direct Universal Data Generator Usage**
```bash
# Generate with perfect cross-database consistency
python3 scripts/data-generation/universal_data_generator_v2.py --all --mode full

# Validate perfect consistency
python3 scripts/data-generation/universal_data_generator_v2.py --validate-consistency

# Load generated data
./scripts/data-loading/load_full_dataset.sh
```

### 3. **Test Incremental Data Lake Processing**
```bash
# Generate baseline data first
./eurostyle.sh demo-fast

# NEW: Use Universal Incremental Generator for perfect consistency
# Add 1 business day of activity (100 orders, 20 customers, 500 sessions)
python3 scripts/data-generation/universal_incremental_generator.py --days 1

# Add 1 week of business activity with perfect GL matching
python3 scripts/data-generation/universal_incremental_generator.py --days 7 --intensity normal

# Simulate Black Friday (high-volume day)
python3 scripts/data-generation/universal_incremental_generator.py --days 1 --intensity heavy

# Specific data types only
python3 scripts/data-generation/universal_incremental_generator.py --types "orders,customers" --days 3
```

### 4. **System Maintenance**
```bash
./eurostyle.sh status         # Check system health
./eurostyle.sh logs           # View container logs
./eurostyle.sh clean          # Clean up generated data
./eurostyle.sh stop           # Stop containers
```

## 📊 Commands Reference

### Core Operations
- `start` - Start containers only
- `stop` - Stop containers only
- `setup` - Create empty database structure
- `status` - Show system status and data volumes

### Data Generation
- `demo-fast` - Fast demo data (~2K customers, ~1K orders) - **1-2 minutes**
- `demo-full` - Full demo data (~150K customers, ~50K orders) - **15-30 minutes**

### Incremental Data (Perfect for Data Lake Testing)
- `increment` - Add incremental data mutations

### Maintenance
- `clean` - Remove generated data and optionally truncate tables
- `logs` - Show container logs

## 🎯 Incremental Data Types

Use with `./eurostyle.sh increment --type "<types>" --days <N>`

### Business Data Types
- `orders` - New orders and order lines
- `customers` - New and updated customer records
- `sessions` - New web sessions and page views
- `carts` - Shopping cart activities  
- `searches` - Search queries and results
- `reviews` - Product reviews and ratings

### System Data Types  
- `calendar` - Fashion calendar updates (seasonal events)
- `employees` - New employees and leave requests
- `finance` - GL transactions and journal entries
- `all` - All data types combined

## 🔧 Advanced Options

### Force Operations
```bash
./eurostyle.sh start --force     # Force recreate containers
./eurostyle.sh clean --force     # Skip confirmation prompts
```

### Verbose Output
```bash
./eurostyle.sh demo-fast --verbose    # Detailed generation logs
```

### Custom Incremental Scenarios
```bash
# Simulate Black Friday (high order volume)
python3 scripts/data-generation/universal_incremental_generator.py --days 1 --intensity heavy

# Simulate new product launch (customer registration surge)  
python3 scripts/data-generation/universal_incremental_generator.py --types "customers,sessions" --days 3

# Simulate quarterly HR reorganization
python3 scripts/data-generation/universal_incremental_generator.py --types "departments" --days 1

# Simulate steady business growth (30 days)
for day in {1..30}; do
  python3 scripts/data-generation/universal_incremental_generator.py --days 1 --intensity normal
done
```

## 🌐 Connection Information

After starting the system:

- **HTTP Interface**: http://localhost:8124
- **Native ClickHouse**: localhost:9002  
- **Container**: `eurostyle_clickhouse_retail`

### Operations as Master Architecture with Multi-Database Structure
- `eurostyle_operational` - **Master System** (31,050+ records)
  - **All Sales Channels**: 2,250+ orders (335 online + 1,915 in-store)
  - **Channel Performance**: Online €515 avg vs In-store €204 avg
  - 1,000+ customers, 500+ products, 27,939+ inventory records
- `eurostyle_finance` - Financial GL (13,023 records: GL entries from ALL channels)
- `eurostyle_hr` - HR Management (11,628 records: 315+ employees)
- `eurostyle_webshop` - Digital Analytics (31,016 records: sessions, events, journey)
- `eurostyle_pos` - Store Analytics (7,351 records: payment details, staff, shifts)

**✅ Operations as Master**: All channels → Operations → GL (9% variance = EXCELLENT)

## 💡 Data Lake Testing Scenarios

### Scenario 1: Daily ETL Processing with Perfect Consistency
```bash
# Day 1: Initial load
./eurostyle.sh demo-fast

# Day 2: Add incremental business day (100 orders, 20 customers, 500 sessions)
python3 scripts/data-generation/universal_incremental_generator.py --days 1
# Load: cat data/csv/*_incremental.csv.gz | gunzip | docker exec -i eurostyle_clickhouse_retail clickhouse-client --query="INSERT INTO ... FORMAT CSVWithNames"

# Day 3: Add more business activity
python3 scripts/data-generation/universal_incremental_generator.py --days 1
```

### Scenario 2: Weekly Batch Processing with Business Patterns
```bash
# Initial state
./eurostyle.sh demo-fast

# Week 1: Full business week (700 orders, 140 customers, 3500 sessions)
python3 scripts/data-generation/universal_incremental_generator.py --days 7 --intensity normal

# Week 2: Specific data types (e.g., holiday season customer acquisition)
python3 scripts/data-generation/universal_incremental_generator.py --types "customers,sessions" --days 7
```

### Scenario 3: Mixed Workload with Seasonal Patterns
```bash
# Start with production-like data
./eurostyle.sh demo-full

# Normal business days (Monday-Thursday)
python3 scripts/data-generation/universal_incremental_generator.py --days 4 --intensity normal

# Black Friday (high-volume day)
python3 scripts/data-generation/universal_incremental_generator.py --days 1 --intensity heavy

# Post-holiday HR activities (employee changes)
python3 scripts/data-generation/universal_incremental_generator.py --types "departments" --days 1
```

## 🛟 Troubleshooting

### Container Issues
```bash
./eurostyle.sh status    # Check container health
./eurostyle.sh logs      # View detailed logs
./eurostyle.sh stop      # Stop if needed
./eurostyle.sh start     # Restart containers
```

### Data Issues
```bash
./eurostyle.sh clean --force    # Clean all data
./eurostyle.sh setup            # Recreate structure
./eurostyle.sh demo-fast        # Regenerate data
```

### Performance Issues
- Use `demo-fast` for development (much faster)
- Use `demo-full` only when you need production-scale volumes
- Incremental generation is always fast regardless of base data size

---

**🎉 You're ready to go!** This unified system gives you complete control over your EuroStyle Fashion demo environment with both fast development cycles and comprehensive data lake testing capabilities.