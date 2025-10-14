-- =====================================================
-- EuroStyle Fashion - Webshop Database Setup
-- =====================================================
-- This script creates a separate webshop database for
-- tracking digital customer journey and e-commerce behavior
-- This represents the website/app analytics system

-- Create separate webshop database
CREATE DATABASE IF NOT EXISTS eurostyle_webshop;

-- Use the webshop database
-- Note: Tables will be created in eurostyle_webshop database

-- Web Sessions Table
-- Tracks user browsing sessions across country-specific sites
CREATE TABLE IF NOT EXISTS eurostyle_webshop.web_sessions (
    session_id String,
    customer_id Nullable(String),  -- NULL for anonymous sessions
    country_code String,           -- Which country site (nl.eurostyle.com, de.eurostyle.com, etc.)
    device_type String,            -- desktop, mobile, tablet
    browser String,
    operating_system String,
    session_start DateTime,
    session_end Nullable(DateTime),
    session_duration_seconds UInt32,
    page_views UInt16,
    unique_products_viewed UInt16,
    bounce_session Bool,            -- Single page session
    conversion_session Bool,        -- Session resulted in purchase
    utm_source Nullable(String),   -- Marketing attribution
    utm_medium Nullable(String),
    utm_campaign Nullable(String),
    referrer_url Nullable(String),
    landing_page String,
    exit_page Nullable(String),
    ip_address String,
    user_agent String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, session_start, session_id);

-- Page Views Table  
-- Tracks individual page and product views
CREATE TABLE IF NOT EXISTS eurostyle_webshop.page_views (
    page_view_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    page_type String,               -- homepage, category, product, checkout, etc.
    page_url String,
    page_title String,
    product_id Nullable(String),   -- If product page
    category_l1 Nullable(String),  -- If category page
    category_l2 Nullable(String),
    view_timestamp DateTime,
    time_on_page_seconds UInt16,
    scroll_depth_percent UInt8,    -- How far user scrolled (0-100)
    click_events UInt8,            -- Number of clicks on page
    is_mobile Bool,
    referrer_page Nullable(String),
    exit_page Bool,                -- Was this the last page in session?
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, view_timestamp, session_id);

-- Cart Activities Table
-- Tracks shopping cart interactions
CREATE TABLE IF NOT EXISTS eurostyle_webshop.cart_activities (
    cart_activity_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    activity_type String,          -- add_to_cart, remove_from_cart, update_quantity
    product_id String,
    size String,
    color String,
    quantity_before UInt16,
    quantity_after UInt16,
    unit_price_eur Decimal(18, 2),
    activity_timestamp DateTime,
    cart_total_items UInt16,       -- Total items in cart after this action
    cart_total_value_eur Decimal(18, 2), -- Total cart value after this action
    product_position_in_list Nullable(UInt16), -- Where product appeared in listing
    recommendation_type Nullable(String),      -- If from recommendations: similar, trending, etc.
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, activity_timestamp, session_id);

-- Search Queries Table
-- Tracks what customers search for
CREATE TABLE IF NOT EXISTS eurostyle_webshop.search_queries (
    search_query_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    search_term String,
    search_timestamp DateTime,
    results_count UInt32,
    clicked_result_position Nullable(UInt16), -- Which search result was clicked (1st, 2nd, etc.)
    clicked_product_id Nullable(String),
    filters_applied Array(String), -- ["color:black", "size:M", "category:dresses"]
    sort_order String,             -- relevance, price_low, price_high, newest, popular
    search_refinements UInt8,      -- How many times user refined the search
    no_results Bool,               -- Search returned no results
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, search_timestamp, session_id);

-- Product Reviews Table
-- Customer reviews and ratings
CREATE TABLE IF NOT EXISTS eurostyle_webshop.product_reviews (
    review_id String,
    product_id String,
    customer_id String,
    country_code String,
    rating UInt8,                  -- 1-5 stars
    review_title String,
    review_text String,
    review_date Date,
    verified_purchase Bool,        -- Customer actually bought the product
    helpful_votes UInt16,          -- How many found review helpful
    total_votes UInt16,            -- Total votes (helpful + not helpful)
    size_purchased Nullable(String),
    color_purchased Nullable(String),
    fit_rating Nullable(String),  -- runs_small, true_to_size, runs_large
    quality_rating Nullable(UInt8), -- Separate quality rating 1-5
    style_rating Nullable(UInt8),   -- Separate style rating 1-5
    review_status String,          -- pending, approved, rejected
    moderated_by Nullable(String), -- Staff member who approved
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (product_id, review_date, review_id);

-- Wishlist Items Table
-- Products saved by customers
CREATE TABLE IF NOT EXISTS eurostyle_webshop.wishlist_items (
    wishlist_item_id String,
    customer_id String,
    product_id String,
    country_code String,
    size Nullable(String),
    color Nullable(String),
    added_date DateTime,
    added_from_page String,       -- product_page, search_results, recommendations
    priority Nullable(String),    -- high, medium, low
    price_when_added_eur Decimal(18, 2),
    current_price_eur Decimal(18, 2),
    price_alert_enabled Bool,     -- Notify when price drops
    in_stock Bool,
    purchased Bool,               -- Item was eventually purchased
    purchase_date Nullable(Date),
    removed_date Nullable(DateTime),
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (customer_id, added_date, wishlist_item_id);

-- Web Analytics Events Table
-- Detailed interaction tracking
CREATE TABLE IF NOT EXISTS eurostyle_webshop.web_analytics_events (
    event_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    event_type String,            -- click, scroll, form_submit, video_play, etc.
    event_category String,        -- navigation, product_interaction, marketing
    event_action String,          -- button_click, image_zoom, newsletter_signup
    event_label Nullable(String), -- Specific element clicked/interacted with
    event_value Nullable(Decimal(18, 2)), -- Optional numeric value
    page_url String,
    element_selector Nullable(String),    -- CSS selector of element
    element_text Nullable(String),        -- Text content of element
    event_timestamp DateTime,
    user_journey_step UInt16,     -- Step in user journey (1=first interaction)
    ab_test_variant Nullable(String),    -- A/B testing variant
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, event_timestamp, session_id);

-- Email Marketing Table
-- Track email campaign interactions
CREATE TABLE IF NOT EXISTS eurostyle_webshop.email_marketing (
    email_event_id String,
    customer_id String,
    country_code String,
    campaign_id String,           -- Links to operational campaigns table
    email_type String,            -- newsletter, promotional, transactional
    email_subject String,
    event_type String,            -- sent, delivered, opened, clicked, unsubscribed, bounced
    event_timestamp DateTime,
    email_template_id Nullable(String),
    clicked_link_url Nullable(String),
    device_type Nullable(String),
    email_client Nullable(String), -- gmail, outlook, apple_mail, etc.
    conversion_value_eur Nullable(Decimal(18, 2)), -- Revenue if conversion occurred
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, event_timestamp, customer_id);

-- Product Recommendations Table
-- Track recommendation engine performance
CREATE TABLE IF NOT EXISTS eurostyle_webshop.product_recommendations (
    recommendation_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    recommendation_type String,   -- similar_items, frequently_bought_together, trending, personalized
    source_product_id Nullable(String), -- Product that triggered recommendation
    recommended_product_id String,
    recommendation_position UInt8, -- 1st, 2nd, 3rd recommended item
    page_context String,          -- product_page, cart_page, homepage
    algorithm_version String,     -- v1.2, collaborative_filtering, content_based
    confidence_score Decimal(5, 4), -- Algorithm confidence (0-1)
    shown_timestamp DateTime,
    clicked Bool,
    clicked_timestamp Nullable(DateTime),
    added_to_cart Bool,
    purchased Bool,
    revenue_eur Nullable(Decimal(18, 2)),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (country_code, shown_timestamp, session_id);

-- A/B Test Results Table
-- Track A/B testing performance
CREATE TABLE IF NOT EXISTS eurostyle_webshop.ab_test_results (
    ab_test_id String,
    session_id String,
    customer_id Nullable(String),
    country_code String,
    test_name String,
    variant String,               -- control, variant_a, variant_b, etc.
    assignment_timestamp DateTime,
    conversion_goal String,       -- purchase, signup, engagement
    converted Bool,
    conversion_timestamp Nullable(DateTime),
    conversion_value_eur Nullable(Decimal(18, 2)),
    page_views_in_test UInt16,
    time_to_conversion_seconds Nullable(UInt32),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (test_name, assignment_timestamp, session_id);