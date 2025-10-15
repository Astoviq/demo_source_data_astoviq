#!/usr/bin/env python3
"""
Webshop Entity Generator - WARP.md Compliant
============================================

Following WARP.md Rule: "dont hard code, always use guidelines and framework principles"

This module provides configuration-driven generation for webshop entities including:
- Product Reviews
- Email Marketing Campaigns  
- Search Queries
- Web Analytics Events
- A/B Test Results
- Wishlist Items
- Cart Activities
- Product Recommendations

All generation follows YAML configuration patterns and business logic.
"""

import random
import yaml
from faker import Faker
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging

class WebshopEntityGenerator:
    """WARP.md compliant generator for webshop entities."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.faker = Faker()
        self.logger = logging.getLogger(__name__)
        self._load_configurations()
        
    def _load_configurations(self):
        """Load all configuration files following WARP.md principles."""
        try:
            # Load existing webshop missing tables patterns
            patterns_file = self.config_path / 'data_patterns' / 'webshop_missing_tables.yaml'
            with open(patterns_file, 'r') as f:
                self.patterns = yaml.safe_load(f)
                self.logger.info(f"✅ Loaded webshop patterns from {patterns_file}")
        except FileNotFoundError:
            self.logger.error(f"❌ Missing configuration file: {patterns_file}")
            self.patterns = {}
    
    def generate_all_entities(self, mode: str, dependencies: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Generate all webshop entities following configuration patterns."""
        
        self.logger.info(f"🛍️ Generating webshop entities in {mode} mode")
        self.logger.info(f"🔗 Dependencies: {list(dependencies.keys())}")
        
        results = {}
        
        # Generate each entity type
        entities = [
            ('product_reviews', self.generate_product_reviews),
            ('email_marketing', self.generate_email_marketing),
            ('search_queries', self.generate_search_queries), 
            ('web_analytics_events', self.generate_web_analytics_events),
            ('ab_test_results', self.generate_ab_test_results),
            ('wishlist_items', self.generate_wishlist_items),
            ('cart_activities', self.generate_cart_activities),
            ('product_recommendations', self.generate_product_recommendations),
            ('page_views', self.generate_page_views)
        ]
        
        for entity_name, generator_func in entities:
            if entity_name in self.patterns:
                try:
                    self.logger.info(f"📊 Generating {entity_name}...")
                    data = generator_func(mode, dependencies)
                    results[entity_name] = data
                    self.logger.info(f"✅ Generated {len(data)} {entity_name}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to generate {entity_name}: {e}")
                    results[entity_name] = []
            else:
                self.logger.warning(f"⚠️ No configuration found for {entity_name}")
                results[entity_name] = []
                
        return results
    
    def generate_product_reviews(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate product reviews following configuration patterns."""
        
        config = self.patterns.get('product_reviews', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Get total records - adjust for mode
        mode_multipliers = {'demo': 0.1, 'fast': 0.2, 'full': 1.0}
        base_records = generation_rules.get('total_records', 2500)
        total_records = int(base_records * mode_multipliers.get(mode, 0.2))
        
        # Check dependencies
        customers = dependencies.get('customers', [])
        products = dependencies.get('products', [])
        orders = dependencies.get('orders', [])
        
        if not customers or not products:
            self.logger.warning("Missing customers or products for product reviews")
            return []
        
        reviews = []
        rating_distribution = data_patterns.get('rating_distribution', {})
        content_templates = data_patterns.get('content_templates', {})
        
        # Generate reviews based on verified/guest split
        verified_ratio = data_patterns.get('review_characteristics', {}).get('reviewer_types', {}).get('VERIFIED_BUYER', 0.85)
        verified_count = int(total_records * verified_ratio)
        guest_count = total_records - verified_count
        
        # Generate verified buyer reviews
        for i in range(verified_count):
            review = self._create_review_record(
                i + 1,
                customers,
                products,
                orders, 
                is_verified=True,
                rating_distribution=rating_distribution,
                content_templates=content_templates
            )
            reviews.append(review)
        
        # Generate guest reviews  
        for i in range(guest_count):
            review = self._create_review_record(
                verified_count + i + 1,
                customers,
                products,
                orders,
                is_verified=False,
                rating_distribution=rating_distribution,
                content_templates=content_templates
            )
            reviews.append(review)
            
        return reviews
    
    def _create_review_record(self, index: int, customers: List, products: List, 
                            orders: List, is_verified: bool, rating_distribution: Dict,
                            content_templates: Dict) -> Dict:
        """Create a single review record following patterns."""
        
        product = random.choice(products)
        
        # Select rating based on distribution
        if rating_distribution:
            rating_keys = list(rating_distribution.keys())
            rating_weights = list(rating_distribution.values())
            rating_key = random.choices(rating_keys, weights=rating_weights)[0]
            rating_value = int(rating_key.split('_')[0])
        else:
            rating_value = random.randint(1, 5)  # Fallback
        
        # Select content based on rating
        if rating_value >= 4:
            templates = content_templates.get('positive', ['Great product!'])
        elif rating_value == 3:
            templates = content_templates.get('neutral', ['Good product.'])
        else:
            templates = content_templates.get('negative', ['Not satisfied.'])
            
        review_text = random.choice(templates)
        
        review = {
            'review_id': f"REV_{index:08d}",
            'product_id': product['product_id'],
            'customer_id': random.choice(customers)['customer_id'] if is_verified else None,
            'order_id': random.choice(orders)['order_id'] if is_verified and orders else None,
            'rating': rating_value,
            'review_title': f"{rating_value} star review",
            'review_text': review_text,
            'is_verified_purchase': is_verified,
            'helpful_votes': random.randint(0, 25 if is_verified else 10),
            'review_date': self.faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
            'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
            'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return review
        
    def generate_email_marketing(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate email marketing campaigns following configuration patterns."""
        
        config = self.patterns.get('email_marketing', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.1, 'fast': 0.3, 'full': 1.0}
        base_records = generation_rules.get('total_records', 150)
        total_records = int(base_records * mode_multipliers.get(mode, 0.3))
        
        campaigns = []
        campaign_types = data_patterns.get('campaign_types', {})
        performance_benchmarks = data_patterns.get('performance_benchmarks', {})
        
        for i in range(total_records):
            # Select campaign type
            if campaign_types:
                types = list(campaign_types.keys())
                weights = list(campaign_types.values())
                campaign_type = random.choices(types, weights=weights)[0]
            else:
                campaign_type = random.choice(['NEWSLETTER', 'PROMOTIONAL', 'ABANDONED_CART'])
            
            # Get performance metrics
            open_rate = performance_benchmarks.get('email_open_rate', {}).get(campaign_type, 0.20)
            ctr = performance_benchmarks.get('click_through_rate', {}).get(campaign_type, 0.05)
            
            # Generate realistic metrics
            recipients = random.randint(1000, 10000)
            opens = max(0, int(recipients * random.normalvariate(open_rate, open_rate * 0.2)))
            clicks = max(0, int(opens * random.normalvariate(ctr / open_rate if open_rate > 0 else 0.05, ctr * 0.3)))
            
            campaign = {
                'campaign_id': f"EMAIL_{i + 1:06d}",
                'campaign_name': f"{campaign_type.replace('_', ' ').title()} Campaign {i + 1}",
                'campaign_type': campaign_type,
                'subject_line': f"Subject for {campaign_type.replace('_', ' ').lower()}",
                'sent_date': self.faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                'recipients_count': recipients,
                'delivered_count': max(0, recipients - random.randint(0, int(recipients * 0.02))),
                'opens_count': opens,
                'clicks_count': clicks,
                'unsubscribes_count': random.randint(0, int(recipients * 0.005)),
                'open_rate': round(opens / recipients if recipients > 0 else 0, 4),
                'click_through_rate': round(clicks / opens if opens > 0 else 0, 4),
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            campaigns.append(campaign)
            
        return campaigns
    
    def generate_search_queries(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate search queries following configuration patterns."""
        
        config = self.patterns.get('search_queries', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.1, 'fast': 0.2, 'full': 1.0}
        base_records = generation_rules.get('total_records', 12000)
        total_records = int(base_records * mode_multipliers.get(mode, 0.2))
        
        sessions = dependencies.get('web_sessions', [])
        if not sessions:
            self.logger.warning("No sessions available for search queries")
            return []
        
        queries = []
        search_types = data_patterns.get('search_types', {})
        popular_terms = data_patterns.get('popular_search_terms', {})
        
        # Collect all search terms
        all_terms = []
        for category, terms in popular_terms.items():
            all_terms.extend(terms)
        if not all_terms:
            all_terms = ['laptop', 'phone', 'shoes', 'shirt', 'book']  # Fallback
        
        for i in range(total_records):
            session = random.choice(sessions)
            
            # Select search type
            if search_types:
                types = list(search_types.keys())
                weights = list(search_types.values())
                search_type = random.choices(types, weights=weights)[0]
            else:
                search_type = 'PRODUCT_NAME'
            
            # Generate search query based on type
            if search_type == 'BRAND':
                search_query = random.choice(['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony'])
            else:
                search_query = random.choice(all_terms)
            
            # Add occasional typos
            if random.random() < 0.1:
                search_query = search_query[:-1] + random.choice('abcdefghijklmnopqrstuvwxyz')
            
            query = {
                'query_id': f"SEARCH_{i + 1:08d}",
                'session_id': session['session_id'],
                'customer_id': session.get('customer_id'),
                'search_query': search_query,
                'search_type': search_type,
                'results_count': random.choice([0] + list(range(1, 101))),
                'clicked_result': random.random() < 0.65,
                'search_timestamp': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            queries.append(query)
            
        return queries
    
    def generate_web_analytics_events(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate web analytics events following configuration patterns."""
        
        config = self.patterns.get('web_analytics_events', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.05, 'fast': 0.1, 'full': 1.0}
        base_records = generation_rules.get('total_records', 75000)
        total_records = int(base_records * mode_multipliers.get(mode, 0.1))
        
        sessions = dependencies.get('web_sessions', [])
        products = dependencies.get('products', [])
        
        if not sessions:
            self.logger.warning("No sessions available for web analytics events")
            return []
        
        events = []
        event_types = data_patterns.get('event_types', {})
        
        for i in range(total_records):
            session = random.choice(sessions)
            product = random.choice(products) if products else None
            
            # Select event type
            if event_types:
                types = list(event_types.keys())
                weights = list(event_types.values())
                event_type = random.choices(types, weights=weights)[0]
            else:
                event_type = random.choice(['PAGE_VIEW', 'PRODUCT_VIEW', 'ADD_TO_CART'])
            
            event = {
                'event_id': f"EVENT_{i + 1:08d}",
                'session_id': session['session_id'],
                'customer_id': session.get('customer_id'),
                'event_type': event_type,
                'product_id': product['product_id'] if product and event_type in ['PRODUCT_VIEW', 'ADD_TO_CART'] else None,
                'page_url': f"/{'product' if event_type == 'PRODUCT_VIEW' else 'page'}/{random.randint(1, 1000)}",
                'event_timestamp': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'event_properties': '{}',  # JSON string - could be enhanced
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            events.append(event)
            
        return events
    
    def generate_ab_test_results(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate A/B test results following configuration patterns."""
        
        config = self.patterns.get('ab_test_results', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Scale for mode  
        mode_multipliers = {'demo': 0.2, 'fast': 0.4, 'full': 1.0}
        base_records = generation_rules.get('total_records', 25)
        total_records = int(base_records * mode_multipliers.get(mode, 0.4))
        
        tests = []
        test_types = data_patterns.get('test_types', {})
        test_outcomes = data_patterns.get('test_outcomes', {})
        test_areas = data_patterns.get('test_areas', [])
        
        for i in range(total_records):
            # Select test type
            if test_types:
                types = list(test_types.keys())
                weights = list(test_types.values())
                test_type = random.choices(types, weights=weights)[0]
            else:
                test_type = 'LAYOUT'
            
            # Select outcome
            if test_outcomes:
                outcomes = list(test_outcomes.keys())
                outcome_weights = list(test_outcomes.values())
                outcome = random.choices(outcomes, weights=outcome_weights)[0]
            else:
                outcome = random.choice(['VARIANT_A_WINS', 'VARIANT_B_WINS', 'NO_SIGNIFICANT_DIFF'])
            
            # Select test area
            test_area = random.choice(test_areas) if test_areas else {'test_area': 'GENERAL', 'description': 'General testing'}
            
            # Generate performance metrics
            control_visitors = random.randint(1000, 10000)
            variant_visitors = random.randint(1000, 10000)
            
            if outcome == 'VARIANT_B_WINS':
                control_conversion = random.uniform(0.02, 0.10)
                variant_conversion = control_conversion * random.uniform(1.05, 1.30)
            elif outcome == 'VARIANT_A_WINS':
                variant_conversion = random.uniform(0.02, 0.10)
                control_conversion = variant_conversion * random.uniform(1.05, 1.20)
            else:  # NO_SIGNIFICANT_DIFF
                base_conversion = random.uniform(0.02, 0.10)
                control_conversion = base_conversion * random.uniform(0.98, 1.02)
                variant_conversion = base_conversion * random.uniform(0.98, 1.02)
            
            test = {
                'test_id': f"TEST_{i + 1:06d}",
                'test_name': f"{test_type} Test {i + 1}",
                'test_type': test_type,
                'test_area': test_area.get('test_area', 'GENERAL'),
                'start_date': self.faker.date_between(start_date='-6m', end_date='-1m').strftime('%Y-%m-%d'),
                'end_date': self.faker.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d'),
                'control_visitors': control_visitors,
                'variant_visitors': variant_visitors,
                'control_conversions': int(control_visitors * control_conversion),
                'variant_conversions': int(variant_visitors * variant_conversion),
                'control_conversion_rate': round(control_conversion, 4),
                'variant_conversion_rate': round(variant_conversion, 4),
                'statistical_significance': random.random() < 0.8,
                'winning_variant': outcome,
                'created_date': self.faker.date_time_between(start_date='-6m', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-6m', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            tests.append(test)
            
        return tests
    
    def generate_wishlist_items(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate wishlist items following configuration patterns."""
        
        config = self.patterns.get('wishlist_items', {})
        generation_rules = config.get('generation_rules', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.1, 'fast': 0.2, 'full': 1.0}
        base_records = generation_rules.get('total_records', 8000)
        total_records = int(base_records * mode_multipliers.get(mode, 0.2))
        
        customers = dependencies.get('customers', [])
        products = dependencies.get('products', [])
        
        if not customers or not products:
            self.logger.warning("Missing customers or products for wishlist items")
            return []
        
        wishlist_items = []
        
        for i in range(total_records):
            customer = random.choice(customers)
            product = random.choice(products)
            
            item = {
                'wishlist_item_id': f"WISH_{i + 1:08d}",
                'customer_id': customer['customer_id'],
                'product_id': product['product_id'],
                'added_date': self.faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                'is_public': random.random() < 0.15,
                'purchased_date': self.faker.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d') if random.random() < 0.25 else None,
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            wishlist_items.append(item)
            
        return wishlist_items
    
    def generate_cart_activities(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate cart activities following configuration patterns."""
        
        config = self.patterns.get('cart_activities', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.05, 'fast': 0.1, 'full': 1.0}
        base_records = generation_rules.get('total_records', 20000)
        total_records = int(base_records * mode_multipliers.get(mode, 0.1))
        
        sessions = dependencies.get('web_sessions', [])
        products = dependencies.get('products', [])
        
        if not sessions or not products:
            self.logger.warning("Missing sessions or products for cart activities")
            return []
        
        activities = []
        cart_actions = data_patterns.get('cart_actions', {})
        
        for i in range(total_records):
            session = random.choice(sessions)
            product = random.choice(products)
            
            # Select action
            if cart_actions:
                actions = list(cart_actions.keys())
                weights = list(cart_actions.values())
                action = random.choices(actions, weights=weights)[0]
            else:
                action = random.choice(['ADD_ITEM', 'REMOVE_ITEM', 'UPDATE_QUANTITY'])
            
            activity = {
                'activity_id': f"CART_{i + 1:08d}",
                'session_id': session['session_id'],
                'customer_id': session.get('customer_id'),
                'product_id': product['product_id'],
                'action_type': action,
                'quantity': random.randint(1, 3) if action in ['ADD_ITEM', 'UPDATE_QUANTITY'] else 0,
                'unit_price_eur': float(product.get('price_eur', 29.99)),
                'activity_timestamp': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            activities.append(activity)
            
        return activities
    
    def generate_product_recommendations(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate product recommendations following configuration patterns."""
        
        config = self.patterns.get('product_recommendations', {})
        generation_rules = config.get('generation_rules', {})
        
        # Scale for mode
        mode_multipliers = {'demo': 0.1, 'fast': 0.2, 'full': 1.0}
        base_records = generation_rules.get('total_records', 15000)
        total_records = int(base_records * mode_multipliers.get(mode, 0.2))
        
        products = dependencies.get('products', [])
        customers = dependencies.get('customers', [])
        
        if not products:
            self.logger.warning("Missing products for product recommendations")
            return []
        
        recommendations = []
        
        for i in range(total_records):
            source_product = random.choice(products)
            recommended_product = random.choice(products)
            
            # Avoid self-recommendation
            while recommended_product['product_id'] == source_product['product_id'] and len(products) > 1:
                recommended_product = random.choice(products)
            
            recommendation = {
                'recommendation_id': f"REC_{i + 1:08d}",
                'source_product_id': source_product['product_id'],
                'recommended_product_id': recommended_product['product_id'],
                'recommendation_type': random.choice(['SIMILAR_PRODUCTS', 'FREQUENTLY_BOUGHT_TOGETHER', 'CUSTOMERS_ALSO_VIEWED']),
                'confidence_score': round(random.uniform(0.4, 1.0), 3),
                'click_count': random.randint(0, 100),
                'purchase_count': random.randint(0, 25),
                'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            }
            recommendations.append(recommendation)
            
        return recommendations
    
    def generate_page_views(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate page views following configuration patterns."""
        
        config = self.patterns.get('page_views', {})
        generation_rules = config.get('generation_rules', {})
        data_patterns = config.get('data_patterns', {})
        
        # Get web sessions as dependency
        web_sessions = dependencies.get('web_sessions', [])
        
        if not web_sessions:
            self.logger.warning("Missing web_sessions for page views generation")
            return []
        
        # Page view patterns from configuration
        page_categories = data_patterns.get('page_categories', {
            'HOMEPAGE': 0.25, 'PRODUCT_LISTING': 0.30, 'PRODUCT_DETAIL': 0.20,
            'CART': 0.08, 'CHECKOUT': 0.05, 'ACCOUNT': 0.07, 'SEARCH': 0.05
        })
        
        conversion_funnel = data_patterns.get('conversion_funnel', {})
        pages_per_session_range = generation_rules.get('pages_per_session', [1, 8])
        
        page_views = []
        view_id = 1
        
        for session in web_sessions:
            # Determine number of pages per session
            pages_count = random.randint(pages_per_session_range[0], pages_per_session_range[1])
            
            # Start with homepage for most sessions
            current_page = 'HOMEPAGE' if random.random() < 0.6 else random.choices(
                list(page_categories.keys()), 
                weights=list(page_categories.values())
            )[0]
            
            for page_num in range(pages_count):
                page_view = {
                    'page_view_id': f"PV_{view_id:08d}",
                    'session_id': session['session_id'],
                    'customer_id': session.get('customer_id'),
                    'page_url': f"/{current_page.lower()}.html",
                    'page_title': current_page.replace('_', ' ').title(),
                    'page_category': current_page,
                    'view_duration_seconds': random.randint(10, 300),
                    'page_load_time_ms': random.randint(800, 3500),
                    'scroll_depth_percent': random.randint(10, 100),
                    'page_sequence': page_num + 1,
                    'is_entrance_page': page_num == 0,
                    'is_exit_page': page_num == pages_count - 1,
                    'referrer_page': None if page_num == 0 else f"PV_{view_id-1:08d}",
                    'device_type': session.get('device_type', 'desktop'),
                    'browser': session.get('browser', 'Chrome'),
                    'timestamp': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                    'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
                }
                
                page_views.append(page_view)
                view_id += 1
                
                # Determine next page based on conversion funnel
                if page_num < pages_count - 1 and current_page in conversion_funnel:
                    funnel_data = conversion_funnel[current_page]
                    next_pages = funnel_data.get('next_pages', [current_page])
                    weights = funnel_data.get('weights', [1.0] * len(next_pages))
                    current_page = random.choices(next_pages, weights=weights)[0]
                elif page_num < pages_count - 1:
                    # Random next page if no funnel defined
                    current_page = random.choices(
                        list(page_categories.keys()),
                        weights=list(page_categories.values())
                    )[0]
        
        return page_views
