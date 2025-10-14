-- =====================================================
-- EuroStyle Fashion - Master Database Initialization
-- =====================================================
-- This is the master script that sets up the complete
-- EuroStyle Fashion retail analytics platform with:
--
-- 1. Operational Database (ERP) - Core business operations
-- 2. Webshop Database - E-commerce analytics  
-- 3. Finance Database - Financial management & reporting
-- 4. HR Database - Human resources & European compliance
-- 5. POS Database - Point of sale transactions
--
-- Author: EuroStyle Fashion Data Team
-- Version: 2.0
-- Date: 2024-10-14
-- 
-- Usage: clickhouse-client --multiquery --queries-file /path/to/00_master_init.sql
-- =====================================================

-- Display initialization banner
SELECT '🏪 EuroStyle Fashion - Master Database Initialization' as message FORMAT Pretty;
SELECT 'Initializing complete retail analytics platform...' as status FORMAT Pretty;

-- =====================================================
-- SYSTEM SETTINGS & CONFIGURATION
-- =====================================================

-- Enable advanced features
SET allow_experimental_object_type = 1;
SET allow_experimental_map_type = 1; 
SET allow_experimental_bigint_types = 1;

-- Performance optimizations for bulk operations
SET max_insert_threads = 4;
SET max_threads = 8;

SELECT 'System configuration completed ✅' as status FORMAT Pretty;

-- =====================================================  
-- 1. OPERATIONAL DATABASE (ERP)
-- =====================================================

SELECT 'Creating Operational Database (ERP)...' as status FORMAT Pretty;

-- Drop and recreate to ensure clean state
DROP DATABASE IF EXISTS eurostyle_operational;
CREATE DATABASE IF NOT EXISTS eurostyle_operational;

SELECT 'Operational database created ✅' as status FORMAT Pretty;

-- =====================================================
-- 2. WEBSHOP DATABASE (E-COMMERCE ANALYTICS) 
-- =====================================================

SELECT 'Creating Webshop Analytics Database...' as status FORMAT Pretty;

-- Drop and recreate to ensure clean state
DROP DATABASE IF EXISTS eurostyle_webshop;
CREATE DATABASE IF NOT EXISTS eurostyle_webshop;

SELECT 'Webshop database created ✅' as status FORMAT Pretty;

-- =====================================================
-- 3. FINANCE DATABASE (FINANCIAL MANAGEMENT)
-- =====================================================

SELECT 'Creating Finance Database...' as status FORMAT Pretty;

-- Drop and recreate to ensure clean state
DROP DATABASE IF EXISTS eurostyle_finance;
CREATE DATABASE IF NOT EXISTS eurostyle_finance;

SELECT 'Finance database created ✅' as status FORMAT Pretty;

-- =====================================================
-- 4. HR DATABASE (HUMAN RESOURCES)
-- =====================================================

SELECT 'Creating HR Database...' as status FORMAT Pretty;

-- Drop and recreate to ensure clean state  
DROP DATABASE IF EXISTS eurostyle_hr;
CREATE DATABASE IF NOT EXISTS eurostyle_hr;

SELECT 'HR database created ✅' as status FORMAT Pretty;

-- =====================================================
-- 5. POS DATABASE (POINT OF SALE)
-- =====================================================

SELECT 'Creating POS Database...' as status FORMAT Pretty;

-- Drop and recreate to ensure clean state
DROP DATABASE IF EXISTS eurostyle_pos;
CREATE DATABASE IF NOT EXISTS eurostyle_pos;

SELECT 'POS database created ✅' as status FORMAT Pretty;

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT '🎉 EuroStyle Fashion Database Platform Initialized!' as message FORMAT Pretty;
SELECT 'All 5 databases created successfully:' as status FORMAT Pretty;
SELECT '  • eurostyle_operational (ERP)' as databases FORMAT Pretty;
SELECT '  • eurostyle_webshop (E-commerce Analytics)' as databases FORMAT Pretty; 
SELECT '  • eurostyle_finance (Financial Management)' as databases FORMAT Pretty;
SELECT '  • eurostyle_hr (Human Resources)' as databases FORMAT Pretty;
SELECT '  • eurostyle_pos (Point of Sale)' as databases FORMAT Pretty;

SELECT 'Next: Execute individual database table creation scripts' as next_steps FORMAT Pretty;

-- Show database summary
SELECT 
    name as database_name,
    engine as database_engine,
    formatReadableSize(bytes_on_disk) as disk_usage
FROM system.databases 
WHERE name LIKE 'eurostyle_%'
ORDER BY name
FORMAT PrettyCompact;