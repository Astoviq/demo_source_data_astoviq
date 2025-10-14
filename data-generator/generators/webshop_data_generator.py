"""
Webshop Data Generator
======================

Generates webshop data that is directly related to the operational database.
This creates realistic digital customer journeys that lead to actual orders.
"""

from generators.base_generator import BaseGenerator

class WebshopDataGenerator(BaseGenerator):
    """Generates webshop analytics data related to operational transactions."""
    
    def __init__(self, config, db_connector):
        """Initialize the webshop data generator."""
        super().__init__(config, db_connector)
        
        # Switch to webshop database for insertions
        self.webshop_db_name = "eurostyle_webshop"
    
    def generate_web_sessions_and_page_views(self) -> bool:
        """Generate web sessions and page views that relate to actual orders."""
        self.logger.info("🌐 Generating web sessions and page views...")
        
        from datetime import datetime, date, timedelta
        from faker import Faker
        import random
        import pandas as pd
        
        fake = Faker()
        
        # Load operational data to create realistic connections
        self.logger.info("Loading operational data for relationships...")
        
        # Get customers from operational DB
        customers_query = "SELECT customer_id, country_code, registration_date, total_orders FROM eurostyle_operational.customers WHERE customer_status = 'active'"
        customers_result = self.db_connector.client.execute(customers_query, with_column_types=True)
        customers_df = pd.DataFrame([dict(zip([col[0] for col in customers_result[1]], row)) for row in customers_result[0]])
        
        # Get products from operational DB
        products_query = "SELECT product_id, category_l1, category_l2, category_l3, price_eur, color_primary FROM eurostyle_operational.products WHERE is_active = true"
        products_result = self.db_connector.client.execute(products_query, with_column_types=True)
        products_df = pd.DataFrame([dict(zip([col[0] for col in products_result[1]], row)) for row in products_result[0]])
        
        # Get orders to create conversion sessions
        orders_query = "SELECT order_id, customer_id, order_datetime, total_amount_eur, order_channel FROM eurostyle_operational.orders ORDER BY order_datetime"
        orders_result = self.db_connector.client.execute(orders_query, with_column_types=True)
        orders_df = pd.DataFrame([dict(zip([col[0] for col in orders_result[1]], row)) for row in orders_result[0]])
        
        self.logger.info(f"Loaded {len(customers_df)} customers, {len(products_df)} products, {len(orders_df)} orders")
        
        sessions_data = []
        page_views_data = []
        cart_activities_data = []
        
        # Device and browser data for realistic sessions
        devices = [
            {"type": "desktop", "browsers": ["Chrome", "Firefox", "Safari", "Edge"], "os": ["Windows 10", "macOS", "Linux"]},
            {"type": "mobile", "browsers": ["Chrome Mobile", "Safari Mobile", "Samsung Internet"], "os": ["Android", "iOS"]},
            {"type": "tablet", "browsers": ["Safari", "Chrome", "Samsung Internet"], "os": ["iOS", "Android"]}
        ]
        
        utm_sources = ["google", "facebook", "instagram", "email", "direct", "bing", "pinterest"]
        utm_mediums = ["organic", "cpc", "email", "social", "referral", "display"]
        
        country_sites = {
            "NL": "nl.eurostyle.com",
            "BE": "be.eurostyle.com", 
            "DE": "de.eurostyle.com",
            "FR": "fr.eurostyle.com",
            "LU": "lu.eurostyle.com"
        }
        
        session_id_counter = 1
        page_view_id_counter = 1
        cart_activity_id_counter = 1
        
        # Strategy 1: Generate sessions that lead to actual orders (conversion sessions)
        self.logger.info("Generating conversion sessions (sessions that led to orders)...")
        
        for _, order in orders_df.iterrows():
            # Each order should have 1-3 sessions leading up to it
            num_sessions = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            
            # Find the customer for this order (with error handling)
            customer_matches = customers_df[customers_df['customer_id'] == order['customer_id']]
            if len(customer_matches) == 0:
                # Skip this order if customer not found in active customers
                continue
            customer = customer_matches.iloc[0]
            order_time = order['order_datetime']
            
            for session_num in range(num_sessions):
                # Sessions occur 0-7 days before the order
                days_before = random.randint(0, min(7, session_num + 1))
                hours_before = random.randint(1, 48) if days_before == 0 else random.randint(0, 23)
                
                session_start = order_time - timedelta(days=days_before, hours=hours_before)
                
                # Device selection (mobile increases over time)
                if session_start.year >= 2023:
                    device_weights = [40, 50, 10]  # desktop, mobile, tablet
                else:
                    device_weights = [60, 35, 5]   # more desktop in earlier years
                
                device_info = random.choices(devices, weights=device_weights)[0]
                device_type = device_info["type"]
                browser = random.choice(device_info["browsers"])
                operating_system = random.choice(device_info["os"])
                
                # Session characteristics
                is_final_session = (session_num == num_sessions - 1)  # Last session before order
                
                if is_final_session:
                    # Final session - user completes purchase
                    session_duration = random.randint(15*60, 45*60)  # 15-45 minutes
                    page_views_count = random.randint(8, 25)
                    unique_products_viewed = random.randint(3, 8)
                    conversion_session = True
                    bounce_session = False
                else:
                    # Earlier session - browsing, comparison
                    session_duration = random.randint(3*60, 20*60)   # 3-20 minutes
                    page_views_count = random.randint(3, 15)
                    unique_products_viewed = random.randint(1, 5)
                    conversion_session = False
                    bounce_session = page_views_count == 1
                
                session_end = session_start + timedelta(seconds=session_duration)
                
                # Marketing attribution (more attribution for first session)
                utm_source = None
                utm_medium = None
                utm_campaign = None
                referrer_url = None
                
                if session_num == 0:  # First session in journey
                    if random.random() < 0.7:  # 70% have attribution
                        utm_source = random.choice(utm_sources)
                        utm_medium = random.choice(utm_mediums)
                        if utm_source in ["google", "facebook", "instagram"]:
                            utm_campaign = f"{utm_source}_{random.choice(['spring', 'summer', 'fall', 'winter'])}_2024"
                
                # Landing and exit pages
                landing_pages = [
                    "/", "/women", "/men", "/new-arrivals", "/sale", 
                    f"/product/{random.choice(products_df['product_id'])}"
                ]
                landing_page = random.choice(landing_pages)
                
                exit_pages = [
                    "/checkout/complete" if is_final_session else "/cart",
                    "/product-detail", "/category", "/search-results"
                ]
                exit_page = random.choice(exit_pages)
                
                # Generate session record
                session_record = {
                    "session_id": f"SES_{session_id_counter:08d}",
                    "customer_id": customer['customer_id'],
                    "country_code": customer['country_code'],
                    "device_type": device_type,
                    "browser": browser,
                    "operating_system": operating_system,
                    "session_start": session_start,
                    "session_end": session_end,
                    "session_duration_seconds": session_duration,
                    "page_views": page_views_count,
                    "unique_products_viewed": unique_products_viewed,
                    "bounce_session": bounce_session,
                    "conversion_session": conversion_session,
                    "utm_source": utm_source,
                    "utm_medium": utm_medium,
                    "utm_campaign": utm_campaign,
                    "referrer_url": referrer_url,
                    "landing_page": landing_page,
                    "exit_page": exit_page,
                    "ip_address": fake.ipv4(),
                    "user_agent": f"{browser}/1.0 ({operating_system})",
                    "created_at": session_start,
                    "updated_at": session_start
                }
                
                sessions_data.append(session_record)
                
                # Generate page views for this session
                session_products = products_df.sample(n=min(unique_products_viewed, len(products_df)))
                current_time = session_start
                
                for page_num in range(page_views_count):
                    # Determine page type and content
                    if page_num == 0:
                        page_type = "homepage" if landing_page == "/" else "category"
                        page_url = landing_page
                        page_title = f"EuroStyle Fashion - {customer['country_code']}"
                        product_id = None
                        category_l1 = None
                        category_l2 = None
                    elif page_num < page_views_count - 2 and random.random() < 0.6:
                        # Product pages
                        page_type = "product"
                        product = session_products.iloc[page_num % len(session_products)]
                        product_id = product['product_id']
                        page_url = f"/product/{product_id}"
                        page_title = f"{product['category_l3']} - EuroStyle"
                        category_l1 = product['category_l1']
                        category_l2 = product['category_l2']
                    elif is_final_session and page_num >= page_views_count - 2:
                        # Checkout pages for converting sessions
                        page_type = "checkout"
                        page_url = "/checkout" if page_num == page_views_count - 2 else "/checkout/complete"
                        page_title = "Checkout - EuroStyle"
                        product_id = None
                        category_l1 = None
                        category_l2 = None
                    else:
                        # Category or other pages
                        page_type = random.choice(["category", "search", "account"])
                        page_url = f"/{page_type}"
                        page_title = f"{page_type.title()} - EuroStyle"
                        product_id = None
                        category_l1 = random.choice(products_df['category_l1'].unique()) if page_type == "category" else None
                        category_l2 = None
                    
                    # Page engagement metrics
                    time_on_page = random.randint(10, 300)  # 10 seconds to 5 minutes
                    scroll_depth = random.randint(20, 100)
                    click_events = random.randint(0, 5)
                    
                    page_view_record = {
                        "page_view_id": f"PV_{page_view_id_counter:08d}",
                        "session_id": session_record["session_id"],
                        "customer_id": customer['customer_id'],
                        "country_code": customer['country_code'],
                        "page_type": page_type,
                        "page_url": page_url,
                        "page_title": page_title,
                        "product_id": product_id,
                        "category_l1": category_l1,
                        "category_l2": category_l2,
                        "view_timestamp": current_time,
                        "time_on_page_seconds": time_on_page,
                        "scroll_depth_percent": scroll_depth,
                        "click_events": click_events,
                        "is_mobile": device_type == "mobile",
                        "referrer_page": page_views_data[-1]["page_url"] if page_views_data else None,
                        "exit_page": page_num == page_views_count - 1,
                        "created_at": current_time
                    }
                    
                    page_views_data.append(page_view_record)
                    page_view_id_counter += 1
                    
                    # Advance time
                    current_time += timedelta(seconds=time_on_page + random.randint(5, 60))
                
                session_id_counter += 1
                
                # Progress logging
                if len(sessions_data) % 1000 == 0:
                    self.logger.info(f"Generated {len(sessions_data)} sessions with {len(page_views_data)} page views...")
        
        # Strategy 2: Generate browsing sessions that don't convert (majority of sessions)
        self.logger.info("Generating non-conversion sessions (browsing only)...")
        
        # Generate 3-5x more non-converting sessions
        num_non_converting = len(sessions_data) * random.randint(3, 5)
        
        # Time range for non-converting sessions
        time_config = self.config.get('time_range', {})
        start_date = datetime.strptime(time_config.get('sales_start_date', '2020-01-01'), '%Y-%m-%d')
        end_date = datetime.strptime(time_config.get('sales_end_date', '2025-10-10'), '%Y-%m-%d')
        
        for _ in range(min(num_non_converting, 100000)):  # Cap for performance
            # Random customer (mix of registered and anonymous)
            customer_id = None
            country_code = random.choice(["NL", "BE", "DE", "FR", "LU"])
            
            if random.random() < 0.6:  # 60% are registered users
                customer = customers_df.sample(1).iloc[0]
                customer_id = customer['customer_id']
                country_code = customer['country_code']
            
            # Random session time
            session_start = fake.date_time_between(start_date=start_date, end_date=end_date)
            session_duration = random.randint(30, 15*60)  # 30 seconds to 15 minutes
            session_end = session_start + timedelta(seconds=session_duration)
            
            # Device info
            device_info = random.choices(devices, weights=[45, 45, 10])[0]
            device_type = device_info["type"]
            browser = random.choice(device_info["browsers"])
            operating_system = random.choice(device_info["os"])
            
            # Browsing behavior (non-converting)
            page_views_count = random.choices([1, 2, 3, 4, 5, 6], weights=[40, 25, 15, 10, 6, 4])[0]
            unique_products_viewed = min(page_views_count, random.randint(0, 3))
            bounce_session = page_views_count == 1
            
            session_record = {
                "session_id": f"SES_{session_id_counter:08d}",
                "customer_id": customer_id,
                "country_code": country_code,
                "device_type": device_type,
                "browser": browser,
                "operating_system": operating_system,
                "session_start": session_start,
                "session_end": session_end,
                "session_duration_seconds": session_duration,
                "page_views": page_views_count,
                "unique_products_viewed": unique_products_viewed,
                "bounce_session": bounce_session,
                "conversion_session": False,
                "utm_source": random.choice(utm_sources) if random.random() < 0.3 else None,
                "utm_medium": random.choice(utm_mediums) if random.random() < 0.3 else None,
                "utm_campaign": None,
                "referrer_url": None,
                "landing_page": random.choice(["/", "/women", "/men", "/sale"]),
                "exit_page": random.choice(["/category", "/product-detail", "/search"]),
                "ip_address": fake.ipv4(),
                "user_agent": f"{browser}/1.0 ({operating_system})",
                "created_at": session_start,
                "updated_at": session_start
            }
            
            sessions_data.append(session_record)
            session_id_counter += 1
            
            # Basic page views for non-converting sessions
            # (We'll generate these later if needed to keep initial dataset manageable)
        
        # Insert sessions data
        self.logger.info(f"Inserting {len(sessions_data)} web sessions...")
        success_sessions = self._insert_webshop_data("web_sessions", sessions_data)
        
        # Insert page views data
        self.logger.info(f"Inserting {len(page_views_data)} page views...")
        success_page_views = self._insert_webshop_data("page_views", page_views_data)
        
        if success_sessions and success_page_views:
            self.logger.info(f"✅ Generated {len(sessions_data)} sessions and {len(page_views_data)} page views")
            return True
        else:
            self.logger.error("❌ Failed to generate web sessions and page views")
            return False
    
    def _insert_webshop_data(self, table_name: str, data_list: list) -> bool:
        """Insert data into webshop database table."""
        try:
            # Convert to iterator for batch processing
            data_iterator = iter(data_list)
            
            # Use existing batch processing but specify webshop database
            success = self.process_in_batches(f"{self.webshop_db_name}.{table_name}", data_iterator, len(data_list))
            return success
        except Exception as e:
            self.logger.error(f"Failed to insert data into {table_name}: {e}")
            return False
    
    def generate_table_data(self, table_name: str) -> bool:
        """Generate data for a specific webshop table."""
        if table_name == "web_sessions":
            return self.generate_web_sessions_and_page_views()
        elif hasattr(self, f"generate_{table_name}"):
            return getattr(self, f"generate_{table_name}")()
        else:
            self.logger.error(f"❌ Unknown webshop table: {table_name}")
            return False