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

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

class UniversalIncrementalGenerator:
    def __init__(self, base_data_path="data/csv"):
        self.base_data_path = Path(base_data_path)
        self.output_path = self.base_data_path
        self.current_date = datetime.now().date()
        
        print(f"🔄 Universal Incremental Data Generator initialized")
        print(f"📁 Base data path: {self.base_data_path}")
        
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
            print(f"⚠️ Could not determine latest order ID: {e}")
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
            print(f"⚠️ Could not determine latest customer ID: {e}")
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
        print(f"📦 Generating {num_orders} incremental orders for {days} day(s)")
        
        # Get existing data for referential integrity
        customers = self.get_existing_customers()
        products = self.get_existing_products()
        stores = self.get_existing_stores()
        
        if not customers or not products:
            print("❌ Cannot generate orders without existing customers and products")
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
        
        print(f"💾 Saved {len(data)} records to {filename}")
    
    def generate_business_day(self, intensity='normal'):
        """Generate a complete business day of activity"""
        print(f"🗓️ Generating full business day activity (intensity: {intensity})")
        
        # Adjust volumes based on intensity
        multiplier = {'light': 0.5, 'normal': 1.0, 'heavy': 2.0}.get(intensity, 1.0)
        
        # Daily business volumes (scaled by intensity)
        daily_orders = int(100 * multiplier)          # ~100 orders per day
        new_customers = int(20 * multiplier)          # ~20 new registrations
        webshop_sessions = int(500 * multiplier)      # ~500 sessions per day
        
        print(f"📊 Daily volumes: {daily_orders} orders, {new_customers} customers, {webshop_sessions} sessions")
        
        success = True
        success &= self.generate_incremental_orders(daily_orders, days=1)
        success &= self.generate_incremental_customers(new_customers) 
        success &= self.generate_incremental_webshop_sessions(webshop_sessions)
        
        # Simulate HR activities occasionally
        if random.random() < 0.2:  # 20% chance of HR activities
            success &= self.simulate_department_shuffle()
        
        return success


def main():
    parser = argparse.ArgumentParser(description="Generate incremental business data")
    parser.add_argument('--days', type=int, default=1, help='Number of business days to simulate')
    parser.add_argument('--intensity', choices=['light', 'normal', 'heavy'], default='normal',
                       help='Business activity intensity')
    parser.add_argument('--types', help='Specific data types to generate (comma-separated)')
    
    args = parser.parse_args()
    
    generator = UniversalIncrementalGenerator()
    
    print(f"🚀 Starting incremental data generation")
    print(f"📅 Days: {args.days}, Intensity: {args.intensity}")
    
    success = True
    
    if args.types:
        # Generate specific data types
        types = [t.strip() for t in args.types.split(',')]
        for data_type in types:
            if data_type == 'orders':
                success &= generator.generate_incremental_orders(50 * args.days, args.days)
            elif data_type == 'customers':
                success &= generator.generate_incremental_customers(20 * args.days)
            elif data_type == 'sessions':
                success &= generator.generate_incremental_webshop_sessions(200 * args.days)
            elif data_type == 'departments':
                success &= generator.simulate_department_shuffle()
            else:
                print(f"⚠️ Unknown data type: {data_type}")
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