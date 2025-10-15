-- =====================================================
-- EuroStyle Fashion - Database Initialization Script
-- =====================================================
-- Creates the eurostyle_operational database and all tables
-- for the European fashion retail demo system

-- Create the operational database
CREATE DATABASE IF NOT EXISTS eurostyle_operational;

-- Use the database for subsequent table creation
USE eurostyle_operational;

-- =====================================================
-- 1. CUSTOMERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id String,              -- CUST_EU_000001, CUST_EU_000002
    email String,                    -- primary identifier for online
    first_name String,               -- Jan, Emma, Lars, Sophie, Pierre, Hans
    last_name String,                -- van der Berg, Müller, Dubois, etc.
    phone String,                    -- country-specific formats
    date_of_birth Date,              -- for age demographics
    gender Enum8('M' = 1, 'F' = 2, 'O' = 3),
    language_preference String,      -- nl, de, fr, en
    
    -- Address information
    street_address String,
    city String,
    postal_code String,              -- country-specific formats
    country_code String,             -- NL, BE, DE, FR, LU
    region String,                   -- province/state/region
    
    -- Customer lifecycle
    registration_date DateTime,      -- when they first registered
    registration_channel String,     -- online, in-store, social, referral
    customer_status Enum8('active' = 1, 'inactive' = 2, 'suspended' = 3),
    
    -- Marketing preferences (GDPR compliant)
    marketing_opt_in Bool,
    newsletter_subscription Bool,
    sms_opt_in Bool,
    
    -- Customer value metrics
    total_orders UInt32,
    total_spent Decimal64(2),
    average_order_value Decimal64(2),
    last_order_date Date,
    
    -- Loyalty program
    loyalty_member Bool,
    loyalty_points UInt32,
    loyalty_tier String,             -- Bronze, Silver, Gold, Platinum
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY customer_id;

-- =====================================================
-- 2. PRODUCTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS products (
    product_id String,               -- PROD_EU_000001, SKU format
    product_name String,             -- "Sustainable Cotton T-Shirt"  
    product_name_local Map(String, String), -- translations per country
    
    -- Product hierarchy
    category_l1 String,              -- Women, Men, Kids, Accessories
    category_l2 String,              -- Tops, Bottoms, Dresses, Shoes
    category_l3 String,              -- T-Shirts, Jeans, Casual Dresses
    
    -- Product attributes
    brand String,                    -- EuroStyle, EuroStyle Premium, etc.
    color_primary String,            -- Black, White, Navy, etc.
    color_secondary String,          -- accent colors
    size_range Array(String),        -- ['XS', 'S', 'M', 'L', 'XL']
    material_composition String,     -- "80% Organic Cotton, 20% Recycled Polyester"
    
    -- Pricing (multi-currency)
    price_eur Decimal64(2),          -- base price in EUR
    price_local Map(String, Decimal64(2)), -- local currency prices
    cost_price_eur Decimal64(2),     -- wholesale cost
    margin_percentage Decimal64(2),   -- profit margin
    
    -- Sustainability metrics  
    sustainability_score UInt8,      -- 1-10 rating
    eco_friendly_materials Bool,
    carbon_footprint_kg Decimal32(2),
    production_country String,       -- mostly European production
    
    -- Inventory management
    current_stock_total UInt32,      -- across all locations
    reorder_level UInt32,
    lead_time_days UInt16,
    
    -- Product lifecycle
    launch_date Date,
    season String,                   -- Spring/Summer, Fall/Winter
    is_active Bool,
    discontinue_date Nullable(Date),
    
    -- Web presence
    online_availability Bool,
    product_url String,
    image_urls Array(String),
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY product_id;

-- =====================================================
-- 3. STORES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS stores (
    store_id String,                 -- STORE_NL_001, STORE_DE_001, etc.
    store_name String,               -- "EuroStyle Amsterdam Central"
    
    -- Location details
    country_code String,             -- NL, BE, DE, FR, LU  
    city String,
    address String,
    postal_code String,
    latitude Decimal64(6),
    longitude Decimal64(6),
    
    -- Store characteristics  
    store_format String,             -- flagship, standard, outlet, popup
    floor_area_sqm UInt32,
    opening_date Date,
    
    -- Operational details
    manager_name String,
    staff_count UInt16,
    operating_hours String,          -- "Mon-Sat 10:00-20:00, Sun 12:00-18:00"
    
    -- Performance tier
    performance_tier String,         -- A, B, C based on revenue
    target_monthly_revenue Decimal64(2),
    
    -- Store amenities
    has_fitting_rooms Bool,
    has_personal_styling Bool,
    has_click_and_collect Bool,
    wheelchair_accessible Bool,
    
    is_active Bool,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY store_id;

-- =====================================================
-- 4. ORDERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id String,                 -- ORD_EU_2024_000001
    customer_id String,              -- FK to customers
    store_id String DEFAULT 'ONLINE', -- 'ONLINE' for online orders, store ID for in-store
    
    -- Order timing
    order_date Date,
    order_datetime DateTime,
    delivery_date Nullable(Date),
    promised_delivery_date Nullable(Date),
    
    -- Financial details
    subtotal_eur Decimal64(2),       -- before tax and shipping
    tax_amount_eur Decimal64(2),     -- VAT varies by country
    shipping_cost_eur Decimal64(2),
    discount_amount_eur Decimal64(2),
    total_amount_eur Decimal64(2),   -- final amount
    
    -- Local currency (for non-EUR countries)
    currency_code String,            -- EUR, (future: other currencies)
    exchange_rate Decimal64(4),      -- conversion rate used
    total_amount_local Decimal64(2), -- amount in local currency
    
    -- Order fulfillment
    order_status String,             -- pending, confirmed, shipped, delivered, cancelled, returned
    fulfillment_center String,       -- which DC processed the order
    shipping_method String,          -- standard, express, same-day, in-store-pickup
    tracking_number Nullable(String),
    
    -- Channel attribution
    order_channel String,            -- online, in-store, mobile-app, phone
    traffic_source String,           -- organic, paid-search, social, email, direct
    campaign_code Nullable(String),  -- marketing campaign tracking
    
    -- Payment details
    payment_method String,           -- credit-card, paypal, klarna, bancontact, ideal
    payment_status String,           -- pending, completed, failed, refunded
    
    -- Customer service
    customer_service_notes Nullable(String),
    return_reason Nullable(String),
    return_date Nullable(Date),
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (order_date, order_id);

-- =====================================================
-- 5. ORDER LINES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS order_lines (
    order_line_id String,            -- unique line identifier
    order_id String,                 -- FK to orders
    product_id String,               -- FK to products
    
    -- Product variant details
    size String,                     -- S, M, L, XL, etc.
    color String,                    -- specific color variant
    
    -- Quantity and pricing
    quantity UInt16,
    unit_price_eur Decimal64(2),     -- price per item at time of order
    unit_cost_eur Decimal64(2),      -- cost per item for margin analysis
    line_discount_eur Decimal64(2),  -- line-specific discounts
    line_total_eur Decimal64(2),     -- final line total
    
    -- Fulfillment tracking
    fulfillment_status String,       -- pending, picked, packed, shipped, delivered
    shipped_quantity UInt16,         -- may differ from ordered quantity
    
    -- Returns and exchanges
    returned_quantity UInt16,
    return_reason Nullable(String),  -- too-small, too-large, defective, changed-mind
    exchange_product_id Nullable(String), -- if exchanged for different product
    
    -- Inventory impact
    inventory_reserved_at DateTime,  -- when stock was allocated
    inventory_fulfilled_at Nullable(DateTime), -- when physically picked
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (order_id, order_line_id);

-- =====================================================
-- 6. INVENTORY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id String,             -- unique inventory tracking ID
    product_id String,               -- FK to products
    store_id String DEFAULT 'DC',   -- 'DC' for distribution center, store ID for stores
    location_type String,            -- store, distribution-center, warehouse
    
    -- Product variant
    size String,
    color String,
    
    -- Stock levels
    quantity_on_hand UInt32,
    quantity_reserved UInt32,        -- reserved for orders
    quantity_available UInt32,       -- on_hand - reserved
    quantity_on_order UInt32,        -- incoming from suppliers
    
    -- Inventory management
    reorder_point UInt32,
    max_stock_level UInt32,
    last_restock_date Date,
    next_restock_date Nullable(Date),
    
    -- Inventory valuation
    unit_cost_eur Decimal64(2),      -- current cost per unit
    inventory_value_eur Decimal64(2), -- quantity * unit_cost
    
    -- Movement tracking
    last_movement_date DateTime,
    last_movement_type String,       -- received, sold, transferred, adjusted
    
    -- Seasonal management
    season String,                   -- current season relevance
    markdown_date Nullable(Date),    -- when item goes on sale
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (product_id, store_id, size, color);

-- =====================================================
-- 7. MARKETING CAMPAIGNS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id String,              -- CAMP_2024_SPRING_001
    campaign_name String,            -- "Spring Collection Launch 2024"
    
    -- Campaign details
    campaign_type String,            -- product-launch, seasonal, clearance, brand-awareness
    channel String,                  -- email, social-media, google-ads, display, influencer
    target_countries String,         -- Semi-colon delimited: 'NL; BE; DE'
    
    -- Timing
    start_date Date,
    end_date Date,
    
    -- Budget and performance
    budget_eur Decimal64(2),
    spend_eur Decimal64(2),
    target_impressions UInt64,
    actual_impressions UInt64,
    target_clicks UInt64,
    actual_clicks UInt64,
    target_conversions UInt32,
    actual_conversions UInt32,
    
    -- Content
    campaign_message String,
    discount_percentage Nullable(Decimal32(2)),
    promotional_code Nullable(String),
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY campaign_id;

-- =====================================================
-- 8. EUROPEAN GEOGRAPHY REFERENCE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS european_geography (
    geo_id String,
    country_code String,             -- NL, BE, DE, FR, LU
    country_name String,
    region String,                   -- Noord-Holland, Vlaanderen, Bayern, Île-de-France
    city String,
    postal_code String,
    latitude Decimal64(6),
    longitude Decimal64(6),
    population UInt32,
    economic_index Decimal32(2),     -- relative purchasing power
    timezone String,                 -- Europe/Amsterdam, Europe/Berlin, etc.
    
    -- Market characteristics
    fashion_market_size_eur Decimal64(2), -- estimated local market
    competition_density String,      -- low, medium, high
    avg_income_eur Decimal64(2),     -- average household income
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (country_code, city, postal_code);

-- =====================================================
-- 9. EUROPEAN FASHION CALENDAR REFERENCE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS fashion_calendar (
    date Date,
    country_code String,
    event_name String,               -- "Fashion Week Milan", "Black Friday", "Sinterklaas"
    event_type String,               -- fashion-event, shopping-holiday, cultural-holiday
    impact_level String,             -- high, medium, low
    expected_sales_lift Decimal32(2), -- percentage increase expected
    
    -- Season mapping
    fashion_season String,           -- Spring/Summer 2024, Fall/Winter 2024
    collection_phase String,        -- launch, peak, markdown, clearance
    
    -- Marketing relevance
    campaign_opportunity Bool,       -- should we run campaigns?
    inventory_planning Bool,         -- impacts inventory decisions?
    
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (date, country_code);

-- =====================================================
-- DATABASE SETUP COMPLETE
-- =====================================================
-- The eurostyle_operational database has been created with:
-- - 7 core business tables (customers, products, stores, orders, order_lines, inventory, campaigns)
-- - 2 reference data tables (european_geography, fashion_calendar)
-- - Proper ClickHouse engines optimized for the data patterns
-- - Indexes and partitioning for optimal query performance