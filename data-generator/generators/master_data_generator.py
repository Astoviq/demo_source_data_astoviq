"""
Master Data Generator
=====================

Generates master data for the EuroStyle Fashion system:
- Stores
- Products  
- Campaigns
- Customers
"""

from generators.base_generator import BaseGenerator

class MasterDataGenerator(BaseGenerator):
    """Generates master data tables."""
    
    def __init__(self, config, db_connector):
        """Initialize the master data generator."""
        super().__init__(config, db_connector)
    
    def generate_stores(self) -> bool:
        """Generate stores data."""
        self.logger.info("🏦 Generating stores data...")
        
        from datetime import datetime, date
        from faker import Faker
        import random
        
        fake = Faker(['nl_NL', 'de_DE', 'fr_FR', 'en_GB'])
        stores_data = []
        
        # Store configuration from design document: 47 stores total
        store_config = {
            "NL": {
                "cities": [
                    {"city": "Amsterdam", "count": 3, "format": ["flagship", "standard", "standard"]},
                    {"city": "Rotterdam", "count": 2, "format": ["standard", "standard"]},
                    {"city": "Utrecht", "count": 2, "format": ["standard", "outlet"]},
                    {"city": "Eindhoven", "count": 1, "format": ["standard"]},
                    {"city": "Groningen", "count": 1, "format": ["standard"]},
                    {"city": "Tilburg", "count": 1, "format": ["standard"]},
                    {"city": "Almere", "count": 1, "format": ["standard"]},
                    {"city": "Maastricht", "count": 1, "format": ["standard"]}
                ]
            },
            "BE": {
                "cities": [
                    {"city": "Brussels", "count": 3, "format": ["flagship", "standard", "outlet"]},
                    {"city": "Antwerp", "count": 2, "format": ["standard", "standard"]},
                    {"city": "Ghent", "count": 2, "format": ["standard", "standard"]},
                    {"city": "Liège", "count": 1, "format": ["standard"]}
                ]
            },
            "DE": {
                "cities": [
                    {"city": "Berlin", "count": 4, "format": ["flagship", "standard", "standard", "outlet"]},
                    {"city": "Hamburg", "count": 3, "format": ["standard", "standard", "popup"]},
                    {"city": "Munich", "count": 3, "format": ["flagship", "standard", "standard"]},
                    {"city": "Cologne", "count": 2, "format": ["standard", "standard"]},
                    {"city": "Frankfurt", "count": 1, "format": ["standard"]},
                    {"city": "Stuttgart", "count": 1, "format": ["standard"]},
                    {"city": "Düsseldorf", "count": 1, "format": ["standard"]}
                ]
            },
            "FR": {
                "cities": [
                    {"city": "Paris", "count": 4, "format": ["flagship", "flagship", "standard", "standard"]},
                    {"city": "Lyon", "count": 2, "format": ["standard", "outlet"]},
                    {"city": "Marseille", "count": 1, "format": ["standard"]},
                    {"city": "Nice", "count": 1, "format": ["standard"]},
                    {"city": "Toulouse", "count": 1, "format": ["standard"]},
                    {"city": "Bordeaux", "count": 1, "format": ["standard"]}
                ]
            },
            "LU": {
                "cities": [
                    {"city": "Luxembourg City", "count": 2, "format": ["standard", "popup"]}
                ]
            }
        }
        
        # Store format specifications
        format_specs = {
            "flagship": {"sqm_range": (700, 900), "staff_range": (15, 25), "tier": "A", "target_revenue": (80000, 120000)},
            "standard": {"sqm_range": (400, 500), "staff_range": (8, 15), "tier": "B", "target_revenue": (45000, 75000)},
            "outlet": {"sqm_range": (550, 650), "staff_range": (6, 12), "tier": "B", "target_revenue": (35000, 55000)},
            "popup": {"sqm_range": (150, 250), "staff_range": (3, 6), "tier": "C", "target_revenue": (15000, 30000)}
        }
        
        # City coordinates for realistic addresses
        city_coords = {
            "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "addresses": ["Kalverstraat 1", "Nieuwendijk 45", "PC Hooftstraat 12"]},
            "Rotterdam": {"lat": 51.9225, "lon": 4.4792, "addresses": ["Lijnbaan 89", "Beurstraverse 23"]},
            "Utrecht": {"lat": 52.0907, "lon": 5.1214, "addresses": ["Vredenburg 15", "Hoog Catharijne 67"]},
            "Brussels": {"lat": 50.8505, "lon": 4.3488, "addresses": ["Rue Neuve 78", "Avenue Louise 123", "Boulevard Anspach 45"]},
            "Antwerp": {"lat": 51.2194, "lon": 4.4025, "addresses": ["Meir 67", "Kammenstraat 12"]},
            "Berlin": {"lat": 52.5200, "lon": 13.4050, "addresses": ["Alexanderplatz 1", "Kurfürstendamm 89", "Friedrichstrasse 156", "Mall of Berlin 23"]},
            "Hamburg": {"lat": 53.5511, "lon": 9.9937, "addresses": ["Mönckebergstrasse 45", "Spitalerstrasse 12", "Neuer Wall 78"]},
            "Munich": {"lat": 48.1351, "lon": 11.5820, "addresses": ["Marienplatz 8", "Pedestrian Zone 34", "Maximilianstrasse 67"]},
            "Paris": {"lat": 48.8566, "lon": 2.3522, "addresses": ["Champs-Élysées 123", "Rue de Rivoli 89", "Boulevard Saint-Germain 45", "Marais District 12"]},
            "Lyon": {"lat": 45.7640, "lon": 4.8357, "addresses": ["Rue de la République 56", "Part-Dieu 23"]},
            "Luxembourg City": {"lat": 49.6116, "lon": 6.1319, "addresses": ["Grand Rue 34", "Avenue de la Liberté 78"]}
        }
        
        store_id_counter = 1
        
        # Generate stores for each country
        for country_code, country_config in store_config.items():
            for city_config in country_config["cities"]:
                city = city_config["city"]
                city_info = city_coords.get(city, {"lat": 50.0, "lon": 5.0, "addresses": ["Main Street 1"]})
                
                for i, store_format in enumerate(city_config["format"]):
                    specs = format_specs[store_format]
                    
                    # Generate store details
                    store_name = f"EuroStyle {city}"
                    if len(city_config["format"]) > 1:
                        if store_format == "flagship":
                            store_name += " Flagship"
                        elif store_format == "outlet":
                            store_name += " Outlet"
                        elif store_format == "popup":
                            store_name += " Pop-up"
                        else:
                            store_name += f" {i+1}"
                    
                    # Address
                    address = city_info["addresses"][i] if i < len(city_info["addresses"]) else f"Fashion Street {i+1}"
                    
                    # Postal code (simplified)
                    postal_codes = {
                        "NL": lambda: f"{random.randint(1000, 9999)} {random.choice(['AA', 'AB', 'AC'])}",
                        "BE": lambda: f"{random.randint(1000, 9999)}",
                        "DE": lambda: f"{random.randint(10000, 99999)}",
                        "FR": lambda: f"{random.randint(75000, 95999)}",
                        "LU": lambda: f"L-{random.randint(1000, 9999)}"
                    }
                    
                    # Opening date (stores opened between 2019-2023)
                    opening_year = random.randint(2019, 2023)
                    opening_month = random.randint(1, 12)
                    opening_day = random.randint(1, 28)
                    opening_date = date(opening_year, opening_month, opening_day)
                    
                    # Manager name with appropriate locale
                    if country_code == "NL":
                        fake_local = Faker('nl_NL')
                    elif country_code == "DE":
                        fake_local = Faker('de_DE')
                    elif country_code == "FR":
                        fake_local = Faker('fr_FR')
                    else:
                        fake_local = Faker('en_GB')
                    
                    manager_name = fake_local.name()
                    
                    store_record = {
                        "store_id": f"STORE_{country_code}_{store_id_counter:03d}",
                        "store_name": store_name,
                        "country_code": country_code,
                        "city": city,
                        "address": address,
                        "postal_code": postal_codes[country_code](),
                        "latitude": city_info["lat"] + random.uniform(-0.01, 0.01),
                        "longitude": city_info["lon"] + random.uniform(-0.01, 0.01),
                        "store_format": store_format,
                        "floor_area_sqm": random.randint(*specs["sqm_range"]),
                        "opening_date": opening_date,
                        "manager_name": manager_name,
                        "staff_count": random.randint(*specs["staff_range"]),
                        "operating_hours": "Mon-Sat 10:00-20:00, Sun 12:00-18:00" if store_format != "popup" else "Thu-Sun 11:00-19:00",
                        "performance_tier": specs["tier"],
                        "target_monthly_revenue": random.randint(*specs["target_revenue"]),
                        "has_fitting_rooms": store_format in ["flagship", "standard", "outlet"],
                        "has_personal_styling": store_format == "flagship",
                        "has_click_and_collect": store_format in ["flagship", "standard"],
                        "wheelchair_accessible": random.choice([True, True, True, False]),  # 75% accessible
                        "is_active": True,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    stores_data.append(store_record)
                    store_id_counter += 1
        
        # Insert data in batches
        success = self.process_in_batches("stores", iter(stores_data), len(stores_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(stores_data)} store records across 5 countries")
            return True
        else:
            self.logger.error("❌ Failed to generate stores data")
            return False
    
    def generate_products(self) -> bool:
        """Generate products data."""
        self.logger.info("👕 Generating products data...")
        
        from datetime import datetime, date
        from faker import Faker
        import random
        
        fake = Faker(['en_US', 'de_DE', 'fr_FR', 'nl_NL'])
        products_data = []
        
        # Get target number from config
        target_products = self.config.get('data_volumes', {}).get('products', 2500)
        
        # Fashion product categories from config
        categories = {
            "Women": {
                "Tops": ["T-Shirts", "Blouses", "Sweaters", "Hoodies", "Tank Tops", "Cardigans"],
                "Bottoms": ["Jeans", "Trousers", "Skirts", "Shorts", "Leggings", "Pants"],
                "Dresses": ["Casual Dresses", "Formal Dresses", "Summer Dresses", "Evening Dresses"],
                "Outerwear": ["Jackets", "Coats", "Blazers", "Parkas", "Vests"]
            },
            "Men": {
                "Tops": ["T-Shirts", "Shirts", "Sweaters", "Hoodies", "Polo Shirts", "Tank Tops"],
                "Bottoms": ["Jeans", "Chinos", "Shorts", "Formal Trousers", "Cargo Pants"],
                "Outerwear": ["Jackets", "Coats", "Blazers", "Hoodies", "Vests"]
            },
            "Kids": {
                "Tops": ["T-Shirts", "Sweaters", "Hoodies", "Shirts"],
                "Bottoms": ["Jeans", "Shorts", "Leggings", "Sweatpants"],
                "Dresses": ["Play Dresses", "Party Dresses"]
            },
            "Accessories": {
                "Shoes": ["Sneakers", "Boots", "Sandals", "Flats", "Heels"],
                "Bags": ["Handbags", "Backpacks", "Totes", "Crossbody"],
                "Jewelry": ["Necklaces", "Bracelets", "Earrings", "Rings"]
            }
        }
        
        # Product attributes from config
        colors = ["Black", "White", "Navy", "Grey", "Beige", "Brown", "Red", "Blue", "Green", "Pink", "Yellow", "Purple", "Orange"]
        secondary_colors = ["Silver", "Gold", "Rose Gold", "Cream", "Ivory", "Charcoal", "Burgundy", "Teal", "Coral"]
        
        materials = {
            "sustainable": ["Organic Cotton", "Recycled Polyester", "Hemp", "Tencel", "Linen", "Bamboo"],
            "traditional": ["Cotton", "Polyester", "Wool", "Denim", "Leather", "Silk", "Cashmere", "Acrylic"]
        }
        
        sizes = {
            "clothing": ["XS", "S", "M", "L", "XL", "XXL"],
            "shoes_eu": ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"],
            "kids": ["2T", "3T", "4T", "5T", "6", "8", "10", "12", "14", "16"]
        }
        
        seasons = ["Spring/Summer 2024", "Fall/Winter 2024", "Spring/Summer 2025", "Fall/Winter 2025"]
        production_countries = ["Turkey", "Portugal", "Italy", "Germany", "Netherlands", "Belgium", "India", "China", "Vietnam"]
        
        # Brand names (mix of realistic fashion brands)
        brands = ["EuroStyle", "ModernCasual", "UrbanChic", "ClassicFit", "TrendSetters", "EcoFashion", "PremiumWear", "BasicStyle"]
        
        # Price ranges by category (EUR)
        price_ranges = {
            "Women": {"Tops": (19.99, 89.99), "Bottoms": (29.99, 129.99), "Dresses": (39.99, 199.99), "Outerwear": (49.99, 299.99)},
            "Men": {"Tops": (19.99, 79.99), "Bottoms": (29.99, 119.99), "Outerwear": (49.99, 249.99)},
            "Kids": {"Tops": (12.99, 39.99), "Bottoms": (16.99, 49.99), "Dresses": (19.99, 59.99)},
            "Accessories": {"Shoes": (39.99, 199.99), "Bags": (29.99, 149.99), "Jewelry": (9.99, 89.99)}
        }
        
        # Generate products
        product_id_counter = 1
        
        for category_l1, l2_categories in categories.items():
            # Calculate how many products for this L1 category
            category_weight = {"Women": 0.45, "Men": 0.35, "Kids": 0.15, "Accessories": 0.05}[category_l1]
            category_products = int(target_products * category_weight)
            
            products_generated = 0
            
            for category_l2, l3_list in l2_categories.items():
                l2_products = category_products // len(l2_categories)
                
                for category_l3 in l3_list:
                    l3_products = l2_products // len(l3_list)
                    
                    for _ in range(max(1, l3_products)):
                        if products_generated >= category_products:
                            break
                            
                        # Basic product info
                        brand = random.choice(brands)
                        primary_color = random.choice(colors)
                        secondary_color = random.choice(secondary_colors) if random.random() < 0.3 else None
                        
                        # Material composition
                        if random.random() < 0.35:  # 35% sustainable
                            material = random.choice(materials["sustainable"])
                            eco_friendly = True
                            sustainability_score = random.randint(7, 10)
                            carbon_footprint = round(random.uniform(2.0, 8.0), 2)
                        else:
                            material = random.choice(materials["traditional"])
                            eco_friendly = False
                            sustainability_score = random.randint(3, 7)
                            carbon_footprint = round(random.uniform(5.0, 15.0), 2)
                        
                        # Pricing
                        if category_l2 in price_ranges[category_l1]:
                            price_range = price_ranges[category_l1][category_l2]
                        else:
                            price_range = (19.99, 89.99)  # Default
                        
                        price_eur = round(random.uniform(*price_range), 2)
                        margin_pct = round(random.uniform(45.0, 65.0), 2)
                        cost_price = round(price_eur * (1 - margin_pct/100), 2)
                        
                        # Size ranges
                        if category_l2 == "Shoes":
                            size_range = sizes["shoes_eu"]
                        elif category_l1 == "Kids":
                            size_range = sizes["kids"] if category_l2 != "Shoes" else sizes["shoes_eu"][:6]
                        else:
                            size_range = sizes["clothing"]
                        
                        # Product name
                        style_adjectives = ["Classic", "Modern", "Casual", "Premium", "Basic", "Trendy", "Elegant", "Sporty"]
                        product_name = f"{random.choice(style_adjectives)} {primary_color} {category_l3.rstrip('s')}"
                        
                        # Localized names
                        product_name_local = {
                            "EN": product_name,
                            "DE": product_name.replace("Classic", "Klassisch").replace("Modern", "Modern").replace("Premium", "Premium"),
                            "FR": product_name.replace("Classic", "Classique").replace("Modern", "Moderne").replace("Premium", "Premium"),
                            "NL": product_name.replace("Classic", "Klassiek").replace("Modern", "Modern").replace("Premium", "Premium")
                        }
                        
                        # Launch date (products launched over past 3 years)
                        launch_year = random.randint(2022, 2025)
                        launch_month = random.randint(1, 12)
                        launch_day = random.randint(1, 28)
                        launch_date = date(launch_year, launch_month, launch_day)
                        
                        # Discontinue date (10% of products discontinued)
                        discontinue_date = None
                        is_active = True
                        if random.random() < 0.1 and launch_date < date(2024, 1, 1):
                            is_active = False
                            disc_year = random.randint(launch_year + 1, 2025)
                            discontinue_date = date(disc_year, random.randint(1, 12), random.randint(1, 28))
                        
                        # Stock and logistics
                        current_stock = random.randint(50, 2000) if is_active else random.randint(0, 100)
                        reorder_level = max(10, int(current_stock * 0.2))
                        lead_time = random.randint(14, 60)
                        
                        # URLs and images
                        product_slug = product_name.lower().replace(" ", "-")
                        product_url = f"https://eurostyle.com/products/{product_slug}"
                        image_urls = [
                            f"https://eurostyle.com/images/{product_slug}-main.jpg",
                            f"https://eurostyle.com/images/{product_slug}-detail.jpg",
                            f"https://eurostyle.com/images/{product_slug}-lifestyle.jpg"
                        ]
                        
                        product_record = {
                            "product_id": f"PROD_{product_id_counter:06d}",
                            "product_name": product_name,
                            "product_name_local": product_name_local,
                            "category_l1": category_l1,
                            "category_l2": category_l2,
                            "category_l3": category_l3,
                            "brand": brand,
                            "color_primary": primary_color,
                            "color_secondary": secondary_color or "",
                            "size_range": size_range,
                            "material_composition": material,
                            "price_eur": price_eur,
                            "price_local": {"EUR": price_eur},  # Could expand with currency conversion
                            "cost_price_eur": cost_price,
                            "margin_percentage": margin_pct,
                            "sustainability_score": sustainability_score,
                            "eco_friendly_materials": eco_friendly,
                            "carbon_footprint_kg": carbon_footprint,
                            "production_country": random.choice(production_countries),
                            "current_stock_total": current_stock,
                            "reorder_level": reorder_level,
                            "lead_time_days": lead_time,
                            "launch_date": launch_date,
                            "season": random.choice(seasons),
                            "is_active": is_active,
                            "discontinue_date": discontinue_date,
                            "online_availability": random.choice([True, True, True, False]),  # 75% available online
                            "product_url": product_url,
                            "image_urls": image_urls,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                        
                        products_data.append(product_record)
                        product_id_counter += 1
                        products_generated += 1
                        
                        if products_generated >= category_products:
                            break
                    
                    if products_generated >= category_products:
                        break
                
                if products_generated >= category_products:
                    break
        
        # Insert data in batches
        success = self.process_in_batches("products", iter(products_data), len(products_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(products_data)} fashion products across all categories")
            return True
        else:
            self.logger.error("❌ Failed to generate products data")
            return False
    
    def generate_campaigns(self) -> bool:
        """Generate marketing campaigns data."""
        self.logger.info("📢 Generating campaigns data...")
        
        from datetime import datetime, date, timedelta
        import random
        
        campaigns_data = []
        
        # Get target number from config
        target_campaigns = self.config.get('data_volumes', {}).get('campaigns', 200)
        
        # Get time range from config
        time_config = self.config.get('time_range', {})
        start_date = datetime.strptime(time_config.get('sales_start_date', '2020-01-01'), '%Y-%m-%d').date()
        end_date = datetime.strptime(time_config.get('sales_end_date', '2025-10-10'), '%Y-%m-%d').date()
        
        # Campaign types and channels
        campaign_types = [
            "seasonal_promotion", "new_collection_launch", "customer_acquisition", 
            "retention", "flash_sale", "loyalty_program", "brand_awareness", "clearance"
        ]
        
        channels = [
            "social_media", "email", "google_ads", "display_ads", "influencer", 
            "tv_commercial", "radio", "print", "outdoor", "in_store"
        ]
        
        countries = ["DE", "FR", "NL", "BE", "LU"]
        
        # Campaign messaging templates
        messages_by_type = {
            "seasonal_promotion": [
                "Celebrate the season with 25% off selected items!",
                "Spring into style with our latest collection!",
                "Winter warmth - cozy up with 30% off outerwear!"
            ],
            "new_collection_launch": [
                "Introducing our latest collection - fashion forward!",
                "New arrivals are here - be the first to shop!",
                "Fresh styles, endless possibilities - shop now!"
            ],
            "flash_sale": [
                "24 hours only - up to 50% off everything!",
                "Flash sale alert - limited time, unlimited style!",
                "Quick! Don't miss out on these incredible deals!"
            ],
            "clearance": [
                "End of season clearance - up to 70% off!",
                "Last chance to grab these styles at amazing prices!",
                "Clearance event - make room for new arrivals!"
            ]
        }
        
        # Generate campaigns
        campaign_id_counter = 1
        
        # Distribute campaigns across the time period
        total_days = (end_date - start_date).days
        campaigns_per_month = target_campaigns / (total_days / 30)
        
        current_date = start_date
        while current_date <= end_date and len(campaigns_data) < target_campaigns:
            # Generate 1-3 campaigns per month
            month_campaigns = random.randint(1, max(1, int(campaigns_per_month * 2)))
            
            for _ in range(month_campaigns):
                if len(campaigns_data) >= target_campaigns:
                    break
                    
                # Campaign basics
                campaign_type = random.choice(campaign_types)
                channel = random.choice(channels)
                
                # Campaign duration (1-30 days)
                if campaign_type == "flash_sale":
                    duration_days = random.randint(1, 3)  # Short flash sales
                elif campaign_type in ["seasonal_promotion", "clearance"]:
                    duration_days = random.randint(14, 30)  # Longer promotions
                else:
                    duration_days = random.randint(7, 21)  # Standard campaigns
                
                campaign_start = current_date + timedelta(days=random.randint(0, 28))
                campaign_end = campaign_start + timedelta(days=duration_days)
                
                # Ensure we don't go beyond our end date
                if campaign_end > end_date:
                    campaign_end = end_date
                
                # Target countries (1-5 countries)
                num_countries = random.choices([1, 2, 3, 5], weights=[30, 25, 25, 20])[0]
                target_countries = random.sample(countries, num_countries)
                
                # Budget based on channel and scope
                base_budget = {
                    "social_media": 5000, "email": 2000, "google_ads": 15000,
                    "display_ads": 12000, "influencer": 8000, "tv_commercial": 50000,
                    "radio": 20000, "print": 15000, "outdoor": 25000, "in_store": 5000
                }[channel]
                
                # Adjust budget by number of target countries
                budget = base_budget * len(target_countries) * random.uniform(0.8, 1.5)
                
                # Actual spend (85-110% of budget)
                spend = budget * random.uniform(0.85, 1.10)
                
                # Performance metrics based on channel
                channel_performance = {
                    "social_media": {"cpm": 8.5, "ctr": 0.015, "cvr": 0.025},
                    "email": {"cpm": 2.0, "ctr": 0.045, "cvr": 0.035},
                    "google_ads": {"cpm": 12.0, "ctr": 0.035, "cvr": 0.028},
                    "display_ads": {"cpm": 6.5, "ctr": 0.008, "cvr": 0.015},
                    "influencer": {"cpm": 15.0, "ctr": 0.025, "cvr": 0.022},
                    "tv_commercial": {"cpm": 25.0, "ctr": 0.002, "cvr": 0.008},
                    "radio": {"cpm": 18.0, "ctr": 0.003, "cvr": 0.012},
                    "print": {"cpm": 20.0, "ctr": 0.005, "cvr": 0.010},
                    "outdoor": {"cpm": 30.0, "ctr": 0.001, "cvr": 0.005},
                    "in_store": {"cpm": 5.0, "ctr": 0.100, "cvr": 0.045}
                }
                
                perf = channel_performance[channel]
                
                # Calculate impressions and clicks
                target_impressions = int((spend * 1000) / perf["cpm"])
                actual_impressions = int(target_impressions * random.uniform(0.9, 1.1))
                
                target_clicks = int(target_impressions * perf["ctr"])
                actual_clicks = int(target_clicks * random.uniform(0.8, 1.2))
                
                target_conversions = int(target_clicks * perf["cvr"])
                actual_conversions = int(target_conversions * random.uniform(0.7, 1.3))
                
                # Campaign messaging
                if campaign_type in messages_by_type:
                    message = random.choice(messages_by_type[campaign_type])
                else:
                    message = f"Discover amazing {campaign_type.replace('_', ' ')} deals!"
                
                # Discount and promo codes
                discount_percentage = 0.0  # Default to 0 instead of None
                promo_code = ""  # Default to empty string instead of None
                
                if campaign_type in ["seasonal_promotion", "flash_sale", "clearance", "loyalty_program"]:
                    if campaign_type == "flash_sale":
                        discount_percentage = round(random.uniform(30, 60), 1)
                    elif campaign_type == "clearance":
                        discount_percentage = round(random.uniform(40, 70), 1)
                    elif campaign_type == "seasonal_promotion":
                        discount_percentage = round(random.uniform(15, 35), 1)
                    else:
                        discount_percentage = round(random.uniform(10, 25), 1)
                    
                    # Generate promo code
                    promo_prefixes = ["STYLE", "EURO", "FRESH", "NEW", "SAVE", "DEAL"]
                    promo_code = f"{random.choice(promo_prefixes)}{random.randint(10, 99)}"
                
                # Campaign name
                season_names = ["Spring", "Summer", "Fall", "Winter"]
                campaign_names = {
                    "seasonal_promotion": f"{random.choice(season_names)} Style Event",
                    "new_collection_launch": f"New Arrivals {campaign_start.strftime('%B')}",
                    "flash_sale": f"Flash Sale {campaign_start.strftime('%d/%m')}",
                    "clearance": f"End of Season Clearance",
                    "customer_acquisition": f"Welcome Campaign {campaign_start.strftime('%B')}",
                    "retention": f"Come Back Campaign {campaign_start.strftime('%B')}",
                    "brand_awareness": f"EuroStyle Brand Campaign {campaign_start.year}",
                    "loyalty_program": f"Loyalty Rewards {campaign_start.strftime('%B')}"
                }
                
                campaign_name = campaign_names.get(campaign_type, f"Campaign {campaign_id_counter}")
                
                campaign_record = {
                    "campaign_id": f"CAMP_{campaign_id_counter:06d}",
                    "campaign_name": campaign_name,
                    "campaign_type": campaign_type,
                    "channel": channel,
                    "target_countries": target_countries,
                    "start_date": campaign_start,
                    "end_date": campaign_end,
                    "budget_eur": round(budget, 2),
                    "spend_eur": round(spend, 2),
                    "target_impressions": target_impressions,
                    "actual_impressions": actual_impressions,
                    "target_clicks": target_clicks,
                    "actual_clicks": actual_clicks,
                    "target_conversions": target_conversions,
                    "actual_conversions": actual_conversions,
                    "campaign_message": message,
                    "discount_percentage": discount_percentage,
                    "promotional_code": promo_code,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                campaigns_data.append(campaign_record)
                campaign_id_counter += 1
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        # Insert data in batches
        success = self.process_in_batches("campaigns", iter(campaigns_data), len(campaigns_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(campaigns_data)} marketing campaigns across 5+ years")
            return True
        else:
            self.logger.error("❌ Failed to generate campaigns data")
            return False
    
    def generate_customers(self) -> bool:
        """Generate customers data."""
        self.logger.info("👥 Generating customers data...")
        
        from datetime import datetime, date, timedelta
        from faker import Faker
        import random
        
        customers_data = []
        
        # Get target number from config
        target_customers = self.config.get('data_volumes', {}).get('customers', 150000)
        
        # Geographic distribution from config
        geo_config = self.config.get('geographic_distribution', {})
        countries = [
            {"code": "DE", "percentage": 35, "faker_locale": "de_DE", "language": "DE"},
            {"code": "FR", "percentage": 25, "faker_locale": "fr_FR", "language": "FR"},
            {"code": "NL", "percentage": 20, "faker_locale": "nl_NL", "language": "NL"},
            {"code": "BE", "percentage": 15, "faker_locale": "nl_BE", "language": "NL"},
            {"code": "LU", "percentage": 5, "faker_locale": "fr_FR", "language": "FR"}
        ]
        
        # Registration channels
        registration_channels = ["website", "mobile_app", "in_store", "social_media", "email_campaign", "referral"]
        
        # Customer lifecycle segments from config
        lifecycle_segments = {
            "new": {"weight": 0.25, "orders": (0, 1), "spend": (0, 200)},
            "developing": {"weight": 0.35, "orders": (2, 5), "spend": (100, 800)},
            "established": {"weight": 0.25, "orders": (6, 15), "spend": (600, 2000)},
            "loyal": {"weight": 0.15, "orders": (16, 50), "spend": (1500, 5000)}
        }
        
        # Loyalty tiers
        loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
        
        customer_id_counter = 1
        
        for country in countries:
            country_customers = int(target_customers * (country["percentage"] / 100))
            
            # Use appropriate Faker locale
            fake = Faker(country["faker_locale"])
            
            # Get cities for this country from geography data
            cities_data = {
                "DE": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf"],
                "FR": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
                "NL": ["Amsterdam", "Rotterdam", "Utrecht", "Eindhoven", "Groningen", "Tilburg", "Almere"],
                "BE": ["Brussels", "Antwerp", "Ghent", "Charleroi", "Liège"],
                "LU": ["Luxembourg City", "Esch-sur-Alzette"]
            }
            
            for i in range(country_customers):
                # Basic demographics
                gender_choice = random.choices(["M", "F", "O"], weights=[48, 50, 2])[0]
                
                if gender_choice == "M":
                    first_name = fake.first_name_male()
                elif gender_choice == "F":
                    first_name = fake.first_name_female()
                else:
                    first_name = fake.first_name()
                
                last_name = fake.last_name()
                
                # Age distribution (16-75, fashion retail customers)
                age = random.choices(
                    range(16, 76),
                    weights=[1 if age < 18 else 5 if age < 30 else 8 if age < 45 else 6 if age < 60 else 2 for age in range(16, 76)]
                )[0]
                
                birth_date = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
                
                # Contact information
                email = fake.email()
                phone = fake.phone_number() if random.random() > 0.08 else ""  # 92% have phone
                
                # Address
                city = random.choice(cities_data[country["code"]])
                street_address = fake.street_address()
                
                # Postal codes by country
                if country["code"] == "DE":
                    postal_code = fake.postcode()
                elif country["code"] == "FR":
                    postal_code = f"{random.randint(75000, 95000)}"
                elif country["code"] == "NL":
                    postal_code = f"{random.randint(1000, 9999)} {random.choice(['AA', 'AB', 'AC', 'AD'])}"
                elif country["code"] == "BE":
                    postal_code = f"{random.randint(1000, 9999)}"
                else:  # LU
                    postal_code = f"L-{random.randint(1000, 9999)}"
                
                # Registration date (customers registered over past 5 years)
                reg_start = date(2020, 1, 1)
                reg_end = date.today()
                reg_days = (reg_end - reg_start).days
                registration_date = reg_start + timedelta(days=random.randint(0, reg_days))
                
                # Customer behavior based on lifecycle segment
                segment = random.choices(
                    list(lifecycle_segments.keys()),
                    weights=[segment["weight"] for segment in lifecycle_segments.values()]
                )[0]
                
                segment_data = lifecycle_segments[segment]
                total_orders = random.randint(*segment_data["orders"])
                total_spent = round(random.uniform(*segment_data["spend"]), 2)
                
                # Calculate average order value
                avg_order_value = round(total_spent / max(1, total_orders), 2) if total_orders > 0 else 0
                
                # Last order date (if they have orders)
                last_order_date = registration_date  # Default to registration date
                if total_orders > 0:
                    max_days_ago = max(1, min(365, (date.today() - registration_date).days))
                    if max_days_ago > 1:
                        last_order_days_ago = random.randint(1, max_days_ago)
                        last_order_date = date.today() - timedelta(days=last_order_days_ago)
                    else:
                        last_order_date = registration_date
                
                # Customer status
                days_since_registration = (date.today() - registration_date).days
                days_since_last_order = (date.today() - last_order_date).days if last_order_date else days_since_registration
                
                if days_since_last_order > 365:
                    customer_status = "inactive"
                elif random.random() < 0.005:  # 0.5% suspended
                    customer_status = "suspended"
                else:
                    customer_status = "active"
                
                # Marketing preferences (GDPR compliant)
                marketing_opt_in = random.random() < 0.42
                newsletter_subscription = random.random() < 0.28 if marketing_opt_in else False
                sms_opt_in = random.random() < 0.25 if marketing_opt_in else False
                
                # Loyalty program
                loyalty_member = random.random() < 0.35  # 35% adoption rate
                loyalty_points = 0
                loyalty_tier = ""
                
                if loyalty_member:
                    # Points based on spending (1 point per euro)
                    loyalty_points = int(total_spent) + random.randint(0, 500)
                    
                    if loyalty_points >= 2000:
                        loyalty_tier = "Platinum"
                    elif loyalty_points >= 1000:
                        loyalty_tier = "Gold"
                    elif loyalty_points >= 500:
                        loyalty_tier = "Silver"
                    else:
                        loyalty_tier = "Bronze"
                
                customer_record = {
                    "customer_id": f"CUST_{country['code']}_{customer_id_counter:07d}",
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "date_of_birth": birth_date,
                    "gender": gender_choice,
                    "language_preference": country["language"],
                    "street_address": street_address,
                    "city": city,
                    "postal_code": postal_code,
                    "country_code": country["code"],
                    "region": city,  # Simplified - using city as region
                    "registration_date": datetime.combine(registration_date, datetime.min.time()),
                    "registration_channel": random.choice(registration_channels),
                    "customer_status": customer_status,
                    "marketing_opt_in": marketing_opt_in,
                    "newsletter_subscription": newsletter_subscription,
                    "sms_opt_in": sms_opt_in,
                    "total_orders": total_orders,
                    "total_spent": total_spent,
                    "average_order_value": avg_order_value,
                    "last_order_date": last_order_date,
                    "loyalty_member": loyalty_member,
                    "loyalty_points": loyalty_points,
                    "loyalty_tier": loyalty_tier,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                customers_data.append(customer_record)
                customer_id_counter += 1
                
                # Progress logging for large datasets
                if customer_id_counter % 10000 == 0:
                    self.logger.info(f"Generated {customer_id_counter} customers...")
        
        # Insert data in batches
        success = self.process_in_batches("customers", iter(customers_data), len(customers_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(customers_data)} European customers across 5 countries")
            return True
        else:
            self.logger.error("❌ Failed to generate customers data")
            return False
    
    def generate_table_data(self, table_name: str) -> bool:
        """Generate data for a specific master data table."""
        if hasattr(self, f"generate_{table_name}"):
            return getattr(self, f"generate_{table_name}")()
        else:
            self.logger.error(f"❌ Unknown master data table: {table_name}")
            return False