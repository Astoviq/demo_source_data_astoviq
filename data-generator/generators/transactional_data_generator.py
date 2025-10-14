"""
Transactional Data Generator
============================

Generates transactional data for the EuroStyle Fashion system:
- Inventory
- Orders
- Order Lines
"""

from generators.base_generator import BaseGenerator

class TransactionalDataGenerator(BaseGenerator):
    """Generates transactional data tables."""
    
    def __init__(self, config, db_connector):
        """Initialize the transactional data generator."""
        super().__init__(config, db_connector)
    
    def generate_inventory(self) -> bool:
        """Generate inventory data."""
        self.logger.info("📦 Generating inventory data...")
        
        from datetime import datetime, date, timedelta
        import random
        import pandas as pd
        
        inventory_data = []
        
        # Get target number from config
        target_inventory = self.config.get('data_volumes', {}).get('inventory_records', 50000)
        
        # Load reference data from database
        self.logger.info("Loading reference data...")
        
        # Get products
        products_query = "SELECT product_id, category_l1, cost_price_eur, size_range, color_primary, season, is_active FROM products WHERE is_active = true"
        products_result = self.db_connector.client.execute(products_query, with_column_types=True)
        products_df = pd.DataFrame([dict(zip([col[0] for col in products_result[1]], row)) for row in products_result[0]])
        
        # Get stores
        stores_query = "SELECT store_id, country_code, store_format FROM stores WHERE is_active = true"
        stores_result = self.db_connector.client.execute(stores_query, with_column_types=True)
        stores_df = pd.DataFrame([dict(zip([col[0] for col in stores_result[1]], row)) for row in stores_result[0]])
        
        self.logger.info(f"Loaded {len(products_df)} products, {len(stores_df)} stores")
        
        # Inventory configuration
        location_types = ["store", "warehouse", "distribution_center"]
        movement_types = ["receipt", "sale", "transfer", "adjustment", "return"]
        
        # Stock level patterns by store format
        stock_patterns = {
            "flagship": {"base_qty": (50, 200), "variety_factor": 0.8},  # High variety, high stock
            "standard": {"base_qty": (20, 100), "variety_factor": 0.6},  # Medium variety, medium stock
            "outlet": {"base_qty": (10, 80), "variety_factor": 0.4},     # Lower variety, discount focus
            "popup": {"base_qty": (5, 30), "variety_factor": 0.3}       # Limited variety, low stock
        }
        
        inventory_id_counter = 1
        
        # Generate inventory for each store
        for _, store in stores_df.iterrows():
            store_pattern = stock_patterns.get(store['store_format'], stock_patterns['standard'])
            
            # Determine how many products this store carries
            variety_factor = store_pattern['variety_factor']
            num_products = int(len(products_df) * variety_factor)
            
            # Select products for this store (favor popular categories)
            store_products = products_df.sample(n=min(num_products, len(products_df))).copy()
            
            for _, product in store_products.iterrows():
                # Get size range for product
                size_range = product['size_range']
                if isinstance(size_range, list):
                    sizes = size_range
                else:
                    # Default sizes if parsing fails
                    sizes = ["XS", "S", "M", "L", "XL"]
                
                # Generate inventory for each size (not all sizes for all products)
                num_sizes = random.choices([1, 2, 3, len(sizes)], weights=[20, 30, 35, 15])[0]
                selected_sizes = random.sample(sizes, min(num_sizes, len(sizes)))
                
                for size in selected_sizes:
                    # Base inventory levels
                    base_qty_range = store_pattern['base_qty']
                    quantity_on_hand = random.randint(*base_qty_range)
                    
                    # Seasonal adjustments
                    current_month = date.today().month
                    if product['season'] == 'Spring/Summer 2025' and current_month in [3, 4, 5, 6]:
                        quantity_on_hand = int(quantity_on_hand * random.uniform(1.2, 1.8))  # Higher stock for in-season
                    elif product['season'] == 'Fall/Winter 2024' and current_month in [9, 10, 11, 12]:
                        quantity_on_hand = int(quantity_on_hand * random.uniform(1.2, 1.8))
                    elif current_month in [1, 2, 7, 8]:  # Off-season clearance
                        quantity_on_hand = int(quantity_on_hand * random.uniform(0.3, 0.7))
                    
                    # Reserved quantities (orders not yet fulfilled)
                    quantity_reserved = random.randint(0, min(10, quantity_on_hand // 3))
                    quantity_available = max(0, quantity_on_hand - quantity_reserved)
                    
                    # Reorder points and max levels
                    reorder_point = max(5, int(quantity_on_hand * random.uniform(0.15, 0.25)))
                    max_stock_level = int(quantity_on_hand * random.uniform(1.5, 2.5))
                    
                    # Quantities on order (if below reorder point)
                    quantity_on_order = 0
                    if quantity_available <= reorder_point:
                        quantity_on_order = random.randint(reorder_point, max_stock_level - quantity_on_hand)
                    
                    # Dates
                    last_restock_days_ago = random.randint(1, 60)
                    last_restock_date = date.today() - timedelta(days=last_restock_days_ago)
                    
                    next_restock_date = None
                    if quantity_on_order > 0:
                        next_restock_date = date.today() + timedelta(days=random.randint(3, 21))
                    
                    # Last movement
                    last_movement_days_ago = random.randint(0, 7)
                    last_movement_date = datetime.now() - timedelta(days=last_movement_days_ago, hours=random.randint(0, 23))
                    last_movement_type = random.choice(movement_types)
                    
                    # Pricing
                    unit_cost = float(product['cost_price_eur'])
                    inventory_value = round(quantity_on_hand * unit_cost, 2)
                    
                    # Markdown dates (for clearance items)
                    markdown_date = None
                    if random.random() < 0.15:  # 15% of items on markdown
                        markdown_date = date.today() + timedelta(days=random.randint(-30, 30))
                    
                    # Location type (mostly store, some warehouse)
                    if store['store_format'] == 'flagship':
                        location_type = random.choices(["store", "warehouse"], weights=[85, 15])[0]
                    else:
                        location_type = "store"
                    
                    inventory_record = {
                        "inventory_id": f"INV_{inventory_id_counter:08d}",
                        "product_id": product['product_id'],
                        "store_id": store['store_id'],
                        "location_type": location_type,
                        "size": size,
                        "color": product['color_primary'],
                        "quantity_on_hand": quantity_on_hand,
                        "quantity_reserved": quantity_reserved,
                        "quantity_available": quantity_available,
                        "quantity_on_order": quantity_on_order,
                        "reorder_point": reorder_point,
                        "max_stock_level": max_stock_level,
                        "last_restock_date": last_restock_date,
                        "next_restock_date": next_restock_date,
                        "unit_cost_eur": unit_cost,
                        "inventory_value_eur": inventory_value,
                        "last_movement_date": last_movement_date,
                        "last_movement_type": last_movement_type,
                        "season": product['season'],
                        "markdown_date": markdown_date,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    inventory_data.append(inventory_record)
                    inventory_id_counter += 1
                    
                    # Progress logging
                    if len(inventory_data) % 5000 == 0:
                        self.logger.info(f"Generated {len(inventory_data)} inventory records...")
                    
                    # Stop if we've reached target
                    if len(inventory_data) >= target_inventory:
                        break
                
                if len(inventory_data) >= target_inventory:
                    break
            
            if len(inventory_data) >= target_inventory:
                break
        
        # Insert inventory data
        success = self.process_in_batches("inventory", iter(inventory_data), len(inventory_data))
        
        if success:
            self.logger.info(f"✅ Generated {len(inventory_data)} inventory records across {len(stores_df)} stores")
            return True
        else:
            self.logger.error("❌ Failed to generate inventory data")
            return False
    
    def generate_orders(self) -> bool:
        """Generate orders and order_lines data together."""
        self.logger.info("🛒 Generating orders and order lines data...")
        
        from datetime import datetime, date, timedelta
        from faker import Faker
        import random
        import pandas as pd
        
        fake = Faker()
        
        # Get target numbers from config
        target_orders = self.config.get('data_volumes', {}).get('orders', 500000)
        target_order_lines = self.config.get('data_volumes', {}).get('order_lines', 1200000)
        avg_lines_per_order = target_order_lines / target_orders
        
        # Get time range from config
        time_config = self.config.get('time_range', {})
        start_date = datetime.strptime(time_config.get('sales_start_date', '2020-01-01'), '%Y-%m-%d').date()
        end_date = datetime.strptime(time_config.get('sales_end_date', '2025-10-10'), '%Y-%m-%d').date()
        
        # Load reference data from database
        self.logger.info("Loading reference data...")
        
        # Get customers data directly from ClickHouse
        customers_query = "SELECT customer_id, country_code, customer_status, total_orders, average_order_value, registration_date FROM customers WHERE customer_status = 'active'"
        customers_result = self.db_connector.client.execute(customers_query, with_column_types=True)
        customers_df = pd.DataFrame([dict(zip([col[0] for col in customers_result[1]], row)) for row in customers_result[0]])
        
        # Get products data
        products_query = "SELECT product_id, category_l1, price_eur, cost_price_eur, size_range, color_primary, is_active FROM products WHERE is_active = true"
        products_result = self.db_connector.client.execute(products_query, with_column_types=True)
        products_df = pd.DataFrame([dict(zip([col[0] for col in products_result[1]], row)) for row in products_result[0]])
        
        # Get stores data
        stores_query = "SELECT store_id, country_code, store_format FROM stores WHERE is_active = true"
        stores_result = self.db_connector.client.execute(stores_query, with_column_types=True)
        stores_df = pd.DataFrame([dict(zip([col[0] for col in stores_result[1]], row)) for row in stores_result[0]])
        
        # Get campaigns data
        campaigns_query = "SELECT campaign_id, promotional_code, discount_percentage, start_date, end_date, target_countries FROM campaigns"
        campaigns_result = self.db_connector.client.execute(campaigns_query, with_column_types=True)
        campaigns_df = pd.DataFrame([dict(zip([col[0] for col in campaigns_result[1]], row)) for row in campaigns_result[0]])
        
        self.logger.info(f"Loaded {len(customers_df)} customers, {len(products_df)} products, {len(stores_df)} stores, {len(campaigns_df)} campaigns")
        
        # Seasonality patterns from config
        seasonal_multipliers = self.config.get('seasonality', {}).get('sales_multipliers', {
            1: 0.6, 2: 0.7, 3: 1.4, 4: 1.3, 5: 1.0, 6: 1.0,
            7: 0.8, 8: 0.9, 9: 1.5, 10: 1.4, 11: 1.6, 12: 1.3
        })
        
        # Order and fulfillment settings
        order_statuses = [
            "completed", "shipped", "processing", "cancelled", "returned", "pending"
        ]
        
        status_weights = [0.70, 0.15, 0.08, 0.04, 0.02, 0.01]  # Most orders completed
        
        channels = ["online", "mobile_app", "in_store", "phone", "social_commerce"]
        channel_weights = [0.45, 0.30, 0.20, 0.03, 0.02]
        
        traffic_sources = ["organic_search", "paid_search", "social_media", "email", "direct", "referral", "display_ads"]
        
        shipping_methods = ["standard", "express", "next_day", "click_collect", "in_store_pickup"]
        payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer", "buy_now_pay_later"]
        
        # Generate orders and order lines
        orders_data = []
        order_lines_data = []
        
        # Calculate orders per day
        total_days = (end_date - start_date).days
        base_orders_per_day = target_orders / total_days
        
        current_date = start_date
        order_id_counter = 1
        order_line_id_counter = 1
        
        self.logger.info(f"Generating {target_orders} orders over {total_days} days...")
        
        while current_date <= end_date and len(orders_data) < target_orders:
            # Apply seasonal multiplier
            seasonal_mult = seasonal_multipliers.get(current_date.month, 1.0)
            daily_orders = int(base_orders_per_day * seasonal_mult * random.uniform(0.7, 1.3))
            
            for _ in range(daily_orders):
                if len(orders_data) >= target_orders:
                    break
                
                # Select customer (weighted by activity)
                customer = customers_df.sample(1).iloc[0]
                
                # Determine channel and store
                channel = random.choices(channels, weights=channel_weights)[0]
                store_id = ""
                
                if channel == "in_store" or random.random() < 0.15:  # 15% of online orders also have store association
                    country_stores = stores_df[stores_df['country_code'] == customer['country_code']]
                    if not country_stores.empty:
                        store_id = country_stores.sample(1)['store_id'].iloc[0]
                
                # Order timing
                order_hour = random.choices(range(24), weights=[
                    1,1,1,1,1,2,3,4,5,6,8,10,12,14,16,18,20,18,15,12,8,5,3,2
                ])[0]
                order_datetime = datetime.combine(current_date, datetime.min.time().replace(hour=order_hour, minute=random.randint(0,59)))
                
                # Generate order lines (1-6 items per order typically)
                num_lines = random.choices([1,2,3,4,5,6], weights=[30,35,20,10,4,1])[0]
                
                subtotal = 0
                order_line_records = []
                
                for line_idx in range(num_lines):
                    # Select product
                    product = products_df.sample(1).iloc[0]
                    
                    # Select size and color
                    size_range = product['size_range']
                    if isinstance(size_range, list) and len(size_range) > 0:
                        size = random.choice(size_range)
                    else:
                        # Default sizes if parsing fails or list is empty
                        size = random.choice(["XS", "S", "M", "L", "XL"])
                    color = product['color_primary']
                    
                    # Quantity (mostly 1, sometimes 2-3)
                    quantity = random.choices([1,2,3], weights=[85,12,3])[0]
                    
                    # Pricing (convert Decimal to float)
                    unit_price = float(product['price_eur'])
                    unit_cost = float(product['cost_price_eur'])
                    
                    # Line discount (occasional)
                    line_discount = 0
                    if random.random() < 0.2:  # 20% of lines have discount
                        line_discount = unit_price * quantity * random.uniform(0.05, 0.25)
                    
                    line_total = (unit_price * quantity) - line_discount
                    subtotal += line_total
                    
                    # Fulfillment status
                    fulfillment_status = "fulfilled"
                    shipped_qty = quantity
                    returned_qty = 0
                    return_reason = ""
                    
                    if random.random() < 0.08:  # 8% return rate
                        returned_qty = random.randint(1, quantity)
                        return_reasons = ["wrong_size", "wrong_color", "damaged", "not_as_expected", "changed_mind"]
                        return_reason = random.choice(return_reasons)
                        fulfillment_status = "returned"
                    
                    # Inventory timestamps
                    inventory_reserved = order_datetime
                    inventory_fulfilled = None
                    if fulfillment_status in ["fulfilled", "returned"]:
                        inventory_fulfilled = order_datetime + timedelta(hours=random.randint(1, 48))
                    
                    order_line_record = {
                        "order_line_id": f"LINE_{order_line_id_counter:08d}",
                        "order_id": f"ORD_{order_id_counter:08d}",
                        "product_id": product['product_id'],
                        "size": size,
                        "color": color,
                        "quantity": quantity,
                        "unit_price_eur": unit_price,
                        "unit_cost_eur": unit_cost,
                        "line_discount_eur": line_discount,
                        "line_total_eur": line_total,
                        "fulfillment_status": fulfillment_status,
                        "shipped_quantity": shipped_qty,
                        "returned_quantity": returned_qty,
                        "return_reason": return_reason if return_reason else "",
                        "exchange_product_id": "",
                        "inventory_reserved_at": inventory_reserved,
                        "inventory_fulfilled_at": inventory_fulfilled,
                        "created_at": order_datetime,
                        "updated_at": order_datetime
                    }
                    
                    order_line_records.append(order_line_record)
                    order_line_id_counter += 1
                
                # Calculate order totals
                tax_rate = 0.20  # Simplified EU VAT
                tax_amount = subtotal * tax_rate
                
                # Shipping cost
                shipping_cost = 0
                if channel not in ["in_store", "click_collect", "in_store_pickup"]:
                    if subtotal < 50:  # Free shipping over 50 EUR
                        shipping_cost = random.uniform(4.95, 9.95)
                
                # Order-level discount (campaign codes)
                discount_amount = 0
                campaign_code = ""
                
                # Check for active campaigns
                active_campaigns = campaigns_df[
                    (campaigns_df['start_date'] <= current_date) & 
                    (campaigns_df['end_date'] >= current_date) &
                    (campaigns_df['target_countries'].str.contains(customer['country_code']))
                ]
                
                if not active_campaigns.empty and random.random() < 0.15:  # 15% use campaign codes
                    campaign = active_campaigns.sample(1).iloc[0]
                    campaign_code = campaign['promotional_code'] if campaign['promotional_code'] else ""
                    discount_pct = float(campaign['discount_percentage']) if campaign['discount_percentage'] else 0
                    if discount_pct > 0:
                        discount_amount = subtotal * (discount_pct / 100)
                
                total_amount = subtotal + tax_amount + shipping_cost - discount_amount
                
                # Order status and delivery
                order_status = random.choices(order_statuses, weights=status_weights)[0]
                
                delivery_date = None
                promised_delivery = None
                
                if order_status in ["completed", "shipped", "returned"]:
                    delivery_days = random.randint(1, 7)
                    promised_delivery = current_date + timedelta(days=delivery_days)
                    if order_status == "completed":
                        delivery_date = promised_delivery + timedelta(days=random.randint(-1, 1))
                
                # Payment
                payment_method = random.choice(payment_methods)
                payment_status = "completed" if order_status != "cancelled" else "failed"
                
                # Generate order record
                order_record = {
                    "order_id": f"ORD_{order_id_counter:08d}",
                    "customer_id": customer['customer_id'],
                    "store_id": store_id,
                    "order_date": current_date,
                    "order_datetime": order_datetime,
                    "delivery_date": delivery_date,
                    "promised_delivery_date": promised_delivery,
                    "subtotal_eur": round(subtotal, 2),
                    "tax_amount_eur": round(tax_amount, 2),
                    "shipping_cost_eur": round(shipping_cost, 2),
                    "discount_amount_eur": round(discount_amount, 2),
                    "total_amount_eur": round(total_amount, 2),
                    "currency_code": "EUR",
                    "exchange_rate": 1.0000,
                    "total_amount_local": round(total_amount, 2),
                    "order_status": order_status,
                    "fulfillment_center": f"FC_{customer['country_code']}",
                    "shipping_method": random.choice(shipping_methods),
                    "tracking_number": f"TRK{random.randint(100000000, 999999999)}" if order_status in ["shipped", "completed"] else "",
                    "order_channel": channel,
                    "traffic_source": random.choice(traffic_sources),
                    "campaign_code": campaign_code,
                    "payment_method": payment_method,
                    "payment_status": payment_status,
                    "customer_service_notes": "",
                    "return_reason": "",
                    "return_date": None,
                    "created_at": order_datetime,
                    "updated_at": order_datetime
                }
                
                orders_data.append(order_record)
                order_lines_data.extend(order_line_records)
                order_id_counter += 1
                
                # Progress logging
                if len(orders_data) % 10000 == 0:
                    self.logger.info(f"Generated {len(orders_data)} orders with {len(order_lines_data)} order lines...")
            
            current_date += timedelta(days=1)
        
        # Insert orders data
        self.logger.info(f"Inserting {len(orders_data)} orders...")
        success_orders = self.process_in_batches("orders", iter(orders_data), len(orders_data))
        
        if not success_orders:
            self.logger.error("❌ Failed to insert orders data")
            return False
        
        # Insert order lines data
        self.logger.info(f"Inserting {len(order_lines_data)} order lines...")
        success_lines = self.process_in_batches("order_lines", iter(order_lines_data), len(order_lines_data))
        
        if success_orders and success_lines:
            self.logger.info(f"✅ Generated {len(orders_data)} orders and {len(order_lines_data)} order lines")
            return True
        else:
            self.logger.error("❌ Failed to generate orders and order lines data")
            return False
    
    def generate_order_lines(self) -> bool:
        """Generate order lines data (handled by generate_orders)."""
        self.logger.info("📋 Order lines are generated together with orders...")
        return self.generate_orders()  # Order lines are generated with orders
    
    def generate_table_data(self, table_name: str) -> bool:
        """Generate data for a specific transactional table."""
        if hasattr(self, f"generate_{table_name}"):
            return getattr(self, f"generate_{table_name}")()
        else:
            self.logger.error(f"❌ Unknown transactional table: {table_name}")
            return False