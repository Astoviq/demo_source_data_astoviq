-- =====================================================
-- EuroStyle Fashion - Finance Database Initialization
-- =====================================================
-- Creates the eurostyle_finance database and all tables
-- for multi-entity European finance management

-- Create the finance database
CREATE DATABASE IF NOT EXISTS eurostyle_finance;

-- Use the database for subsequent table creation
USE eurostyle_finance;

-- =====================================================
-- 1. LEGAL ENTITIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS legal_entities (
    entity_id String,                    -- ENTITY_NL_HOLDING, ENTITY_DE_BV
    entity_code String,                  -- ESLH, ESDE, ESFR, ESBE, ESLU
    entity_name String,                  -- EuroStyle Fashion Holding B.V.
    entity_type String,                  -- HOLDING, BV
    country_code String,                 -- NL, DE, FR, BE, LU
    registration_number String,          -- KVK-24123456, HRB-12345
    tax_id String,                       -- NL123456789B01, DE123456789
    functional_currency String,          -- EUR
    parent_entity_id Nullable(String),   -- FK to parent entity
    incorporation_date Date,
    fiscal_year_end String,              -- 12-31
    legal_address String,
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY entity_id;

-- =====================================================
-- 2. ENTITY RELATIONSHIPS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS entity_relationships (
    relationship_id String,
    parent_entity_id String,             -- FK to legal_entities
    child_entity_id String,              -- FK to legal_entities
    ownership_percentage Decimal64(2),   -- 100.00 for full ownership
    relationship_type String,            -- SUBSIDIARY, BRANCH
    effective_date Date,
    end_date Nullable(Date),
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY relationship_id;

-- =====================================================
-- 3. CURRENCIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS currencies (
    currency_code String,                -- EUR, USD, GBP
    currency_name String,                -- Euro, US Dollar, British Pound
    currency_symbol String,              -- €, $, £
    decimal_places UInt8,                -- 2
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY currency_code;

-- =====================================================
-- 4. CHART OF ACCOUNTS TABLE  
-- =====================================================
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    account_id String,                   -- COA_1000_001
    account_code String,                 -- 1000, 1100, 4000
    account_name String,                 -- Cash and Cash Equivalents
    account_type String,                 -- ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_subtype String,              -- CURRENT_ASSET, FIXED_ASSET, CURRENT_LIABILITY
    parent_account_id Nullable(String), -- FK to parent account
    is_detail_account Bool,              -- True if leaf node
    normal_balance String,               -- DEBIT, CREDIT
    account_category String,             -- BS (Balance Sheet), IS (Income Statement)
    ifrs_classification String,          -- IFRS account classification
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY account_code;

-- =====================================================
-- 5. ENTITY ACCOUNTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS entity_accounts (
    entity_account_id String,
    entity_id String,                    -- FK to legal_entities
    account_id String,                   -- FK to chart_of_accounts
    local_account_code Nullable(String), -- Local GAAP account code
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY (entity_id, account_id);

-- =====================================================
-- 6. REPORTING PERIODS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS reporting_periods (
    period_id String,                    -- PER_2024_01, PER_2024_Q1, PER_2024_Y
    period_type String,                  -- MONTH, QUARTER, YEAR
    period_name String,                  -- January 2024, Q1 2024, 2024
    start_date Date,
    end_date Date,
    fiscal_year UInt16,
    is_closed Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY period_id;

-- =====================================================
-- 7. COST CENTERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS cost_centers (
    cost_center_id String,              -- CC_NL_001, CC_DE_001
    cost_center_code String,             -- NL_OPS, DE_RETAIL
    cost_center_name String,             -- Netherlands Operations
    entity_id String,                   -- FK to legal_entities
    cost_center_type String,             -- OPERATIONAL, ADMINISTRATIVE, SALES
    manager_name Nullable(String),
    department String,
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY cost_center_id;

-- =====================================================
-- 8. EXCHANGE RATES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS exchange_rates (
    exchange_rate_id String,
    base_currency String,                -- EUR
    target_currency String,              -- USD, GBP
    rate_date Date,
    exchange_rate Decimal64(6),          -- 1.123456
    rate_type String,                    -- SPOT, AVERAGE, CLOSING
    data_source String,                  -- ECB, REUTERS, BLOOMBERG
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY (base_currency, target_currency, rate_date);

-- =====================================================
-- 9. GL JOURNAL HEADERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS gl_journal_headers (
    journal_header_id String,           -- JH_2024_000001
    journal_number String,              -- JV-2024-001
    entity_id String,                   -- FK to legal_entities
    period_id String,                   -- FK to reporting_periods
    journal_date Date,
    posting_date Date,
    journal_type String,                -- STANDARD, ACCRUAL, RECLASSIFICATION
    journal_source String,              -- MANUAL, SYSTEM, IMPORT
    reference_number Nullable(String),  -- Invoice number, PO number
    description String,
    total_debit_amount Decimal64(2),
    total_credit_amount Decimal64(2),
    currency_code String,
    exchange_rate Decimal64(6),
    journal_status String,              -- DRAFT, POSTED, REVERSED
    created_by String,
    approved_by Nullable(String),
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY (journal_date, journal_header_id);

-- =====================================================
-- 10. GL JOURNAL LINES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS gl_journal_lines (
    journal_line_id String,             -- JL_2024_000001_001
    journal_header_id String,           -- FK to gl_journal_headers
    line_number UInt16,                 -- 1, 2, 3
    account_id String,                  -- FK to chart_of_accounts
    cost_center_id Nullable(String),   -- FK to cost_centers
    debit_amount Decimal64(2),
    credit_amount Decimal64(2),
    currency_code String,
    exchange_rate Decimal64(6),
    line_description String,
    reference_1 Nullable(String),       -- Additional reference
    reference_2 Nullable(String),       -- Additional reference
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (journal_header_id, line_number);

-- =====================================================
-- 11. BUDGET VERSIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS budget_versions (
    budget_version_id String,           -- BV_2024_V1, BV_2024_V2
    version_name String,                -- Original Budget 2024, Revised Q2
    fiscal_year UInt16,
    entity_id String,                   -- FK to legal_entities
    version_type String,                -- ORIGINAL, REVISED, FORECAST
    status String,                      -- DRAFT, APPROVED, LOCKED
    created_by String,
    approved_by Nullable(String),
    approval_date Nullable(Date),
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY budget_version_id;

-- =====================================================
-- 12. BUDGET DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS budget_data (
    budget_line_id String,              -- BL_2024_000001
    budget_version_id String,           -- FK to budget_versions
    entity_id String,                   -- FK to legal_entities
    account_id String,                  -- FK to chart_of_accounts
    cost_center_id Nullable(String),   -- FK to cost_centers
    period_id String,                   -- FK to reporting_periods
    budget_amount Decimal64(2),
    currency_code String,
    comments Nullable(String),
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (budget_version_id, entity_id, account_id, period_id);

-- =====================================================
-- 13. FIXED ASSETS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS fixed_assets (
    asset_id String,                    -- FA_NL_000001
    asset_code String,                  -- COMP-2024-001
    asset_name String,                  -- Dell Laptop XPS 13
    entity_id String,                   -- FK to legal_entities
    asset_category String,              -- COMPUTER, FURNITURE, EQUIPMENT
    cost_center_id Nullable(String),   -- FK to cost_centers
    purchase_date Date,
    purchase_cost Decimal64(2),
    currency_code String,
    useful_life_years UInt8,
    depreciation_method String,         -- STRAIGHT_LINE, DECLINING_BALANCE
    salvage_value Decimal64(2),
    accumulated_depreciation Decimal64(2),
    book_value Decimal64(2),
    asset_location String,
    serial_number Nullable(String),
    supplier_name Nullable(String),
    warranty_expiry Nullable(Date),
    asset_status String,                -- ACTIVE, DISPOSED, RETIRED
    disposal_date Nullable(Date),
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY asset_id;

-- =====================================================
-- 14. DEPRECIATION SCHEDULE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS depreciation_schedule (
    depreciation_id String,             -- DEP_2024_000001_01
    asset_id String,                    -- FK to fixed_assets
    period_id String,                   -- FK to reporting_periods
    depreciation_date Date,
    depreciation_amount Decimal64(2),
    accumulated_depreciation Decimal64(2),
    book_value Decimal64(2),
    is_posted Bool,
    journal_header_id Nullable(String), -- FK to gl_journal_headers if posted
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (asset_id, depreciation_date);

-- =====================================================
-- FINANCE DATABASE SETUP COMPLETE
-- =====================================================
-- The eurostyle_finance database has been created with:
-- - 14 comprehensive finance tables
-- - Multi-entity BV structure support  
-- - IFRS compliance
-- - Multi-currency capabilities
-- - Proper ClickHouse engines optimized for finance data patterns