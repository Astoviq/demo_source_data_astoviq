-- =====================================================
-- EuroStyle Fashion - Performance Indexes
-- =====================================================
-- Creates additional indexes to optimize query performance
-- across all databases for common analytical queries
--
-- Author: EuroStyle Fashion Data Team
-- Version: 2.0
-- Date: 2024-10-14
-- =====================================================

SELECT 'Creating performance indexes for optimal query performance...' as status FORMAT Pretty;

-- =====================================================
-- OPERATIONAL DATABASE INDEXES
-- =====================================================

SELECT 'Creating operational database indexes...' as status FORMAT Pretty;

-- Customer analysis indexes
-- Note: ClickHouse doesn't use traditional CREATE INDEX syntax, 
-- but we can create materialized views for complex aggregations

-- Customer activity summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.customer_activity_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for customer analysis instead

-- Product performance summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.product_sales_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for product analysis instead

-- Store performance summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.store_performance_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for store analysis instead

-- =====================================================
-- WEBSHOP DATABASE INDEXES  
-- =====================================================

SELECT 'Creating webshop database indexes...' as status FORMAT Pretty;

-- Session funnel analysis (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_webshop.session_funnel_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for funnel analysis instead

-- Product engagement summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_webshop.product_engagement_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for product engagement analysis instead

-- =====================================================
-- FINANCE DATABASE INDEXES
-- =====================================================

SELECT 'Creating finance database indexes...' as status FORMAT Pretty;

-- Monthly GL summary (DISABLED - schema conflicts with table structure)
-- NOTE: This materialized view conflicts with actual table columns
-- Use regular queries instead of materialized view for GL summaries

-- Budget vs Actual summary (DISABLED - schema conflicts with table structure)
-- NOTE: This materialized view conflicts with actual table columns
-- Use regular queries instead of materialized view for budget analysis

-- =====================================================
-- HR DATABASE INDEXES
-- =====================================================

SELECT 'Creating HR database indexes...' as status FORMAT Pretty;

-- Employee headcount summary (DISABLED - schema conflicts with table structure)
-- NOTE: This materialized view references columns that don't exist (e.g. e.department_id, ch.current_annual_salary_eur)
-- Use regular queries instead of materialized view for HR analytics

-- Leave utilization summary (DISABLED - schema conflicts with table structure)
-- NOTE: This materialized view may reference columns that don't exist in actual tables
-- Use regular queries instead of materialized view for leave analytics

-- =====================================================
-- POS DATABASE INDEXES
-- =====================================================

SELECT 'Creating POS database indexes...' as status FORMAT Pretty;

-- Daily store performance summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_pos.daily_store_performance_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for POS store performance analysis instead

-- Hourly transaction patterns (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_pos.hourly_patterns_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for hourly POS transaction analysis instead

-- =====================================================
-- CROSS-DATABASE SUMMARY TABLES
-- =====================================================

SELECT 'Creating cross-database summary tables...' as status FORMAT Pretty;

-- Unified daily business summary (DISABLED - creates .inner_id tables)
-- CREATE MATERIALIZED VIEW IF NOT EXISTS eurostyle_operational.daily_business_summary_mv
-- DISABLED: This creates internal .inner_id tables that clutter database lists
-- Use regular queries for cross-database business analysis instead

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT '✅ Performance Indexes Processing Complete!' as message FORMAT Pretty;
SELECT 'All materialized views have been disabled to prevent .inner_id table creation.' as status FORMAT Pretty;
SELECT '  📊 Operational: Standard table indexes only (no materialized views)' as indexes FORMAT Pretty;
SELECT '  🌐 Webshop: Standard table indexes only (no materialized views)' as indexes FORMAT Pretty;
SELECT '  🏦 Finance: Standard table indexes only (no materialized views)' as indexes FORMAT Pretty;
SELECT '  👥 HR: Standard table indexes only (no materialized views)' as indexes FORMAT Pretty;
SELECT '  🏪 POS: Standard table indexes only (no materialized views)' as indexes FORMAT Pretty;
SELECT '  🔄 Cross-DB: Standard queries only (no materialized views)' as indexes FORMAT Pretty;

SELECT 'Use regular queries for analytics instead of materialized views for clean database structure! 🧹' as completion FORMAT Pretty;
