#!/usr/bin/env python3
"""
EuroStyle Complete Webshop Data Generator

Generates realistic data for all 10 webshop analytics tables:
1. web_sessions (already exists)
2. page_views (already exists) 
3. cart_activities
4. search_queries
5. product_reviews
6. wishlist_items
7. web_analytics_events
8. email_marketing
9. product_recommendations
10. ab_test_results
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import json

# Configuration
COUNTRIES = ['NL', 'BE', 'DE', 'FR', 'LU']
DEVICE_TYPES = ['desktop', 'mobile', 'tablet']
BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge']
SIZES = ['XS', 'S', 'M', 'L', 'XL', '32', '34', '36', '38', '40', '42']
COLORS = ['Black', 'White', 'Navy', 'Grey', 'Red', 'Blue', 'Green', 'Pink', 'Brown']

def load_existing_data():
    """Load existing customer and product data for referential integrity"""
    customers = []
    products = []
    sessions = []
    campaigns = []
    
    # Load customers
    try:
        import gzip
        with gzip.open('data/csv/customers.csv.gz', 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            customers = [row['customer_id'] for row in reader]
    except FileNotFoundError:
        print("Warning: customers.csv not found, using sample customer IDs")
        customers = [f"CUST_EU_{i:06d}" for i in range(1, 1001)]
    
    # Load products  
    try:
        import gzip
        with gzip.open('data/csv/products.csv.gz', 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = [row['product_id'] for row in reader]
    except FileNotFoundError:
        print("Warning: products.csv not found, using sample product IDs")
        products = [f"PROD_EU_{i:06d}" for i in range(1, 501)]
    
    # Load campaigns
    try:
        import gzip
        with gzip.open('data/csv/campaigns.csv.gz', 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            campaigns = [row['campaign_id'] for row in reader]
    except FileNotFoundError:
        print("Warning: campaigns.csv not found, using sample campaign IDs")
        campaigns = [f"CAMP_2024_SPRING_{i:03d}" for i in range(1, 21)]
        
    # Load existing web sessions
    try:
        with open('data/csv/eurostyle_webshop.web_sessions.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sessions = [(row['session_id'], row.get('customer_id', ''), row['country_code']) for row in reader]
    except FileNotFoundError:
        print("Warning: web_sessions.csv not found, generating sample sessions")
        sessions = [(f"SESSION_2024_{i:06d}", random.choice(customers) if random.random() > 0.3 else '', random.choice(COUNTRIES)) for i in range(1, 10001)]
    
    return customers, products, campaigns, sessions

def generate_cart_activities(customers: List[str], products: List[str], sessions: List[tuple], count: int = 50000):
    """Generate cart activities data"""
    activities = []
    
    for i in range(count):
        session_id, customer_id, country_code = random.choice(sessions)
        
        # Choose activity type with realistic probabilities
        activity_types = ['add_to_cart', 'remove_from_cart', 'update_quantity']
        weights = [0.7, 0.2, 0.1]  # Most activities are adding to cart
        activity_type = random.choices(activity_types, weights=weights)[0]
        
        product_id = random.choice(products)
        size = random.choice(SIZES)
        color = random.choice(COLORS)
        unit_price = round(random.uniform(19.99, 199.99), 2)
        
        # Generate quantities based on activity type
        if activity_type == 'add_to_cart':
            quantity_before = random.randint(0, 3)
            quantity_after = quantity_before + random.randint(1, 3)
        elif activity_type == 'remove_from_cart':
            quantity_before = random.randint(1, 5)
            quantity_after = max(0, quantity_before - random.randint(1, quantity_before))
        else:  # update_quantity
            quantity_before = random.randint(1, 3)
            quantity_after = random.randint(1, 5)
        
        cart_total_items = random.randint(quantity_after, quantity_after + 8)
        cart_total_value = round(cart_total_items * unit_price * random.uniform(0.8, 1.2), 2)
        
        # Add timestamps - spread over last 6 months
        base_date = datetime(2024, 6, 1)
        activity_timestamp = base_date + timedelta(days=random.randint(0, 180), 
                                                  hours=random.randint(0, 23), 
                                                  minutes=random.randint(0, 59))
        
        activities.append({
            'cart_activity_id': f"CART_2024_{i+1:010d}",
            'session_id': session_id,
            'customer_id': customer_id if customer_id else '',
            'country_code': country_code,
            'activity_type': activity_type,
            'product_id': product_id,
            'size': size,
            'color': color,
            'quantity_before': quantity_before,
            'quantity_after': quantity_after,
            'unit_price_eur': unit_price,
            'activity_timestamp': activity_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'cart_total_items': cart_total_items,
            'cart_total_value_eur': cart_total_value,
            'product_position_in_list': random.randint(1, 20) if random.random() > 0.4 else '',
            'recommendation_type': random.choice(['', 'similar', 'trending', 'personalized', 'frequently_bought_together']),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return activities

def generate_search_queries(sessions: List[tuple], products: List[str], count: int = 25000):
    """Generate search queries data"""
    queries = []
    
    # Common search terms in fashion
    search_terms = [
        'sustainable fashion', 'winter jacket', 'summer dress', 'jeans', 'sneakers',
        'black dress', 'white shirt', 'leather jacket', 'running shoes', 'wool sweater',
        'designer bags', 'casual wear', 'office attire', 'party dress', 'sports bra',
        'vintage style', 'eco friendly', 'organic cotton', 'plus size', 'maternity',
        'sale items', 'new arrivals', 'trending now', 'gift cards', 'accessories'
    ]
    
    for i in range(count):
        session_id, customer_id, country_code = random.choice(sessions)
        search_term = random.choice(search_terms)
        
        # Add some country-specific terms
        if country_code == 'DE':
            german_terms = ['nachhaltige mode', 'wintermantel', 'sommerkleid']
            if random.random() > 0.8:
                search_term = random.choice(german_terms)
        elif country_code == 'FR':
            french_terms = ['mode durable', 'veste d\'hiver', 'robe d\'été']
            if random.random() > 0.8:
                search_term = random.choice(french_terms)
        elif country_code == 'NL':
            dutch_terms = ['duurzame mode', 'winterjas', 'zomerjurk']
            if random.random() > 0.8:
                search_term = random.choice(dutch_terms)
        
        results_count = random.randint(0, 250) if search_term != 'xyz123' else 0
        no_results = results_count == 0
        
        # Generate realistic filters - format as ClickHouse Array(String)
        possible_filters = [
            'color:black', 'color:white', 'color:red', 'size:M', 'size:L', 
            'category:women', 'category:men', 'price:under50', 'price:50to100',
            'brand:eurostyle', 'material:cotton', 'sustainable:true'
        ]
        
        num_filters = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
        selected_filters = random.sample(possible_filters, num_filters)
        # Format as ClickHouse array syntax: ['item1','item2'] 
        filters_applied = '[' + ','.join([f"'{f}'" for f in selected_filters]) + ']' if selected_filters else '[]'
        
        search_timestamp = datetime(2024, 6, 1) + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        queries.append({
            'search_query_id': f"SEARCH_2024_{i+1:07d}",
            'session_id': session_id,
            'customer_id': customer_id if customer_id else '',
            'country_code': country_code,
            'search_term': search_term,
            'search_timestamp': search_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'results_count': results_count,
            'clicked_result_position': random.randint(1, min(10, results_count)) if results_count > 0 and random.random() > 0.3 else '',
            'clicked_product_id': random.choice(products) if results_count > 0 and random.random() > 0.4 else '',
            'filters_applied': filters_applied,
            'sort_order': random.choice(['relevance', 'price_low', 'price_high', 'newest', 'popular']),
            'search_refinements': random.randint(0, 5),
            'no_results': no_results,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return queries

def generate_product_reviews(customers: List[str], products: List[str], count: int = 15000):
    """Generate product reviews data"""
    reviews = []
    
    review_titles = [
        'Love this product!', 'Great quality', 'Perfect fit', 'Excellent value',
        'Disappointed with quality', 'Runs small', 'Beautiful design', 'Comfortable wear',
        'Not as expected', 'Amazing material', 'Poor stitching', 'Highly recommended',
        'Stylish and practical', 'Good for the price', 'Will buy again'
    ]
    
    review_texts = [
        'This item exceeded my expectations. Great quality and fast shipping!',
        'Perfect fit and beautiful color. Highly recommend this product.',
        'The material feels cheap and the sizing is off. Disappointed.',
        'Excellent quality and exactly as described. Will definitely order again.',
        'Good value for money. The style is trendy and comfortable to wear.',
        'Runs larger than expected but overall satisfied with the purchase.',
        'Beautiful design but arrived with some loose threads. Still keeping it.',
        'Love the sustainable materials used. Great to support eco-friendly fashion.'
    ]
    
    for i in range(count):
        customer_id = random.choice(customers)
        product_id = random.choice(products)
        
        # Generate ratings with realistic distribution (most positive)
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.15, 0.35, 0.35])[0]
        
        review_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))
        
        # Country code based on customer (simplified)
        country_code = random.choice(COUNTRIES)
        
        reviews.append({
            'review_id': f"REV_2024_{i+1:06d}",
            'product_id': product_id,
            'customer_id': customer_id,
            'country_code': country_code,
            'rating': rating,
            'review_title': random.choice(review_titles),
            'review_text': random.choice(review_texts),
            'review_date': review_date.strftime('%Y-%m-%d'),
            'verified_purchase': random.random() > 0.15,  # 85% verified
            'helpful_votes': random.randint(0, 50),
            'total_votes': random.randint(0, 60),
            'size_purchased': random.choice(SIZES) if random.random() > 0.3 else '',
            'color_purchased': random.choice(COLORS) if random.random() > 0.3 else '',
            'fit_rating': random.choice(['runs_small', 'true_to_size', 'runs_large']) if random.random() > 0.4 else '',
            'quality_rating': random.randint(1, 5) if random.random() > 0.3 else '',
            'style_rating': random.randint(1, 5) if random.random() > 0.3 else '',
            'review_status': random.choices(['approved', 'pending', 'rejected'], weights=[0.85, 0.12, 0.03])[0],
            'moderated_by': f"staff_{random.randint(1, 10)}" if random.random() > 0.7 else '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return reviews

def generate_wishlist_items(customers: List[str], products: List[str], count: int = 35000):
    """Generate wishlist items data"""
    wishlist_items = []
    
    for i in range(count):
        customer_id = random.choice(customers)
        product_id = random.choice(products)
        country_code = random.choice(COUNTRIES)
        
        added_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))
        price_when_added = round(random.uniform(19.99, 199.99), 2)
        current_price = round(price_when_added * random.uniform(0.8, 1.1), 2)  # Price may have changed
        
        purchased = random.random() > 0.75  # 25% conversion rate from wishlist
        purchase_date = added_date + timedelta(days=random.randint(1, 90)) if purchased else None
        removed = random.random() > 0.8 if not purchased else False
        
        wishlist_items.append({
            'wishlist_item_id': f"WISH_2024_{i+1:06d}",
            'customer_id': customer_id,
            'product_id': product_id,
            'country_code': country_code,
            'size': random.choice(SIZES) if random.random() > 0.4 else '',
            'color': random.choice(COLORS) if random.random() > 0.4 else '',
            'added_date': added_date.strftime('%Y-%m-%d %H:%M:%S'),
            'added_from_page': random.choice(['product_page', 'search_results', 'recommendations', 'category_page']),
            'priority': random.choice(['', 'high', 'medium', 'low']),
            'price_when_added_eur': price_when_added,
            'current_price_eur': current_price,
            'price_alert_enabled': random.random() > 0.7,
            'in_stock': random.random() > 0.15,  # 85% in stock
            'purchased': purchased,
            'purchase_date': purchase_date.strftime('%Y-%m-%d') if purchase_date else '',
            'removed_date': (added_date + timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S') if removed else '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return wishlist_items

def generate_web_analytics_events(sessions: List[tuple], count: int = 100000):
    """Generate web analytics events data"""
    events = []
    
    event_types = ['click', 'scroll', 'form_submit', 'video_play', 'image_zoom', 'hover']
    event_categories = ['navigation', 'product_interaction', 'marketing', 'checkout', 'user_engagement']
    event_actions = ['button_click', 'image_zoom', 'newsletter_signup', 'add_to_cart', 'filter_apply', 'social_share']
    
    page_urls = [
        'https://nl.eurostyle.com/', 'https://de.eurostyle.com/', 'https://fr.eurostyle.com/',
        'https://nl.eurostyle.com/women', 'https://de.eurostyle.com/men', 
        'https://fr.eurostyle.com/products/sustainable-tshirt'
    ]
    
    for i in range(count):
        session_id, customer_id, country_code = random.choice(sessions)
        
        event_timestamp = datetime(2024, 6, 1) + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        events.append({
            'event_id': f"EVENT_2024_{i+1:08d}",
            'session_id': session_id,
            'customer_id': customer_id if customer_id else '',
            'country_code': country_code,
            'event_type': random.choice(event_types),
            'event_category': random.choice(event_categories),
            'event_action': random.choice(event_actions),
            'event_label': f"element_{random.randint(1, 100)}" if random.random() > 0.3 else '',
            'event_value': round(random.uniform(1.0, 100.0), 2) if random.random() > 0.7 else '',
            'page_url': random.choice(page_urls),
            'element_selector': f"#btn-{random.randint(1, 50)}" if random.random() > 0.5 else '',
            'element_text': random.choice(['Buy Now', 'Add to Cart', 'Learn More', 'Sign Up']) if random.random() > 0.6 else '',
            'event_timestamp': event_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_journey_step': random.randint(1, 20),
            'ab_test_variant': random.choice(['', 'control', 'variant_a', 'variant_b']),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return events

def generate_email_marketing(customers: List[str], campaigns: List[str], count: int = 75000):
    """Generate email marketing events data"""
    events = []
    
    email_types = ['newsletter', 'promotional', 'transactional', 'welcome', 'abandoned_cart']
    event_types = ['sent', 'delivered', 'opened', 'clicked', 'unsubscribed', 'bounced']
    email_clients = ['gmail', 'outlook', 'apple_mail', 'yahoo', 'other']
    
    subjects = [
        'New Spring Collection is Here!', 'Don\'t Miss Out - 50% Off Sale',
        'Your Order Confirmation', 'Welcome to EuroStyle!', 'Complete Your Purchase'
    ]
    
    for i in range(count):
        customer_id = random.choice(customers)
        campaign_id = random.choice(campaigns)
        country_code = random.choice(COUNTRIES)
        
        email_type = random.choice(email_types)
        event_type = random.choices(event_types, weights=[1, 0.95, 0.25, 0.05, 0.01, 0.03])[0]
        
        event_timestamp = datetime(2024, 6, 1) + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        events.append({
            'email_event_id': f"EMAIL_2024_{i+1:06d}",
            'customer_id': customer_id,
            'country_code': country_code,
            'campaign_id': campaign_id,
            'email_type': email_type,
            'email_subject': random.choice(subjects),
            'event_type': event_type,
            'event_timestamp': event_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'email_template_id': f"template_{random.randint(1, 20)}" if random.random() > 0.3 else '',
            'clicked_link_url': f"https://{country_code.lower()}.eurostyle.com/products/{random.randint(1, 100)}" if event_type == 'clicked' else '',
            'device_type': random.choice(DEVICE_TYPES) if event_type in ['opened', 'clicked'] else '',
            'email_client': random.choice(email_clients) if event_type in ['opened', 'clicked'] else '',
            'conversion_value_eur': round(random.uniform(50.0, 200.0), 2) if event_type == 'clicked' and random.random() > 0.8 else '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return events

def generate_product_recommendations(sessions: List[tuple], products: List[str], count: int = 200000):
    """Generate product recommendations data"""
    recommendations = []
    
    recommendation_types = ['similar_items', 'frequently_bought_together', 'trending', 'personalized', 'cross_sell']
    page_contexts = ['product_page', 'cart_page', 'homepage', 'category_page', 'checkout_page']
    algorithm_versions = ['v1.2', 'collaborative_filtering', 'content_based', 'hybrid_v2', 'ml_boost_v3']
    
    for i in range(count):
        session_id, customer_id, country_code = random.choice(sessions)
        
        rec_type = random.choice(recommendation_types)
        source_product = random.choice(products) if rec_type in ['similar_items', 'frequently_bought_together'] else ''
        recommended_product = random.choice(products)
        
        shown_timestamp = datetime(2024, 6, 1) + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        clicked = random.random() > 0.85  # 15% CTR
        added_to_cart = clicked and random.random() > 0.7  # 30% add to cart rate from clicks
        purchased = added_to_cart and random.random() > 0.6  # 40% purchase rate from adds
        
        recommendations.append({
            'recommendation_id': f"REC_2024_{i+1:08d}",
            'session_id': session_id,
            'customer_id': customer_id if customer_id else '',
            'country_code': country_code,
            'recommendation_type': rec_type,
            'source_product_id': source_product,
            'recommended_product_id': recommended_product,
            'recommendation_position': random.randint(1, 8),
            'page_context': random.choice(page_contexts),
            'algorithm_version': random.choice(algorithm_versions),
            'confidence_score': round(random.uniform(0.1, 0.99), 4),
            'shown_timestamp': shown_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'clicked': clicked,
            'clicked_timestamp': (shown_timestamp + timedelta(seconds=random.randint(1, 300))).strftime('%Y-%m-%d %H:%M:%S') if clicked else '',
            'added_to_cart': added_to_cart,
            'purchased': purchased,
            'revenue_eur': round(random.uniform(29.99, 159.99), 2) if purchased else '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return recommendations

def generate_ab_test_results(sessions: List[tuple], count: int = 30000):
    """Generate A/B test results data"""
    results = []
    
    test_names = ['homepage_layout_v2', 'checkout_flow_optimization', 'product_page_redesign', 
                 'email_subject_testing', 'mobile_navigation_test', 'pricing_display_test']
    variants = ['control', 'variant_a', 'variant_b', 'variant_c']
    conversion_goals = ['purchase', 'signup', 'engagement', 'cart_add', 'newsletter_signup']
    
    for i in range(count):
        session_id, customer_id, country_code = random.choice(sessions)
        
        test_name = random.choice(test_names)
        variant = random.choice(variants)
        goal = random.choice(conversion_goals)
        
        assignment_timestamp = datetime(2024, 6, 1) + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Conversion rates vary by variant (variant_a usually performs better)
        conversion_rates = {'control': 0.15, 'variant_a': 0.18, 'variant_b': 0.16, 'variant_c': 0.14}
        converted = random.random() < conversion_rates.get(variant, 0.15)
        
        conversion_timestamp = None
        conversion_value = None
        time_to_conversion = None
        
        if converted:
            time_to_conversion = random.randint(60, 3600)  # 1 minute to 1 hour
            conversion_timestamp = assignment_timestamp + timedelta(seconds=time_to_conversion)
            if goal == 'purchase':
                conversion_value = round(random.uniform(39.99, 299.99), 2)
        
        results.append({
            'ab_test_id': f"ABT_2024_{i+1:06d}",
            'session_id': session_id,
            'customer_id': customer_id if customer_id else '',
            'country_code': country_code,
            'test_name': test_name,
            'variant': variant,
            'assignment_timestamp': assignment_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'conversion_goal': goal,
            'converted': converted,
            'conversion_timestamp': conversion_timestamp.strftime('%Y-%m-%d %H:%M:%S') if conversion_timestamp else '',
            'conversion_value_eur': conversion_value if conversion_value else '',
            'page_views_in_test': random.randint(1, 15),
            'time_to_conversion_seconds': time_to_conversion if time_to_conversion else '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return results

def write_csv(data: List[Dict], filename: str):
    """Write data to CSV file"""
    if not data:
        print(f"No data to write for {filename}")
        return
        
    output_path = Path('data/csv') / filename
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Generated {len(data):,} records in {filename}")

def main():
    print("🚀 Generating complete EuroStyle webshop analytics data...")
    print("Loading existing data for referential integrity...")
    
    customers, products, campaigns, sessions = load_existing_data()
    
    print(f"Loaded {len(customers):,} customers, {len(products):,} products, {len(campaigns):,} campaigns, {len(sessions):,} sessions")
    
    # Generate all missing webshop tables
    print("\n📊 Generating webshop analytics tables...")
    
    print("3. Generating cart_activities...")
    cart_data = generate_cart_activities(customers, products, sessions, 50000)
    write_csv(cart_data, 'eurostyle_webshop.cart_activities.csv')
    
    print("4. Generating search_queries...")
    search_data = generate_search_queries(sessions, products, 25000)
    write_csv(search_data, 'eurostyle_webshop.search_queries.csv')
    
    print("5. Generating product_reviews...")
    review_data = generate_product_reviews(customers, products, 15000)
    write_csv(review_data, 'eurostyle_webshop.product_reviews.csv')
    
    print("6. Generating wishlist_items...")
    wishlist_data = generate_wishlist_items(customers, products, 35000)
    write_csv(wishlist_data, 'eurostyle_webshop.wishlist_items.csv')
    
    print("7. Generating web_analytics_events...")
    events_data = generate_web_analytics_events(sessions, 100000)
    write_csv(events_data, 'eurostyle_webshop.web_analytics_events.csv')
    
    print("8. Generating email_marketing...")
    email_data = generate_email_marketing(customers, campaigns, 75000)
    write_csv(email_data, 'eurostyle_webshop.email_marketing.csv')
    
    print("9. Generating product_recommendations...")
    rec_data = generate_product_recommendations(sessions, products, 200000)
    write_csv(rec_data, 'eurostyle_webshop.product_recommendations.csv')
    
    print("10. Generating ab_test_results...")
    ab_data = generate_ab_test_results(sessions, 30000)
    write_csv(ab_data, 'eurostyle_webshop.ab_test_results.csv')
    
    print(f"\n✅ Complete webshop data generation finished!")
    print("Generated files:")
    
    output_dir = Path('data/csv')
    for file in sorted(output_dir.glob('eurostyle_webshop.*.csv')):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  📄 {file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()