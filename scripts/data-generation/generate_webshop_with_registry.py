#!/usr/bin/env python3
"""
EuroStyle Webshop Data Generator with Registry Integration
=========================================================

Generates webshop data using the data registry to ensure:
- Realistic conversion rates (2.5%)
- Proper session-to-order mappings
- Cross-system referential integrity

This replaces the existing webshop generator to fix the conversion flow issues.
"""

import csv
import gzip
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))
from data_registry import DataRegistry

class WebshopDataGenerator:
    """Generates webshop data with proper cross-system integration."""
    
    def __init__(self):
        """Initialize the webshop data generator."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.countries = ['NL', 'BE', 'DE', 'FR', 'LU']
        self.device_types = ['desktop', 'mobile', 'tablet']
        self.browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        self.sizes = ['XS', 'S', 'M', 'L', 'XL', '32', '34', '36', '38', '40', '42']
        self.colors = ['Black', 'White', 'Navy', 'Grey', 'Red', 'Blue', 'Green', 'Pink', 'Brown']
        
        # Output directory
        self.output_dir = Path("../generated_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.registry = None
        self.session_mappings = {}
        self.customers = {}
        self.products = {}
        
    def load_registry(self) -> bool:
        """Load the data registry with cross-system mappings."""
        self.logger.info("Loading data registry...")
        
        try:
            self.registry = DataRegistry("../data-generator/generated_data")
            if not self.registry.load_operational_data():
                self.logger.error("Failed to load operational data into registry")
                return False
                
            # Get the session mappings
            self.session_mappings = self.registry.get_session_mappings()
            self.customers = self.registry.customers
            self.products = self.registry.products
            
            self.logger.info(f"Loaded {len(self.session_mappings)} session mappings")
            self.logger.info(f"Converting sessions: {len(self.registry.get_converting_sessions())}")
            self.logger.info(f"Non-converting sessions: {len(self.registry.get_non_converting_sessions())}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading registry: {str(e)}")
            return False
    
    def generate_web_sessions(self) -> bool:
        """Generate web sessions using registry data."""
        self.logger.info("Generating web sessions from registry...")
        
        try:
            sessions = []
            
            for session_id, mapping in self.session_mappings.items():
                # Generate realistic session data
                session_start = datetime.strptime(mapping['session_date'], '%Y-%m-%d')
                session_duration = random.randint(30, 3600)  # 30 seconds to 1 hour
                session_end = session_start + timedelta(seconds=session_duration)
                
                # Device and browser distribution
                device_weights = [0.45, 0.35, 0.20]  # desktop, mobile, tablet
                device_type = random.choices(self.device_types, weights=device_weights)[0]
                
                browser_weights = [0.65, 0.15, 0.12, 0.08]  # Chrome, Firefox, Safari, Edge
                browser = random.choices(self.browsers, weights=browser_weights)[0]
                
                # Generate session characteristics
                page_views = random.randint(1, 20) if mapping['conversion_type'] == 'browse' else random.randint(3, 30)
                bounce_rate = random.random() < 0.4 if mapping['conversion_type'] == 'browse' else False
                
                # Traffic source based on conversion
                if mapping['conversion_type'] == 'purchase':
                    traffic_sources = ['organic_search', 'paid_search', 'direct', 'social_media', 'email']
                    traffic_weights = [0.35, 0.25, 0.20, 0.15, 0.05]
                else:
                    traffic_sources = ['organic_search', 'social_media', 'direct', 'paid_search', 'referral']
                    traffic_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
                
                traffic_source = random.choices(traffic_sources, weights=traffic_weights)[0]
                
                session = {
                    'session_id': session_id,
                    'customer_id': mapping.get('customer_id', ''),
                    'country_code': mapping['country_code'],
                    'session_start': session_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'session_end': session_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'session_duration_seconds': session_duration,
                    'device_type': device_type,
                    'browser': browser,
                    'operating_system': self._get_os_for_device(device_type),
                    'traffic_source': traffic_source,
                    'landing_page': self._get_landing_page(traffic_source),
                    'page_views': page_views,
                    'unique_page_views': max(1, int(page_views * random.uniform(0.7, 1.0))),
                    'bounce_session': bounce_rate,
                    'time_on_page_avg_seconds': random.randint(45, 300),
                    'converted': mapping['conversion_type'] == 'purchase',
                    'conversion_value_eur': mapping.get('order_value_eur', 0),
                    'exit_page': self._get_exit_page(mapping['conversion_type']),
                    'referrer_url': self._get_referrer(traffic_source),
                    'utm_source': traffic_source if traffic_source in ['paid_search', 'email', 'social_media'] else '',
                    'utm_medium': self._get_utm_medium(traffic_source),
                    'utm_campaign': self._get_utm_campaign(traffic_source, session_start),
                    'session_date': mapping['session_date'],
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                sessions.append(session)
            
            # Save web sessions (compressed)
            output_file = self.output_dir / "eurostyle_webshop.web_sessions.csv.gz"
            with gzip.open(output_file, 'wt', newline='', encoding='utf-8') as f:
                if sessions:
                    writer = csv.DictWriter(f, fieldnames=sessions[0].keys())
                    writer.writeheader()
                    writer.writerows(sessions)
            
            self.logger.info(f"Generated {len(sessions)} web sessions")
            self.logger.info(f"Saved to: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating web sessions: {str(e)}")
            return False
    
    def generate_page_views(self) -> bool:
        """Generate page views for sessions."""
        self.logger.info("Generating page views...")
        
        try:
            page_views = []
            page_counter = 1
            
            # Common page types
            page_types = {
                'home': 0.15,
                'category': 0.25, 
                'product': 0.35,
                'cart': 0.08,
                'checkout': 0.05,
                'account': 0.07,
                'search': 0.05
            }
            
            for session_id, mapping in self.session_mappings.items():
                # Get session characteristics
                converting = mapping['conversion_type'] == 'purchase'
                session_date = datetime.strptime(mapping['session_date'], '%Y-%m-%d')
                
                # Determine number of page views for this session
                if converting:
                    num_pages = random.randint(5, 25)  # Converters view more pages
                else:
                    num_pages = random.randint(1, 12)   # Browsers view fewer pages
                
                session_pages = []
                current_time = session_date
                
                for page_num in range(num_pages):
                    # Choose page type based on user journey
                    if page_num == 0:
                        # Landing page
                        page_type = random.choices(['home', 'category', 'product'], weights=[0.4, 0.4, 0.2])[0]
                    elif page_num < num_pages - 1:
                        # Middle pages
                        page_type = random.choices(list(page_types.keys()), weights=list(page_types.values()))[0]
                    else:
                        # Last page for converters vs non-converters
                        if converting:
                            page_type = 'checkout'
                        else:
                            page_type = random.choices(['category', 'product', 'home'], weights=[0.4, 0.4, 0.2])[0]
                    
                    # Generate page view details
                    time_on_page = random.randint(15, 300)  # 15 seconds to 5 minutes
                    current_time += timedelta(seconds=random.randint(1, 10))
                    
                    page_view = {
                        'page_view_id': f"PV_{page_counter:012d}",
                        'session_id': session_id,
                        'customer_id': mapping.get('customer_id', ''),
                        'country_code': mapping['country_code'],
                        'page_view_timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'page_type': page_type,
                        'page_url': self._generate_page_url(page_type),
                        'page_title': self._generate_page_title(page_type),
                        'page_position': page_num + 1,
                        'time_on_page_seconds': time_on_page,
                        'scroll_depth_percentage': random.randint(20, 100),
                        'exit_page': page_num == num_pages - 1,
                        'product_id': random.choice(list(self.products.keys())) if page_type == 'product' and self.products else '',
                        'referrer_page': session_pages[-1]['page_url'] if session_pages else '',
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    session_pages.append(page_view)
                    page_views.append(page_view)
                    page_counter += 1
                    current_time += timedelta(seconds=time_on_page)
            
            # Save page views (compressed)
            output_file = self.output_dir / "eurostyle_webshop.page_views.csv.gz"
            with gzip.open(output_file, 'wt', newline='', encoding='utf-8') as f:
                if page_views:
                    writer = csv.DictWriter(f, fieldnames=page_views[0].keys())
                    writer.writeheader()
                    writer.writerows(page_views)
            
            self.logger.info(f"Generated {len(page_views)} page views")
            self.logger.info(f"Saved to: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating page views: {str(e)}")
            return False
    
    def _get_os_for_device(self, device_type: str) -> str:
        """Get operating system based on device type."""
        if device_type == 'mobile':
            return random.choices(['iOS', 'Android'], weights=[0.4, 0.6])[0]
        elif device_type == 'tablet':
            return random.choices(['iOS', 'Android', 'Windows'], weights=[0.5, 0.4, 0.1])[0]
        else:  # desktop
            return random.choices(['Windows', 'macOS', 'Linux'], weights=[0.7, 0.25, 0.05])[0]
    
    def _get_landing_page(self, traffic_source: str) -> str:
        """Get landing page based on traffic source."""
        if traffic_source == 'organic_search':
            return random.choice(['/products/', '/categories/', '/'])
        elif traffic_source == 'paid_search':
            return random.choice(['/products/', '/categories/', '/sale'])
        elif traffic_source == 'social_media':
            return random.choice(['/new-arrivals', '/trending', '/'])
        elif traffic_source == 'email':
            return random.choice(['/sale', '/new-arrivals', '/'])
        else:
            return '/'
    
    def _get_exit_page(self, conversion_type: str) -> str:
        """Get exit page based on conversion type."""
        if conversion_type == 'purchase':
            return '/checkout/confirmation'
        else:
            return random.choice(['/', '/products/', '/categories/', '/cart'])
    
    def _get_referrer(self, traffic_source: str) -> str:
        """Get referrer URL based on traffic source."""
        if traffic_source == 'organic_search':
            return random.choice(['google.com', 'bing.com', 'duckduckgo.com'])
        elif traffic_source == 'social_media':
            return random.choice(['facebook.com', 'instagram.com', 'twitter.com', 'pinterest.com'])
        elif traffic_source == 'referral':
            return random.choice(['fashionblog.com', 'styletips.eu', 'trendwatcher.nl'])
        else:
            return ''
    
    def _get_utm_medium(self, traffic_source: str) -> str:
        """Get UTM medium based on traffic source."""
        mapping = {
            'paid_search': 'cpc',
            'social_media': 'social',
            'email': 'email',
            'referral': 'referral'
        }
        return mapping.get(traffic_source, '')
    
    def _get_utm_campaign(self, traffic_source: str, session_date: datetime) -> str:
        """Get UTM campaign based on traffic source and date."""
        if traffic_source == 'paid_search':
            return f"search_{session_date.strftime('%Y-%m')}"
        elif traffic_source == 'social_media':
            return f"social_{session_date.strftime('%Y-%m')}"
        elif traffic_source == 'email':
            return f"newsletter_{session_date.strftime('%Y-%m')}"
        return ''
    
    def _generate_page_url(self, page_type: str) -> str:
        """Generate realistic page URL based on page type."""
        urls = {
            'home': '/',
            'category': f'/categories/{random.choice(["women", "men", "kids", "accessories"])}',
            'product': f'/products/item-{random.randint(1000, 9999)}',
            'cart': '/cart',
            'checkout': '/checkout',
            'account': '/account',
            'search': f'/search?q={random.choice(["dress", "shoes", "jacket", "jeans"])}'
        }
        return urls.get(page_type, '/')
    
    def _generate_page_title(self, page_type: str) -> str:
        """Generate page title based on page type."""
        titles = {
            'home': 'EuroStyle Fashion - Sustainable European Fashion',
            'category': f'{random.choice(["Women", "Men", "Kids"])} Fashion Collection',
            'product': f'{random.choice(["Elegant", "Casual", "Premium"])} {random.choice(["Dress", "Jacket", "Shirt"])}',
            'cart': 'Shopping Cart - EuroStyle Fashion',
            'checkout': 'Checkout - EuroStyle Fashion',
            'account': 'My Account - EuroStyle Fashion',
            'search': 'Search Results - EuroStyle Fashion'
        }
        return titles.get(page_type, 'EuroStyle Fashion')

def main():
    """Main function to generate webshop data."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🌐 EuroStyle Webshop Data Generator with Registry Integration")
    logger.info("=" * 65)
    
    generator = WebshopDataGenerator()
    
    try:
        # Load registry data
        if not generator.load_registry():
            logger.error("❌ Failed to load registry data")
            return False
        
        # Generate web sessions
        if not generator.generate_web_sessions():
            logger.error("❌ Failed to generate web sessions")
            return False
        
        # Generate page views
        if not generator.generate_page_views():
            logger.error("❌ Failed to generate page views")
            return False
        
        logger.info("")
        logger.info("🎉 Webshop data generation completed successfully!")
        logger.info(f"Generated realistic webshop data with {len(generator.session_mappings)} sessions")
        logger.info(f"Conversion rate: 2.5% (realistic for fashion e-commerce)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Webshop data generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)