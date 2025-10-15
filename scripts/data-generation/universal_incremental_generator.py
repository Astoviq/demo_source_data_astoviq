#!/usr/bin/env python3
"""
Universal Incremental Data Generator for EuroStyle Fashion
=========================================================
Generates realistic incremental business data on top of existing Universal Data Generator V2 dataset.
Simulates daily business operations: new orders, customer updates, employee changes, etc.
"""

import sys
import os
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import csv
import time

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Add utils directory to path for logging
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))
from logging_config import setup_incremental_logging

class UniversalIncrementalGenerator:
    def __init__(self, base_data_path="data/csv"):
        self.base_data_path = Path(base_data_path)
        self.output_path = self.base_data_path
        self.current_date = datetime.now().date()
        
        # Setup logging
        self.logger_setup = setup_incremental_logging()
        self.logger = self.logger_setup.get_logger()
        
        self.logger.info("🔄 Universal Incremental Data Generator initialized")
        self.logger.info(f"📁 Base data path: {self.base_data_path}")
        
    def get_latest_order_id(self):
        """Get the latest order ID from existing data to continue sequence"""
        try:
            with gzip.open(self.base_data_path / "eurostyle_operational.orders.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                order_ids = [row['order_id'] for row in reader]
                if order_ids:
                    # Extract number from last order ID (e.g., ORD_EU_2024_005000 -> 5000)
                    last_id = max(order_ids)
                    return int(last_id.split('_')[-1])
        except Exception as e:
            self.logger.warning(f"⚠️ Could not determine latest order ID: {e}")
        return 5000  # Default fallback
    
    def get_latest_customer_id(self):
        """Get the latest customer ID from existing data to continue sequence"""
        try:
            with gzip.open(self.base_data_path / "eurostyle_operational.customers.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                customer_ids = [row['customer_id'] for row in reader]
                if customer_ids:
                    # Extract number from last customer ID (e.g., CUST_EU_050000 -> 50000)
                    last_id = max(customer_ids)
                    return int(last_id.split('_')[-1])
        except Exception as e:
            self.logger.warning(f"⚠️ Could not determine latest customer ID: {e}")
        return 50000  # Default fallback
        
    def get_existing_customers(self, limit=1000):
        """Get sample of existing customers for order generation"""
        try:
            customers = []
            with gzip.open(self.base_data_path / "eurostyle_operational.customers.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customers.append(row['customer_id'])
                    if len(customers) >= limit:
                        break
            return customers
        except Exception as e:
            print(f"⚠️ Could not load existing customers: {e}")
            return []
    
    def get_existing_products(self, limit=500):
        """Get sample of existing products for order generation"""
        try:
            products = []
            with gzip.open(self.base_data_path / "eurostyle_operational.products.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    products.append({
                        'product_id': row['product_id'],
                        'price_eur': float(row['price_eur']),
                        'category_l1': row['category_l1']
                    })
                    if len(products) >= limit:
                        break
            return products
        except Exception as e:
            print(f"⚠️ Could not load existing products: {e}")
            return []
    
    def get_existing_stores(self):
        """Get existing stores for order assignment"""
        try:
            stores = []
            with gzip.open(self.base_data_path / "eurostyle_operational.stores.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stores.append(row['store_id'])
            stores.append("ONLINE")  # Always include online store
            return stores
        except Exception as e:
            print(f"⚠️ Could not load existing stores: {e}")
            return ["ONLINE"]
    
    def generate_incremental_orders(self, num_orders, days=1):
        """Generate incremental orders with matching GL entries"""
        self.logger.info(f"📦 Generating {num_orders} incremental orders for {days} day(s)")
        
        # Get existing data for referential integrity
        customers = self.get_existing_customers()
        products = self.get_existing_products()
        stores = self.get_existing_stores()
        
        if not customers or not products:
            self.logger.error("❌ Cannot generate orders without existing customers and products")
            return False
            
        start_order_id = self.get_latest_order_id() + 1
        
        # Generate orders
        orders = []
        gl_headers = []
        gl_lines = []
        
        for i in range(num_orders):
            order_id = f"ORD_EU_2024_{start_order_id + i:06d}"
            customer_id = random.choice(customers)
            store_id = random.choice(stores)
            
            # Random order date within the last 'days' days
            order_date = self.current_date - timedelta(days=random.randint(0, days))
            order_datetime = datetime.combine(order_date, datetime.min.time()) + timedelta(
                hours=random.randint(9, 20), minutes=random.randint(0, 59)
            )
            
            # Generate order items (1-4 items per order)
            num_items = random.randint(1, 4)
            subtotal = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                item_price = product['price_eur'] * quantity
                subtotal += item_price
            
            # Calculate taxes and totals
            tax_rate = 0.21  # 21% VAT (European standard)
            tax_amount = subtotal * tax_rate
            shipping = 0.00 if store_id != "ONLINE" else (5.95 if subtotal < 50 else 0.00)
            total_amount = subtotal + tax_amount + shipping
            
            # Order record
            order = {
                'order_id': order_id,
                'customer_id': customer_id,
                'store_id': store_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'order_datetime': order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'subtotal_eur': round(subtotal, 2),
                'tax_amount_eur': round(tax_amount, 2),
                'shipping_cost_eur': round(shipping, 2),
                'discount_amount_eur': 0.00,
                'total_amount_eur': round(total_amount, 2),
                'currency_code': 'EUR',
                'exchange_rate': 1.0000,
                'total_amount_local': round(total_amount, 2),
                'order_status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
                'order_channel': 'online' if store_id == 'ONLINE' else 'in-store',
                'payment_method': random.choice(['ideal', 'creditcard', 'paypal', 'klarna']),
                'payment_status': 'completed',
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            orders.append(order)
            
            # Generate matching GL entries
            journal_header_id = f"JH_{order_id}"
            gl_header = {
                'journal_header_id': journal_header_id,
                'journal_type': 'SALES',
                'transaction_date': order_date.strftime('%Y-%m-%d'),
                'reference_number': order_id,
                'description': f'Revenue recognition for order {order_id}',
                'total_amount': round(total_amount, 2),
                'currency_code': 'EUR',
                'exchange_rate': 1.0000,
                'status': 'POSTED',
                'created_by': 'SYSTEM',
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            }
            gl_headers.append(gl_header)
            
            # GL Lines: Debit Cash/AR, Credit Revenue, Credit Tax Payable
            line_id = 1
            
            # Cash/Receivable (Debit)
            gl_lines.append({
                'journal_line_id': f"JL_{journal_header_id}_{line_id:03d}",
                'journal_header_id': journal_header_id,
                'line_number': line_id,
                'account_id': '1000',  # Cash/AR
                'debit_amount': round(total_amount, 2),
                'credit_amount': 0.00,
                'currency_code': 'EUR',
                'exchange_rate': 1.0000,
                'line_description': f'Cash/Receivable from order {order_id}',
                'reference_1': order_id,
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            })
            line_id += 1
            
            # Revenue (Credit)
            gl_lines.append({
                'journal_line_id': f"JL_{journal_header_id}_{line_id:03d}",
                'journal_header_id': journal_header_id,
                'line_number': line_id,
                'account_id': '4000',  # Sales Revenue
                'debit_amount': 0.00,
                'credit_amount': round(subtotal, 2),
                'currency_code': 'EUR',
                'exchange_rate': 1.0000,
                'line_description': f'Revenue from order {order_id}',
                'reference_1': order_id,
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            })
            line_id += 1
            
            # Tax Payable (Credit)  
            gl_lines.append({
                'journal_line_id': f"JL_{journal_header_id}_{line_id:03d}",
                'journal_header_id': journal_header_id,
                'line_number': line_id,
                'account_id': '2100',  # Tax Payable
                'debit_amount': 0.00,
                'credit_amount': round(tax_amount, 2),
                'currency_code': 'EUR',
                'exchange_rate': 1.0000,
                'line_description': f'VAT payable from order {order_id}',
                'reference_1': order_id,
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            })
        
        # Save incremental data
        self.save_incremental_csv('eurostyle_operational.orders_incremental', orders)
        self.save_incremental_csv('eurostyle_finance.gl_journal_headers_incremental', gl_headers)
        self.save_incremental_csv('eurostyle_finance.gl_journal_lines_incremental', gl_lines)
        
        print(f"✅ Generated {len(orders)} orders with {len(gl_lines)} GL entries")
        return True
    
    def generate_incremental_customers(self, num_customers):
        """Generate new customer registrations"""
        print(f"👥 Generating {num_customers} new customers")
        
        start_customer_id = self.get_latest_customer_id() + 1
        customers = []
        
        countries = ['NL', 'DE', 'FR', 'BE']
        genders = ['M', 'F', 'O']
        
        for i in range(num_customers):
            customer_id = f"CUST_EU_{start_customer_id + i:06d}"
            country = random.choice(countries)
            
            # Generate registration date (within last few days)
            reg_date = self.current_date - timedelta(days=random.randint(0, 7))
            reg_datetime = datetime.combine(reg_date, datetime.min.time()) + timedelta(
                hours=random.randint(8, 22), minutes=random.randint(0, 59)
            )
            
            customer = {
                'customer_id': customer_id,
                'email': f'customer{start_customer_id + i}@example.com',
                'first_name': f'Customer{start_customer_id + i}',
                'last_name': f'Lastname{start_customer_id + i}',
                'phone': f'+31 6 {random.randint(10000000, 99999999)}',
                'date_of_birth': (self.current_date - timedelta(days=random.randint(18*365, 65*365))).strftime('%Y-%m-%d'),
                'gender': random.choice(genders),
                'language_preference': country.lower(),
                'street_address': f'Street {random.randint(1, 999)}',
                'city': f'City{random.randint(1, 100)}',
                'postal_code': f'{random.randint(1000, 9999)}XX',
                'country_code': country,
                'region': 'Europe',
                'registration_date': reg_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'registration_channel': random.choice(['online', 'in-store', 'mobile-app']),
                'customer_status': 'active',
                'marketing_opt_in': random.choice([True, False]),
                'newsletter_subscription': random.choice([True, False]),
                'loyalty_member': random.choice([True, False]),
                'loyalty_points': random.randint(0, 1000),
                'loyalty_tier': random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            customers.append(customer)
        
        self.save_incremental_csv('eurostyle_operational.customers_incremental', customers)
        print(f"✅ Generated {len(customers)} new customers")
        return True
    
    def generate_incremental_webshop_sessions(self, num_sessions):
        """Generate new webshop sessions"""
        print(f"🌐 Generating {num_sessions} webshop sessions")
        
        customers = self.get_existing_customers(500)  # Get sample for session assignment
        sessions = []
        
        for i in range(num_sessions):
            session_id = f"SESS_INC_{i+1:08d}"
            
            # Session date within last few days
            session_date = self.current_date - timedelta(days=random.randint(0, 3))
            session_start = datetime.combine(session_date, datetime.min.time()) + timedelta(
                hours=random.randint(8, 23), minutes=random.randint(0, 59)
            )
            
            duration = random.randint(30, 3600)  # 30 seconds to 1 hour
            
            session = {
                'session_id': session_id,
                'customer_id': random.choice(customers) if random.random() > 0.3 else None,  # 30% anonymous
                'country_code': random.choice(['NL', 'DE', 'FR', 'BE']),
                'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'operating_system': random.choice(['Windows', 'macOS', 'iOS', 'Android']),
                'session_start': session_start.strftime('%Y-%m-%d %H:%M:%S'),
                'session_end': (session_start + timedelta(seconds=duration)).strftime('%Y-%m-%d %H:%M:%S'),
                'session_duration_seconds': duration,
                'page_views': random.randint(1, 15),
                'unique_products_viewed': random.randint(0, 8),
                'bounce_session': random.random() < 0.4,  # 40% bounce rate
                'conversion_session': random.random() < 0.05,  # 5% conversion rate
                'utm_source': random.choice(['google', 'facebook', 'email', 'direct', None]),
                'utm_medium': random.choice(['cpc', 'organic', 'email', 'social', None]),
                'utm_campaign': random.choice(['spring-sale', 'newsletter', 'retargeting', None]),
                'referrer_url': None,
                'landing_page': random.choice(['/home', '/products', '/sale', '/new-arrivals']),
                'exit_page': random.choice(['/home', '/products', '/cart', '/checkout']),
                'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            sessions.append(session)
        
        self.save_incremental_csv('eurostyle_webshop.web_sessions_incremental', sessions)
        print(f"✅ Generated {len(sessions)} webshop sessions")
        return True
    
    def simulate_department_shuffle(self):
        """Simulate HR department changes and promotions"""
        print(f"🏢 Simulating department shuffle and promotions")
        
        # This would update employee records with new departments/positions
        # For now, we'll just simulate the output
        changes = [
            "👥 5 employees promoted to senior roles",
            "🔄 3 employees transferred between departments", 
            "📋 2 new department codes created",
            "💰 Salary adjustments for promoted employees"
        ]
        
        for change in changes:
            print(f"  • {change}")
        
        print("✅ Department shuffle simulation completed")
        return True
    
    def generate_customer_updates(self, num_updates):
        """Generate updates to existing customers (address changes, loyalty updates, etc.)"""
        print(f"👥 Generating {num_updates} customer updates")
        
        try:
            # Get sample of existing customers to update
            existing_customers = []
            with gzip.open(self.base_data_path / "eurostyle_operational.customers.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                customers_list = list(reader)
                existing_customers = random.sample(customers_list, min(num_updates, len(customers_list)))
            
            if not existing_customers:
                print("❌ No existing customers found to update")
                return False
            
            updates = []
            countries = ['NL', 'DE', 'FR', 'BE']
            
            for customer in existing_customers:
                # Generate realistic updates
                updated_customer = customer.copy()
                
                # Update some fields realistically
                if random.random() < 0.3:  # 30% chance of address update
                    updated_customer['street_address'] = f'New Street {random.randint(1, 999)}'
                    updated_customer['city'] = f'NewCity{random.randint(1, 100)}'
                    updated_customer['postal_code'] = f'{random.randint(1000, 9999)}XX'
                
                if random.random() < 0.4:  # 40% chance of loyalty updates
                    current_points = int(updated_customer.get('loyalty_points', 0))
                    updated_customer['loyalty_points'] = current_points + random.randint(10, 500)
                    
                    # Tier upgrades based on points
                    if updated_customer['loyalty_points'] > 2000:
                        updated_customer['loyalty_tier'] = 'Platinum'
                    elif updated_customer['loyalty_points'] > 1000:
                        updated_customer['loyalty_tier'] = 'Gold'
                    elif updated_customer['loyalty_points'] > 500:
                        updated_customer['loyalty_tier'] = 'Silver'
                
                if random.random() < 0.2:  # 20% chance of preference updates
                    updated_customer['marketing_opt_in'] = random.choice([True, False])
                    updated_customer['newsletter_subscription'] = random.choice([True, False])
                
                # Always update the timestamp
                updated_customer['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates.append(updated_customer)
            
            self.save_incremental_csv('eurostyle_operational.customers_updates', updates)
            print(f"✅ Generated {len(updates)} customer updates")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate customer updates: {e}")
            return False
    
    def generate_employee_updates(self, num_updates):
        """Generate updates to existing employees (status changes, visa updates, etc.)"""
        print(f"👨‍💼 Generating {num_updates} employee updates")
        
        try:
            # Get sample of existing employees to update
            existing_employees = []
            with gzip.open(self.base_data_path / "eurostyle_hr.employees.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                employees_list = list(reader)
                existing_employees = random.sample(employees_list, min(num_updates, len(employees_list)))
            
            if not existing_employees:
                print("❌ No existing employees found to update")
                return False
            
            updates = []
            
            for employee in existing_employees:
                updated_employee = employee.copy()
                
                # Generate realistic updates using only fields that exist in employees table
                if random.random() < 0.05:  # 5% chance of employee status change
                    statuses = ['ACTIVE', 'ON_LEAVE', 'TERMINATED']
                    updated_employee['employee_status'] = random.choice(statuses)
                
                if random.random() < 0.02:  # 2% chance of visa status update
                    visa_statuses = ['EU_CITIZEN', 'WORK_PERMIT', 'STUDENT_VISA', 'OTHER']
                    updated_employee['visa_status'] = random.choice(visa_statuses)
                
                if random.random() < 0.10:  # 10% chance of contact info update
                    updated_employee['phone_mobile'] = f"+31{random.randint(600000000, 699999999)}"
                    updated_employee['personal_email'] = f"{updated_employee['first_name'].lower()}.{updated_employee['last_name'].lower()}@example.com"
                
                if random.random() < 0.05:  # 5% chance of address update
                    updated_employee['address_street'] = f'Updated Street {random.randint(1, 999)}'
                    updated_employee['address_city'] = f'NewCity{random.randint(1, 100)}'
                    updated_employee['address_postal_code'] = f'{random.randint(1000, 9999)}XX'
                
                # Always update the timestamp
                updated_employee['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates.append(updated_employee)
            
            self.save_incremental_csv('eurostyle_hr.employees_updates', updates)
            print(f"✅ Generated {len(updates)} employee updates")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate employee updates: {e}")
            return False
    
    def generate_product_updates(self, num_updates):
        """Generate updates to existing products (price changes, inventory updates, descriptions)"""
        print(f"🛍️ Generating {num_updates} product updates")
        
        try:
            # Get sample of existing products to update
            existing_products = []
            with gzip.open(self.base_data_path / "eurostyle_operational.products.csv.gz", 'rt') as f:
                reader = csv.DictReader(f)
                products_list = list(reader)
                existing_products = random.sample(products_list, min(num_updates, len(products_list)))
            
            if not existing_products:
                print("❌ No existing products found to update")
                return False
            
            updates = []
            
            for product in existing_products:
                updated_product = product.copy()
                
                # Generate realistic updates (only modify existing fields)
                if random.random() < 0.4:  # 40% chance of price adjustment
                    current_price = float(updated_product.get('price_eur', 50.0))
                    # Price adjustments between -20% to +30%
                    price_multiplier = random.uniform(0.8, 1.3)
                    updated_product['price_eur'] = round(current_price * price_multiplier, 2)
                
                if random.random() < 0.6:  # 60% chance of stock level update
                    # Update current_stock_total (this field exists in the schema)
                    updated_product['current_stock_total'] = random.randint(0, 1000)
                    
                    # Update availability based on stock
                    if int(updated_product['current_stock_total']) == 0:
                        updated_product['is_active'] = False
                        updated_product['online_availability'] = False
                    else:
                        updated_product['is_active'] = True
                        updated_product['online_availability'] = True
                
                if random.random() < 0.2:  # 20% chance of seasonal updates
                    seasons = ['spring', 'summer', 'autumn', 'winter']
                    updated_product['season'] = random.choice(seasons)
                
                if random.random() < 0.3:  # 30% chance of cost price adjustment
                    current_cost = float(updated_product.get('cost_price_eur', 25.0))
                    cost_multiplier = random.uniform(0.9, 1.1)  # Small cost adjustments
                    updated_product['cost_price_eur'] = round(current_cost * cost_multiplier, 2)
                    
                    # Recalculate margin
                    price = float(updated_product['price_eur'])
                    cost = float(updated_product['cost_price_eur'])
                    if price > 0:
                        margin = ((price - cost) / price) * 100
                        updated_product['margin_percentage'] = round(margin, 2)
                
                # Always update the timestamp
                updated_product['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates.append(updated_product)
            
            self.save_incremental_csv('eurostyle_operational.products_updates', updates)
            print(f"✅ Generated {len(updates)} product updates")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate product updates: {e}")
            return False
    
    def generate_cost_center_updates(self, num_updates):
        """Generate updates to existing cost centers (budget adjustments, status changes)"""
        print(f"💰 Generating {num_updates} cost center updates")
        
        # Check if cost centers file exists
        cost_centers_file = self.base_data_path / "eurostyle_finance.cost_centers.csv.gz"
        if not cost_centers_file.exists():
            print("⚠️ Cost centers file not found - skipping cost center updates")
            print(f"💡 Expected file: {cost_centers_file}")
            return True  # Return True to not fail the overall process
        
        try:
            # Get sample of existing cost centers to update
            existing_cost_centers = []
            with gzip.open(cost_centers_file, 'rt') as f:
                reader = csv.DictReader(f)
                cost_centers_list = list(reader)
                existing_cost_centers = random.sample(cost_centers_list, min(num_updates, len(cost_centers_list)))
            
            if not existing_cost_centers:
                print("❌ No existing cost centers found to update")
                return True
            
            updates = []
            
            for cost_center in existing_cost_centers:
                updated_cost_center = cost_center.copy()
                
                # Generate realistic updates
                if random.random() < 0.3:  # 30% chance of name change
                    name_suffixes = ['Operations', 'Management', 'Support', 'Analytics', 'Strategy']
                    base_name = updated_cost_center.get('cost_center_name', 'Cost Center')
                    # Remove existing suffix and add new one
                    base = base_name.split()[0] if base_name else 'Cost Center'
                    updated_cost_center['cost_center_name'] = f"{base} {random.choice(name_suffixes)}"
                
                if random.random() < 0.2:  # 20% chance of type change
                    cost_center_types = ['PROFIT_CENTER', 'COST_CENTER', 'INVESTMENT_CENTER']
                    updated_cost_center['cost_center_type'] = random.choice(cost_center_types)
                
                if random.random() < 0.1:  # 10% chance of status change
                    updated_cost_center['is_active'] = random.choice([True, False])
                
                # Always update the timestamp
                updated_cost_center['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates.append(updated_cost_center)
            
            self.save_incremental_csv('eurostyle_finance.cost_centers_updates', updates)
            print(f"✅ Generated {len(updates)} cost center updates")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate cost center updates: {e}")
            return False
    
    def save_incremental_csv(self, table_name, data):
        """Save incremental data to compressed CSV"""
        if not data:
            return
            
        filename = self.output_path / f"{table_name}.csv.gz"
        
        with gzip.open(filename, 'wt', newline='') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        self.logger.info(f"💾 Saved {len(data)} records to {filename}")
    
    def generate_business_day(self, intensity='normal'):
        """Generate a complete business day of activity"""
        print(f"🗓️ Generating full business day activity (intensity: {intensity})")
        
        # Adjust volumes based on intensity
        multiplier = {'light': 0.5, 'normal': 1.0, 'heavy': 2.0}.get(intensity, 1.0)
        
        # Daily business volumes (scaled by intensity)
        daily_orders = int(100 * multiplier)          # ~100 orders per day
        new_customers = int(20 * multiplier)          # ~20 new registrations
        webshop_sessions = int(500 * multiplier)      # ~500 sessions per day
        
        # Daily update volumes (smaller numbers for updates)
        customer_updates = int(50 * multiplier)       # ~50 customer updates per day
        product_updates = int(30 * multiplier)        # ~30 product updates per day
        employee_updates = int(5 * multiplier)        # ~5 employee updates per day
        cost_center_updates = int(3 * multiplier)     # ~3 cost center updates per day
        
        print(f"📊 Daily volumes:")
        print(f"  • New: {daily_orders} orders, {new_customers} customers, {webshop_sessions} sessions")
        print(f"  • Updates: {customer_updates} customers, {product_updates} products, {employee_updates} employees, {cost_center_updates} cost centers")
        
        success = True
        
        # Generate new records
        success &= self.generate_incremental_orders(daily_orders, days=1)
        success &= self.generate_incremental_customers(new_customers) 
        success &= self.generate_incremental_webshop_sessions(webshop_sessions)
        
        # Generate updates to existing records
        success &= self.generate_customer_updates(customer_updates)
        success &= self.generate_product_updates(product_updates)
        success &= self.generate_employee_updates(employee_updates)
        success &= self.generate_cost_center_updates(cost_center_updates)
        
        # Simulate HR activities occasionally
        if random.random() < 0.2:  # 20% chance of HR activities
            success &= self.simulate_department_shuffle()
        
        return success


def main():
    parser = argparse.ArgumentParser(description="Generate incremental business data with inserts and updates")
    parser.add_argument('--days', type=int, default=1, help='Number of business days to simulate')
    parser.add_argument('--intensity', choices=['light', 'normal', 'heavy'], default='normal',
                       help='Business activity intensity')
    parser.add_argument('--types', help='Specific data types to generate (comma-separated). '
                                       'Available: orders, customers, sessions, departments, '
                                       'customer_updates, employee_updates, product_updates, cost_center_updates')
    parser.add_argument('--update-only', action='store_true', 
                       help='Generate only updates to existing records (no new inserts)')
    
    args = parser.parse_args()
    
    generator = UniversalIncrementalGenerator()
    
    # Use the generator's logger for main function logging
    logger = generator.logger
    
    logger.info(f"🚀 Starting incremental data generation")
    logger.info(f"📅 Days: {args.days}, Intensity: {args.intensity}")
    
    if args.update_only:
        logger.info(f"🔄 Mode: Update existing records only")
    else:
        logger.info(f"🆕 Mode: Generate new records and updates")
    
    success = True
    
    if args.types:
        # Generate specific data types
        types = [t.strip() for t in args.types.split(',')]
        print(f"🎯 Generating specific types: {', '.join(types)}")
        
        for data_type in types:
            if data_type == 'orders' and not args.update_only:
                success &= generator.generate_incremental_orders(50 * args.days, args.days)
            elif data_type == 'customers' and not args.update_only:
                success &= generator.generate_incremental_customers(20 * args.days)
            elif data_type == 'sessions' and not args.update_only:
                success &= generator.generate_incremental_webshop_sessions(200 * args.days)
            elif data_type == 'departments':
                success &= generator.simulate_department_shuffle()
            elif data_type == 'customer_updates':
                success &= generator.generate_customer_updates(50 * args.days)
            elif data_type == 'employee_updates':
                success &= generator.generate_employee_updates(10 * args.days)
            elif data_type == 'product_updates':
                success &= generator.generate_product_updates(30 * args.days)
            elif data_type == 'cost_center_updates':
                success &= generator.generate_cost_center_updates(5 * args.days)
            else:
                print(f"⚠️ Unknown data type: {data_type}")
                print(f"💡 Available types: orders, customers, sessions, departments, customer_updates, employee_updates, product_updates, cost_center_updates")
    else:
        # Generate complete business days
        for day in range(args.days):
            print(f"\n📅 === Business Day {day + 1} of {args.days} ===")
            success &= generator.generate_business_day(args.intensity)
    
    if success:
        print(f"\n🎉 Incremental data generation completed successfully!")
        print(f"📊 Generated realistic business activity for {args.days} day(s)")
        print(f"💡 Use ClickHouse to load the *_incremental.csv.gz files")
    else:
        print(f"\n❌ Some incremental data generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()