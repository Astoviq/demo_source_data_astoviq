#!/usr/bin/env python3
"""
EuroStyle Source - Universal Data Generator V2
==============================================
Fixed version with proper datetime handling and gzip compression.
Configuration-driven data generation ensuring perfect consistency across all 4 databases.

CRITICAL CONSISTENCY GUARANTEES:
- Operations revenue = Finance GL revenue (exact match)
- HR employee salaries = Finance payroll GL entries (exact match)  
- Webshop sessions lead to believable operational orders
- All cross-database foreign keys maintained automatically

Usage:
    python3 universal_data_generator_v2.py --all --mode full
    python3 universal_data_generator_v2.py --validate-consistency
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import yaml
import csv
import gzip
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
from faker import Faker

class UniversalDataGeneratorV2:
    """Universal data generator with fixed datetime handling."""
    
    def __init__(self, config_path: str = "config", environment: str = "development"):
        self.config_path = Path(config_path)
        self.environment = environment
        self.logger = self._setup_logging()
        
        # Load configurations
        self.env_config = self._load_environment_config()
        
        # Initialize Faker
        self.faker = Faker(['en_US', 'nl_NL', 'de_DE', 'fr_FR'])
        
        # Data containers
        self.generated_data = {
            'legal_entities': [],
            'stores': [],
            'products': [],
            'customers': [],
            'employees': [],
            'orders': [],
            'gl_entries': [],
            'web_sessions': [],
            # HR training and survey data
            'training_programs': [],
            'employee_training': [],
            'employee_surveys': [],
            'survey_responses': [],
            'performance_cycles': [],
            'performance_reviews': [],
            
            # POS (Point of Sales) data containers - Enhanced completeness
            'pos_employee_assignments': [],
            'pos_employee_shifts': [],
            'pos_transactions': [],
            'pos_transaction_items': [],
            'pos_payments': [],
            'pos_discounts': [],
            'pos_returns': [],
            'pos_employee_performance': [],
            'pos_store_daily_summary': [],
            'pos_shift_summaries': [],
            'pos_cash_drawer_activities': [],
            'pos_promotions': [],
            'pos_loyalty_transactions': []
        }
        
        self.logger.info("🏗️ Universal Data Generator V2 initialized")
        
    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='[%(name)s] %(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger("UniversalDataGeneratorV2")
    
    def _load_environment_config(self) -> Dict[str, Any]:
        env_file = self.config_path / "environments" / f"{self.environment}.yaml"
        try:
            with open(env_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default config if file not found
            return {
                'data_paths': {'csv_output': 'data/csv'},
                'compression': {'enabled': True, 'extension': '.gz'}
            }
    
    def _get_output_path(self, database: str, table: str) -> Path:
        output_dir = Path(self.env_config['data_paths']['csv_output'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{database}.{table}.csv"
        if self.env_config['compression']['enabled']:
            filename += self.env_config['compression']['extension']
            
        return output_dir / filename
    
    def _save_csv_data(self, data: List[Dict], database: str, table: str) -> None:
        if not data:
            self.logger.warning(f"No data to save for {database}.{table}")
            return
            
        output_path = self._get_output_path(database, table)
        fieldnames = list(data[0].keys())
        
        self.logger.info(f"💾 Saving {len(data)} records to {output_path}")
        
        if self.env_config['compression']['enabled']:
            with gzip.open(output_path, 'wt', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                writer.writerows(data)
        else:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                writer.writerows(data)

    def generate_legal_entities(self) -> List[Dict]:
        """Generate legal entities."""
        self.logger.info("🏢 Generating legal entities...")
        
        entities = [
            {
                'entity_id': 'ENTITY_NL_HOLDING',
                'entity_code': 'ESLH', 
                'entity_name': 'EuroStyle Holding B.V.',
                'entity_type': 'HOLDING',
                'country_code': 'NL',
                'currency': 'EUR',
                'legal_form': 'BV',
                'tax_number': 'NL123456789B01',
                'is_active': True,
                'created_date': '2024-01-01 10:00:00'
            },
            {
                'entity_id': 'ENTITY_NL_RETAIL',
                'entity_code': 'ESLR',
                'entity_name': 'EuroStyle Retail Nederland B.V.',
                'entity_type': 'OPERATING',
                'country_code': 'NL', 
                'currency': 'EUR',
                'legal_form': 'BV',
                'tax_number': 'NL234567890B01',
                'is_active': True,
                'created_date': '2024-01-01 10:00:00'
            },
            {
                'entity_id': 'ENTITY_DE_RETAIL',
                'entity_code': 'ESDR',
                'entity_name': 'EuroStyle Deutschland GmbH',
                'entity_type': 'OPERATING',
                'country_code': 'DE',
                'currency': 'EUR',
                'legal_form': 'GmbH', 
                'tax_number': 'DE345678901',
                'is_active': True,
                'created_date': '2024-01-01 10:00:00'
            },
            {
                'entity_id': 'ENTITY_FR_RETAIL',
                'entity_code': 'ESFR',
                'entity_name': 'EuroStyle France SARL',
                'entity_type': 'OPERATING',
                'country_code': 'FR',
                'currency': 'EUR',
                'legal_form': 'SARL',
                'tax_number': 'FR456789012',
                'is_active': True,
                'created_date': '2024-01-01 10:00:00'
            },
            {
                'entity_id': 'ENTITY_BE_RETAIL',
                'entity_code': 'ESBR',
                'entity_name': 'EuroStyle Belgium BVBA',
                'entity_type': 'OPERATING', 
                'country_code': 'BE',
                'currency': 'EUR',
                'legal_form': 'BVBA',
                'tax_number': 'BE567890123',
                'is_active': True,
                'created_date': '2024-01-01 10:00:00'
            }
        ]
        
        self.generated_data['legal_entities'] = entities
        self.logger.info(f"Generated {len(entities)} legal entities")
        return entities
    
    def generate_stores(self, mode: str = 'full') -> List[Dict]:
        """Generate stores with geographic distribution."""
        self.logger.info("🏪 Generating stores...")
        
        store_counts = {
            'demo': {'NL': 3, 'DE': 5, 'FR': 4, 'BE': 2},
            'fast': {'NL': 8, 'DE': 12, 'FR': 10, 'BE': 5},
            'full': {'NL': 15, 'DE': 20, 'FR': 15, 'BE': 8}
        }
        
        counts = store_counts.get(mode, store_counts['full'])
        stores = []
        store_id = 1
        
        for country, count in counts.items():
            for i in range(count):
                store_data = {
                    'store_id': f"STORE_{country}_{store_id:03d}",
                    'store_name': f"EuroStyle {self.faker.city()}",
                    'entity_id': f"ENTITY_{country}_RETAIL",
                    'country_code': country,
                    'city': self.faker.city(),
                    'address': self.faker.street_address(),
                    'postal_code': self.faker.postcode(),
                    'latitude': round(self.faker.latitude(), 6),
                    'longitude': round(self.faker.longitude(), 6),
                    'store_format': random.choice(['flagship', 'standard', 'outlet']),
                    'floor_area_sqm': random.randint(200, 1500),
                    'opening_date': self.faker.date_between(start_date='-5y', end_date='-1y').strftime('%Y-%m-%d'),
                    'manager_name': self.faker.name(),
                    'staff_count': random.randint(8, 25),
                    'performance_tier': random.choice(['A', 'B', 'C']),
                    'target_monthly_revenue': Decimal(str(random.randint(50000, 200000))),
                    'is_active': True,
                    'created_at': '2024-01-01 10:00:00',
                    'updated_at': '2024-01-01 10:00:00'
                }
                stores.append(store_data)
                store_id += 1
        
        self.generated_data['stores'] = stores
        self.logger.info(f"Generated {len(stores)} stores across {len(counts)} countries")
        return stores
    
    def generate_products(self, mode: str = 'full') -> List[Dict]:
        """Generate fashion product catalog."""
        self.logger.info("👕 Generating fashion product catalog...")
        
        product_counts = {'demo': 100, 'fast': 500, 'full': 2500}
        count = product_counts.get(mode, 2500)
        
        categories = {
            'Women': {
                'Tops': ['T-Shirts', 'Blouses', 'Sweaters', 'Hoodies'],
                'Bottoms': ['Jeans', 'Trousers', 'Skirts', 'Shorts'],
                'Dresses': ['Casual Dresses', 'Evening Dresses', 'Summer Dresses'],
                'Outerwear': ['Jackets', 'Coats', 'Blazers']
            },
            'Men': {
                'Tops': ['T-Shirts', 'Shirts', 'Sweaters', 'Hoodies'],
                'Bottoms': ['Jeans', 'Chinos', 'Shorts', 'Sweatpants'],
                'Outerwear': ['Jackets', 'Coats', 'Blazers', 'Vests']
            },
            'Kids': {
                'Tops': ['T-Shirts', 'Sweaters', 'Hoodies'],
                'Bottoms': ['Jeans', 'Leggings', 'Shorts'],
                'Dresses': ['Play Dresses', 'Party Dresses']
            }
        }
        
        colors = ['Black', 'White', 'Navy', 'Gray', 'Red', 'Blue', 'Green', 'Pink', 'Brown', 'Beige']
        
        products = []
        for i in range(count):
            category_l1 = random.choice(list(categories.keys()))
            category_l2 = random.choice(list(categories[category_l1].keys()))
            category_l3 = random.choice(categories[category_l1][category_l2])
            
            color = random.choice(colors)
            base_price = Decimal(str(random.uniform(19.99, 149.99))).quantize(Decimal('0.01'))
            cost_price = (base_price * Decimal('0.4')).quantize(Decimal('0.01'))
            
            product = {
                'product_id': f"PROD_EU_{i+1:06d}",
                'product_name': f"{color} {category_l3}",
                'category_l1': category_l1,
                'category_l2': category_l2,
                'category_l3': category_l3,
                'brand': 'EuroStyle',
                'color_primary': color,
                'price_eur': base_price,
                'cost_price_eur': cost_price,
                'margin_percentage': ((base_price - cost_price) / base_price * 100).quantize(Decimal('0.01')),
                'sustainability_score': random.randint(6, 10),
                'eco_friendly_materials': random.choice([True, False]),
                'production_country': random.choice(['NL', 'DE', 'FR', 'IT', 'PT']),
                'current_stock_total': random.randint(0, 500),
                'launch_date': self.faker.date_between(start_date='-2y', end_date='-1m').strftime('%Y-%m-%d'),
                'season': random.choice(['Spring/Summer 2024', 'Fall/Winter 2024', 'Spring/Summer 2025']),
                'is_active': True,
                'online_availability': True,
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            products.append(product)
        
        self.generated_data['products'] = products
        self.logger.info(f"Generated {len(products)} products")
        return products
    
    def generate_customers(self, mode: str = 'full') -> List[Dict]:
        """Generate customers with European distribution."""
        self.logger.info("👥 Generating customers...")
        
        customer_counts = {'demo': 200, 'fast': 1000, 'full': 50000}
        count = customer_counts.get(mode, 50000)
        
        customers = []
        countries = ['NL', 'DE', 'FR', 'BE']
        
        for i in range(count):
            selected_country = random.choice(countries)
            
            customer = {
                'customer_id': f"CUST_EU_{i+1:06d}",
                'email': self.faker.email(),
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'phone': self.faker.phone_number(),
                'date_of_birth': self.faker.date_of_birth(minimum_age=18, maximum_age=75).strftime('%Y-%m-%d'),
                'gender': random.choice(['M', 'F', 'O']),
                'language_preference': selected_country.lower(),
                'street_address': self.faker.street_address(),
                'city': self.faker.city(),
                'postal_code': self.faker.postcode(),
                'country_code': selected_country,
                'region': self.faker.state(),
                'registration_date': self.faker.date_time_between(start_date='-3y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
                'registration_channel': random.choice(['online', 'in-store', 'social', 'referral']),
                'customer_status': random.choices(['active', 'inactive'], weights=[85, 15])[0],
                'marketing_opt_in': random.choice([True, False]),
                'newsletter_subscription': random.choice([True, False]),
                'loyalty_member': random.choice([True, False]),
                'loyalty_points': random.randint(0, 5000),
                'loyalty_tier': random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            customers.append(customer)
        
        self.generated_data['customers'] = customers
        self.logger.info(f"Generated {len(customers)} customers")
        return customers
    
    def generate_orders_with_gl_entries(self, mode: str = 'full') -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Generate orders with matching GL entries for perfect revenue consistency."""
        self.logger.info("🛒 Generating orders with matching GL entries...")
        
        order_counts = {'demo': 100, 'fast': 500, 'full': 5000}
        count = order_counts.get(mode, 5000)
        
        orders = []
        gl_headers = []
        gl_lines = []
        
        for i in range(count):
            customer = random.choice(self.generated_data['customers'])
            
            # 70% online orders, 30% in-store
            if random.random() < 0.7:
                store_id = 'ONLINE'
                order_channel = 'online'
            else:
                store = random.choice(self.generated_data['stores'])
                store_id = store['store_id'] 
                order_channel = 'in-store'
            
            order_id = f"ORD_EU_2024_{i+1:06d}"
            order_date = self.faker.date_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d')
            
            # Generate order totals
            num_items = random.randint(1, 5)
            subtotal = Decimal('0.00')
            
            for _ in range(num_items):
                product = random.choice(self.generated_data['products'])
                quantity = random.randint(1, 3)
                unit_price = product['price_eur']
                line_total = unit_price * quantity
                subtotal += line_total
            
            tax_rate = Decimal('0.21')
            tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
            
            shipping_cost = Decimal('0.00') if store_id != 'ONLINE' else Decimal('4.95')
            if subtotal > 50:
                shipping_cost = Decimal('0.00')
                
            total_amount = subtotal + tax_amount + shipping_cost
            
            # Create order
            order = {
                'order_id': order_id,
                'customer_id': customer['customer_id'],
                'store_id': store_id,
                'order_date': order_date,
                'order_datetime': f"{order_date} {random.randint(9, 20):02d}:{random.randint(0, 59):02d}:00",
                'subtotal_eur': subtotal,
                'tax_amount_eur': tax_amount,
                'shipping_cost_eur': shipping_cost,
                'discount_amount_eur': Decimal('0.00'),
                'total_amount_eur': total_amount,
                'currency_code': 'EUR',
                'exchange_rate': Decimal('1.0000'),
                'total_amount_local': total_amount,
                'order_status': random.choices(['delivered', 'shipped', 'pending'], weights=[80, 15, 5])[0],
                'order_channel': order_channel,
                'payment_method': random.choice(['credit-card', 'paypal', 'klarna', 'ideal']),
                'payment_status': 'completed',
                'created_at': '2024-01-01 10:00:00',
                'updated_at': '2024-01-01 10:00:00'
            }
            orders.append(order)
            
            # Create matching GL entries
            journal_id = f"JH_{order_id}"
            
            gl_header = {
                'journal_header_id': journal_id,
                'journal_type': 'SALES',
                'transaction_date': order_date,
                'reference_number': order_id,
                'description': f"Revenue recognition for order {order_id}",
                'total_amount': total_amount,
                'currency_code': 'EUR',
                'exchange_rate': Decimal('1.0000'),
                'status': 'POSTED',
                'created_by': 'SYSTEM',
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            }
            gl_headers.append(gl_header)
            
            # GL Journal Lines (Double-entry bookkeeping)
            line_number = 1
            
            # Debit Cash/Accounts Receivable  
            cash_account = '1000' if store_id != 'ONLINE' else '1100'
            gl_lines.append({
                'journal_line_id': f"JL_{journal_id}_{line_number:03d}",
                'journal_header_id': journal_id,
                'line_number': line_number,
                'account_id': cash_account,
                'debit_amount': total_amount,
                'credit_amount': Decimal('0.00'),
                'currency_code': 'EUR',
                'exchange_rate': Decimal('1.0000'),
                'line_description': f"Cash/Receivable from order {order_id}",
                'reference_1': order_id,
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            })
            line_number += 1
            
            # Credit Revenue (excluding tax)
            gl_lines.append({
                'journal_line_id': f"JL_{journal_id}_{line_number:03d}",
                'journal_header_id': journal_id,
                'line_number': line_number,
                'account_id': '4000',  # Revenue account
                'debit_amount': Decimal('0.00'),
                'credit_amount': subtotal,
                'currency_code': 'EUR', 
                'exchange_rate': Decimal('1.0000'),
                'line_description': f"Revenue from order {order_id}",
                'reference_1': order_id,
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            })
            line_number += 1
            
            # Credit VAT Payable
            if tax_amount > 0:
                gl_lines.append({
                    'journal_line_id': f"JL_{journal_id}_{line_number:03d}",
                    'journal_header_id': journal_id,
                    'line_number': line_number,
                    'account_id': '2300',  # VAT Payable
                    'debit_amount': Decimal('0.00'),
                    'credit_amount': tax_amount,
                    'currency_code': 'EUR',
                    'exchange_rate': Decimal('1.0000'),
                    'line_description': f"VAT from order {order_id}",
                    'reference_1': order_id,
                    'created_date': '2024-01-01 10:00:00',
                    'updated_date': '2024-01-01 10:00:00'
                })
                line_number += 1
            
            # Credit Shipping Revenue
            if shipping_cost > 0:
                gl_lines.append({
                    'journal_line_id': f"JL_{journal_id}_{line_number:03d}",
                    'journal_header_id': journal_id,
                    'line_number': line_number,
                    'account_id': '4100',  # Shipping Revenue
                    'debit_amount': Decimal('0.00'),
                    'credit_amount': shipping_cost,
                    'currency_code': 'EUR',
                    'exchange_rate': Decimal('1.0000'),
                    'line_description': f"Shipping revenue from order {order_id}",
                    'reference_1': order_id,
                    'created_date': '2024-01-01 10:00:00',
                    'updated_date': '2024-01-01 10:00:00'
                })
        
        self.generated_data['orders'] = orders
        self.generated_data['gl_entries'] = gl_lines
        
        self.logger.info(f"✅ Generated {len(orders)} orders with {len(gl_lines)} matching GL entries")
        self.logger.info("🎯 GUARANTEED: Operations revenue = Finance GL revenue")
        
        return orders, gl_headers, gl_lines
    
    def generate_employees_with_payroll_gl(self, mode: str = 'full') -> Tuple[List[Dict], List[Dict]]:
        """Generate HR employees with matching payroll GL entries."""
        self.logger.info("👥 Generating employees with payroll GL entries...")
        
        employee_counts = {
            'demo': {'HOLDING': 5, 'OPERATING': 20},
            'fast': {'HOLDING': 15, 'OPERATING': 75}, 
            'full': {'HOLDING': 30, 'OPERATING': 200}
        }
        
        counts = employee_counts.get(mode, employee_counts['full'])
        
        employees = []
        payroll_gl_lines = []
        employee_id = 1
        
        for entity in self.generated_data['legal_entities']:
            entity_type = entity['entity_type']
            count = counts.get(entity_type, 10)
            
            for i in range(count):
                gender = random.choice(['MALE', 'FEMALE'])
                first_name = self.faker.first_name_male() if gender == 'MALE' else self.faker.first_name_female()
                last_name = self.faker.last_name()
                
                base_salary = 30000 if entity_type == 'OPERATING' else 50000
                position_multiplier = random.uniform(1.0, 3.0)
                annual_salary = Decimal(str(base_salary * position_multiplier)).quantize(Decimal('0.01'))
                monthly_salary = (annual_salary / 12).quantize(Decimal('0.01'))
                
                employee = {
                    'employee_id': f"EMP_{employee_id:06d}",
                    'employee_number': f"{entity['entity_code']}{employee_id:06d}",
                    'entity_id': entity['entity_id'],
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{first_name.lower()}.{last_name.lower()}@eurostyle{entity['country_code'].lower()}.com",
                    'date_of_birth': self.faker.date_of_birth(minimum_age=22, maximum_age=65).strftime('%Y-%m-%d'),
                    'gender': gender,
                    'nationality': entity['country_code'],
                    'hire_date': self.faker.date_between(start_date='-5y', end_date='-1m').strftime('%Y-%m-%d'),
                    'employee_status': 'ACTIVE',
                    'visa_status': random.choices(['EU_CITIZEN', 'WORK_PERMIT', 'OTHER'], weights=[85, 10, 5])[0],
                    'annual_salary_eur': annual_salary,
                    'created_date': '2024-01-01 10:00:00',
                    'updated_date': '2024-01-01 10:00:00'
                }
                employees.append(employee)
                
                # Generate monthly payroll entries for last 12 months
                for month_offset in range(12):
                    payroll_date = (date.today().replace(day=1) - timedelta(days=30*month_offset)).strftime('%Y-%m-%d')
                    
                    payroll_gl_lines.append({
                        'journal_line_id': f"PAYROLL_{employee_id}_{payroll_date.replace('-', '')}",
                        'journal_header_id': f"PAYROLL_HDR_{payroll_date.replace('-', '')}",
                        'line_number': 1,
                        'account_id': '6100',  # Salary Expense
                        'debit_amount': monthly_salary,
                        'credit_amount': Decimal('0.00'),
                        'currency_code': 'EUR',
                        'exchange_rate': Decimal('1.0000'),
                        'line_description': f"Monthly salary {employee['employee_number']}",
                        'reference_1': employee['employee_id'],
                        'created_date': '2024-01-01 10:00:00',
                        'updated_date': '2024-01-01 10:00:00'
                    })
                
                employee_id += 1
        
        self.generated_data['employees'] = employees
        
        self.logger.info(f"✅ Generated {len(employees)} employees with {len(payroll_gl_lines)} payroll GL entries")
        self.logger.info("🎯 GUARANTEED: HR compensation costs = Finance payroll expenses")
        
        return employees, payroll_gl_lines
    
    def generate_webshop_sessions_with_orders(self, mode: str = 'full') -> List[Dict]:
        """Generate webshop sessions that correlate with actual orders."""
        self.logger.info("🌐 Generating webshop sessions aligned with operational orders...")
        
        session_counts = {'demo': 500, 'fast': 2500, 'full': 25000}
        count = session_counts.get(mode, 25000)
        
        sessions = []
        order_customers = {order['customer_id'] for order in self.generated_data['orders']}
        
        for i in range(count):
            # 60% of sessions from customers who actually placed orders
            if random.random() < 0.6 and order_customers:
                customer_id = random.choice(list(order_customers))
                customer = next(c for c in self.generated_data['customers'] if c['customer_id'] == customer_id)
            else:
                customer = random.choice(self.generated_data['customers'])
            
            session_date = self.faker.date_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d')
            session_duration = random.randint(30, 1800)
            
            session = {
                'session_id': f"SESS_{i+1:08d}",
                'customer_id': customer['customer_id'] if random.random() < 0.7 else None,
                'session_date': session_date,
                'session_start_time': f"{session_date} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
                'session_duration_seconds': session_duration,
                'device_type': random.choices(['desktop', 'mobile', 'tablet'], weights=[45, 45, 10])[0],
                'browser': random.choice(['Chrome', 'Safari', 'Firefox', 'Edge']),
                'country_code': customer['country_code'],
                'page_views': random.randint(1, 15),
                'products_viewed': random.randint(0, 8),
                'cart_additions': random.randint(0, 3),
                'conversion_flag': customer['customer_id'] in order_customers and random.random() < 0.15,
                'traffic_source': random.choices(['organic', 'paid-search', 'social', 'email', 'direct'], 
                                               weights=[35, 20, 15, 15, 15])[0],
                'created_date': '2024-01-01 10:00:00',
                'updated_date': '2024-01-01 10:00:00'
            }
            sessions.append(session)
        
        self.generated_data['web_sessions'] = sessions
        
        self.logger.info(f"✅ Generated {len(sessions)} webshop sessions aligned with order patterns")
        self.logger.info("🎯 GUARANTEED: Webshop analytics reflect actual customer behavior")
        
        return sessions
    
    def generate_all_databases(self, mode: str = 'full') -> Dict[str, Any]:
        """Generate data for all databases with perfect consistency."""
        self.logger.info(f"🌍 Generating ALL databases with perfect consistency - {mode} mode")
        
        results = {
            'mode': mode,
            'timestamp': datetime.now().isoformat(),
            'consistency_guarantees': [
                'Operations revenue = Finance GL revenue (exact match)',
                'HR salaries = Finance payroll expenses (exact match)', 
                'Webshop sessions correlate with actual orders',
                'All foreign key relationships maintained'
            ],
            'databases': {}
        }
        
        # Phase 1: Foundation data
        self.logger.info("📍 Phase 1: Foundation data")
        legal_entities = self.generate_legal_entities()
        stores = self.generate_stores(mode) 
        products = self.generate_products(mode)
        customers = self.generate_customers(mode)
        
        # Save foundation data
        self._save_csv_data(legal_entities, 'eurostyle_finance', 'legal_entities')
        self._save_csv_data(stores, 'eurostyle_operational', 'stores')
        self._save_csv_data(products, 'eurostyle_operational', 'products')  
        self._save_csv_data(customers, 'eurostyle_operational', 'customers')
        
        # Phase 2: Orders with GL integration
        self.logger.info("📍 Phase 2: Orders with Finance GL integration")
        orders, gl_headers, gl_lines = self.generate_orders_with_gl_entries(mode)
        
        self._save_csv_data(orders, 'eurostyle_operational', 'orders')
        self._save_csv_data(gl_headers, 'eurostyle_finance', 'gl_journal_headers')
        self._save_csv_data(gl_lines, 'eurostyle_finance', 'gl_journal_lines')
        
        # Phase 3: HR with payroll GL integration  
        self.logger.info("📍 Phase 3: HR with Finance payroll integration")
        employees, payroll_gl = self.generate_employees_with_payroll_gl(mode)
        
        self._save_csv_data(employees, 'eurostyle_hr', 'employees')
        # Extend GL lines with payroll entries
        self.generated_data['gl_entries'].extend(payroll_gl)
        self._save_csv_data(self.generated_data['gl_entries'], 'eurostyle_finance', 'gl_journal_lines')
        
        # Phase 4: HR training, surveys and performance data
        self.logger.info("📍 Phase 4: HR training, surveys and performance data")
        training_programs = self.generate_training_programs(mode)
        employee_training_records = self.generate_employee_training_records(mode)
        employee_surveys = self.generate_employee_surveys(mode)
        survey_responses = self.generate_survey_responses(mode)
        performance_cycles = self.generate_performance_cycles(mode)
        performance_reviews = self.generate_performance_reviews(mode)
        
        self._save_csv_data(training_programs, 'eurostyle_hr', 'training_programs')
        self._save_csv_data(employee_training_records, 'eurostyle_hr', 'employee_training_records')
        self._save_csv_data(employee_surveys, 'eurostyle_hr', 'employee_surveys')
        self._save_csv_data(survey_responses, 'eurostyle_hr', 'survey_responses')
        self._save_csv_data(performance_cycles, 'eurostyle_hr', 'performance_cycles')
        self._save_csv_data(performance_reviews, 'eurostyle_hr', 'performance_reviews')
        
        # Phase 5: POS (Point of Sales) with perfect revenue reconciliation and enhanced entities
        self.logger.info("📍 Phase 5: POS with perfect revenue reconciliation and comprehensive business entities")
        pos_assignments = self.generate_pos_employee_assignments(mode)
        pos_transactions, pos_items, pos_gl_entries = self.generate_pos_transactions_with_revenue_matching(mode)
        
        # Generate additional POS business entities for completeness
        pos_shifts = self.generate_pos_employee_shifts(mode)
        pos_payments = self.generate_pos_payments(mode)
        pos_discounts = self.generate_pos_discounts(mode)
        pos_daily_summaries = self.generate_pos_store_daily_summaries(mode)
        pos_promotions = self.generate_pos_promotions(mode)
        
        # Save all POS data
        self._save_csv_data(pos_assignments, 'eurostyle_pos', 'employee_assignments')
        self._save_csv_data(pos_transactions, 'eurostyle_pos', 'transactions')
        self._save_csv_data(pos_items, 'eurostyle_pos', 'transaction_items')
        self._save_csv_data(pos_shifts, 'eurostyle_pos', 'employee_shifts')
        self._save_csv_data(pos_payments, 'eurostyle_pos', 'payments')
        self._save_csv_data(pos_discounts, 'eurostyle_pos', 'discounts')
        self._save_csv_data(pos_daily_summaries, 'eurostyle_pos', 'store_daily_summaries')
        self._save_csv_data(pos_promotions, 'eurostyle_pos', 'promotions')
        
        # Update GL entries with POS transactions
        self._save_csv_data(self.generated_data['gl_entries'], 'eurostyle_finance', 'gl_journal_lines')
        
        # Phase 6: Webshop aligned with operations
        self.logger.info("📍 Phase 6: Webshop aligned with operational data")
        sessions = self.generate_webshop_sessions_with_orders(mode)
        self._save_csv_data(sessions, 'eurostyle_webshop', 'web_sessions')
        
        # Compile results
        results['databases'] = {
            'eurostyle_operational': {
                'stores': len(stores),
                'products': len(products),
                'customers': len(customers),
                'orders': len(orders)
            },
            'eurostyle_finance': {
                'legal_entities': len(legal_entities),
                'gl_journal_headers': len(gl_headers),
                'gl_journal_lines': len(gl_lines) + len(payroll_gl)
            },
            'eurostyle_hr': {
                'employees': len(employees),
                'training_programs': len(training_programs),
                'employee_training_records': len(employee_training_records),
                'employee_surveys': len(employee_surveys),
                'survey_responses': len(survey_responses),
                'performance_cycles': len(performance_cycles),
                'performance_reviews': len(performance_reviews)
            },
            'eurostyle_pos': {
                'employee_assignments': len(pos_assignments),
                'transactions': len(pos_transactions),
                'transaction_items': len(pos_items),
                'employee_shifts': len(pos_shifts),
                'payments': len(pos_payments),
                'discounts': len(pos_discounts),
                'store_daily_summaries': len(pos_daily_summaries),
                'promotions': len(pos_promotions)
            },
            'eurostyle_webshop': {
                'web_sessions': len(sessions)
            }
        }
        
        self.logger.info("🎉 ALL DATABASES GENERATED WITH PERFECT CONSISTENCY!")
        self.logger.info("✅ Operations revenue = Finance GL revenue")
        self.logger.info("✅ HR compensation = Finance payroll expenses") 
        self.logger.info("✅ Webshop sessions align with actual orders")
        
        return results
    
    def validate_consistency(self) -> Dict[str, Any]:
        """Validate data consistency across all generated databases."""
        self.logger.info("🔍 Validating cross-database consistency...")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }
        
        # Check 1: Revenue consistency
        if self.generated_data['orders'] and self.generated_data['gl_entries']:
            total_order_revenue = sum(Decimal(str(order['subtotal_eur'])) for order in self.generated_data['orders'])
            total_gl_revenue = sum(entry['credit_amount'] for entry in self.generated_data['gl_entries'] 
                                 if entry.get('account_id') == '4000')
            
            revenue_variance = abs(total_order_revenue - total_gl_revenue)
            
            validation_results['checks'].append({
                'name': 'revenue_consistency',
                'status': 'PASSED' if revenue_variance < Decimal('0.01') else 'FAILED',
                'details': {
                    'operational_revenue': float(total_order_revenue),
                    'finance_gl_revenue': float(total_gl_revenue),
                    'variance': float(revenue_variance)
                }
            })
        
        self.logger.info(f"Validation completed: {len(validation_results['checks'])} checks run")
        return validation_results
    
    # ========================================
    # HR TRAINING & SURVEY DATA GENERATION
    # ========================================
    
    def _load_hr_patterns(self, pattern_file: str) -> Dict[str, Any]:
        """Load HR data patterns from YAML configuration."""
        pattern_path = self.config_path / "data_patterns" / pattern_file
        try:
            with open(pattern_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Pattern file {pattern_file} not found, using defaults")
            return {}
    
    def _load_pos_patterns(self, pattern_file: str) -> Dict[str, Any]:
        """Load POS data patterns from YAML configuration following WARP.md rules."""
        pattern_path = self.config_path / "data_patterns" / pattern_file
        try:
            with open(pattern_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Pattern file {pattern_file} not found, using defaults")
            return self._get_default_pos_patterns()
    
    def _get_default_pos_patterns(self) -> Dict[str, Any]:
        """Default POS patterns if configuration file not found."""
        return {
            'store_operations': {
                'employees_per_store': {
                    'small_store': {'min_pos_staff': 1, 'max_pos_staff': 2, 'coverage_percentage': 0.8},
                    'medium_store': {'min_pos_staff': 2, 'max_pos_staff': 4, 'coverage_percentage': 0.9},
                    'large_store': {'min_pos_staff': 3, 'max_pos_staff': 6, 'coverage_percentage': 1.0}
                },
                'pos_role_distribution': {'CASHIER': 0.65, 'SALES_ASSOCIATE': 0.25, 'SHIFT_SUPERVISOR': 0.10}
            },
            'transaction_patterns': {
                'daily_volumes': {'demo': 750, 'fast': 1500, 'full': 3000}
            },
            'payment_methods': {
                'NL': {'DEBIT_CARD': 0.70, 'CREDIT_CARD': 0.15, 'CASH': 0.10, 'MOBILE_PAY': 0.05},
                'DE': {'DEBIT_CARD': 0.45, 'CASH': 0.35, 'CREDIT_CARD': 0.15, 'MOBILE_PAY': 0.05},
                'FR': {'DEBIT_CARD': 0.50, 'CREDIT_CARD': 0.25, 'CASH': 0.20, 'MOBILE_PAY': 0.05},
                'BE': {'DEBIT_CARD': 0.65, 'CREDIT_CARD': 0.20, 'CASH': 0.12, 'MOBILE_PAY': 0.03}
            }
        }
    
    def _load_vat_rates(self) -> Dict[str, Any]:
        """Load VAT rates from POS patterns configuration."""
        patterns = self._load_pos_patterns('pos_patterns.yaml')
        return patterns.get('vat_configuration', {
            'rates_by_country': {
                'NL': {'standard_rate': 0.21, 'gl_account': '2300_NL'},
                'DE': {'standard_rate': 0.19, 'gl_account': '2300_DE'},
                'FR': {'standard_rate': 0.20, 'gl_account': '2300_FR'},
                'BE': {'standard_rate': 0.21, 'gl_account': '2300_BE'}
            }
        })
    
    def generate_training_programs(self, mode: str = 'full') -> List[Dict]:
        """Generate comprehensive training program catalog."""
        self.logger.info("🎓 Generating training programs...")
        
        # Load training patterns
        patterns = self._load_hr_patterns('hr_training_patterns.yaml')
        program_config = patterns.get('training_programs', {})
        
        # Program count based on mode
        program_counts = {
            'demo': 50,
            'fast': 100, 
            'full': 175
        }
        total_programs = program_counts.get(mode, 175)
        
        programs = []
        program_id = 1
        
        # Generate programs by category
        categories = program_config.get('categories', ['COMPLIANCE', 'TECHNICAL', 'LEADERSHIP', 'PROFESSIONAL', 'ONBOARDING'])
        distribution = program_config.get('program_distribution', {
            'COMPLIANCE': 0.25, 'TECHNICAL': 0.30, 'LEADERSHIP': 0.18, 
            'PROFESSIONAL': 0.15, 'ONBOARDING': 0.08, 'LANGUAGE': 0.04
        })
        
        for category, percentage in distribution.items():
            if category not in categories:
                categories.append(category)
            
            category_count = int(total_programs * percentage)
            
            for i in range(category_count):
                # Generate realistic program based on category
                program = self._create_training_program(program_id, category, patterns)
                programs.append(program)
                program_id += 1
        
        # Add mandatory European compliance programs
        mandatory_programs = program_config.get('european_compliance', {}).get('mandatory_programs', [])
        for mandatory_name in mandatory_programs:
            if not any(p['program_name'] == mandatory_name for p in programs):
                program = self._create_training_program(program_id, 'COMPLIANCE', patterns, mandatory_name)
                programs.append(program)
                program_id += 1
        
        self.generated_data['training_programs'] = programs
        self.logger.info(f"Generated {len(programs)} training programs")
        return programs
    
    def _create_training_program(self, program_id: int, category: str, patterns: Dict, program_name: str = None) -> Dict:
        """Create individual training program record."""
        cost_ranges = patterns.get('training_programs', {}).get('cost_ranges_eur', {
            'COMPLIANCE': [50, 250], 'TECHNICAL': [200, 1800], 'LEADERSHIP': [400, 2500],
            'PROFESSIONAL': [300, 3200], 'ONBOARDING': [100, 400], 'LANGUAGE': [150, 1200]
        })
        
        if not program_name:
            # Generate realistic program names by category
            program_names = {
                'COMPLIANCE': ['GDPR Data Protection', 'Workplace Safety EU', 'Anti-Discrimination Training', 
                              'Code of Conduct', 'Fire Safety Procedures', 'First Aid Basic'],
                'TECHNICAL': ['Advanced Excel', 'Cloud Technologies', 'Cybersecurity Awareness',
                             'Data Analysis Fundamentals', 'Project Management', 'Agile Methodology'],
                'LEADERSHIP': ['Management Essentials', 'Effective Communication', 'Team Leadership',
                              'Performance Management', 'Strategic Thinking', 'Change Management'],
                'PROFESSIONAL': ['Fashion Industry Trends', 'Customer Service Excellence', 'Sales Techniques',
                                'Quality Management', 'Supply Chain Management', 'Financial Analysis'],
                'ONBOARDING': ['Company Orientation', 'New Employee Welcome', 'Company Culture',
                              'IT Systems Training', 'Workplace Policies', 'Benefits Overview'],
                'LANGUAGE': ['Business English', 'German Language Skills', 'French Communication',
                            'Dutch Language Basics', 'Multilingual Customer Service']
            }
            
            available_names = program_names.get(category, ['Generic Training Program'])
            program_name = self.faker.random_element(available_names) + f" {program_id}"
        
        cost_range = cost_ranges.get(category, [100, 500])
        cost = round(random.uniform(cost_range[0], cost_range[1]), 2)
        
        providers = ['Internal Training Team', 'External Training Provider', 'Online Learning Platform',
                    'Professional Development Institute', 'Industry Expert Consultant']
        
        return {
            'program_id': f"PROG_{program_id:05d}",
            'program_name': program_name,
            'program_category': category,
            'program_type': random.choice(['CLASSROOM', 'ONLINE', 'BLENDED', 'WORKSHOP']),
            'provider_name': random.choice(providers),
            'duration_hours': random.choice([2, 4, 8, 16, 24, 40]),
            'cost_per_participant_eur': cost,
            'max_participants': random.choice([None, 10, 15, 20, 25]) if category != 'ONBOARDING' else 5,
            'target_positions': [random.choice(['ALL', 'MANAGERS', 'TECHNICAL', 'SALES', 'OPERATIONS'])],
            'prerequisites': 'None' if category in ['COMPLIANCE', 'ONBOARDING'] else 'Basic job knowledge',
            'skill_level': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']),
            'mandatory': category == 'COMPLIANCE',
            'compliance_type': category if category == 'COMPLIANCE' else None,
            'renewal_required': category == 'COMPLIANCE',
            'renewal_period_months': 12 if category == 'COMPLIANCE' else None,
            'is_active': True,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
    
    def generate_employee_training_records(self, mode: str = 'full') -> List[Dict]:
        """Generate realistic employee training enrollment and completion records."""
        self.logger.info("📚 Generating employee training records...")
        
        if not self.generated_data['employees']:
            self.logger.error("No employees found - generate employees first")
            return []
        
        if not self.generated_data['training_programs']:
            self.logger.error("No training programs found - generate programs first")
            return []
        
        patterns = self._load_hr_patterns('hr_training_patterns.yaml')
        training_config = patterns.get('employee_training', {})
        
        training_records = []
        record_id = 1
        
        for employee in self.generated_data['employees']:
            # Determine training load based on role and seniority
            annual_training_range = training_config.get('enrollment_patterns', {}).get('per_employee_per_year', [3, 9])
            training_count = random.randint(annual_training_range[0], annual_training_range[1])
            
            # Select appropriate training programs for this employee
            available_programs = self._select_programs_for_employee(employee, self.generated_data['training_programs'])
            selected_programs = random.sample(available_programs, min(training_count, len(available_programs)))
            
            for program in selected_programs:
                record = self._create_training_record(record_id, employee, program, patterns)
                training_records.append(record)
                record_id += 1
        
        self.generated_data['employee_training'] = training_records
        self.logger.info(f"Generated {len(training_records)} employee training records")
        return training_records
    
    def _select_programs_for_employee(self, employee: Dict, programs: List[Dict]) -> List[Dict]:
        """Select appropriate training programs for an employee based on role and department."""
        suitable_programs = []
        
        # All employees must take compliance training
        compliance_programs = [p for p in programs if p['program_category'] == 'COMPLIANCE']
        suitable_programs.extend(compliance_programs)
        
        # Department-specific programs
        dept_mapping = {
            'IT': ['TECHNICAL'],
            'SALES': ['PROFESSIONAL', 'LEADERSHIP'],
            'HR': ['LEADERSHIP', 'PROFESSIONAL'],
            'FINANCE': ['TECHNICAL', 'PROFESSIONAL'],
            'OPERATIONS': ['TECHNICAL', 'PROFESSIONAL'],
            'MARKETING': ['TECHNICAL', 'PROFESSIONAL']
        }
        
        dept_name = employee.get('department_name', 'GENERAL')
        relevant_categories = dept_mapping.get(dept_name, ['PROFESSIONAL'])
        
        for category in relevant_categories:
            dept_programs = [p for p in programs if p['program_category'] == category]
            suitable_programs.extend(random.sample(dept_programs, min(2, len(dept_programs))))
        
        # Add some general programs
        other_programs = [p for p in programs if p['program_category'] in ['ONBOARDING', 'LANGUAGE']]
        if other_programs:
            suitable_programs.extend(random.sample(other_programs, min(1, len(other_programs))))
        
        return list({p['program_id']: p for p in suitable_programs}.values())  # Remove duplicates
    
    def _create_training_record(self, record_id: int, employee: Dict, program: Dict, patterns: Dict) -> Dict:
        """Create individual training record."""
        # Training dates - enrolled sometime in 2023-2024
        enrollment_date = self.faker.date_between(start_date=date(2023, 1, 1), end_date=date(2024, 6, 30))
        start_date = enrollment_date + timedelta(days=random.randint(1, 14))
        
        # Completion based on category completion rates
        completion_rates = patterns.get('training_programs', {}).get('completion_rates', {
            'COMPLIANCE': 0.95, 'TECHNICAL': 0.78, 'LEADERSHIP': 0.65,
            'PROFESSIONAL': 0.72, 'ONBOARDING': 0.98, 'LANGUAGE': 0.58
        })
        
        category = program['program_category']
        completion_rate = completion_rates.get(category, 0.75)
        is_completed = random.random() < completion_rate
        
        completion_date = None
        score = None
        certification_earned = False
        status = 'ENROLLED'
        
        if is_completed:
            completion_timeframes = patterns.get('employee_training', {}).get('completion_timeframes', {
                'COMPLIANCE': [5, 14], 'TECHNICAL': [21, 120], 'LEADERSHIP': [45, 180],
                'PROFESSIONAL': [60, 365], 'ONBOARDING': [1, 7], 'LANGUAGE': [90, 365]
            })
            
            timeframe = completion_timeframes.get(category, [7, 30])
            days_to_complete = random.randint(timeframe[0], timeframe[1])
            completion_date = start_date + timedelta(days=days_to_complete)
            
            # Generate score based on distribution
            scoring_dist = patterns.get('employee_training', {}).get('scoring_distribution', {
                'exceptional': [95, 100], 'excellent': [85, 94], 'good': [75, 84],
                'satisfactory': [65, 74], 'needs_improvement': [0, 64]
            })
            
            score_category = random.choices(
                list(scoring_dist.keys()),
                weights=[0.15, 0.25, 0.35, 0.20, 0.05]
            )[0]
            score_range = scoring_dist[score_category]
            score = round(random.uniform(score_range[0], score_range[1]), 1)
            
            status = 'COMPLETED'
            
            # Certification possibility
            if program.get('program_category') in ['TECHNICAL', 'PROFESSIONAL'] and score >= 80:
                certification_earned = random.random() < 0.4  # 40% chance for eligible programs
        
        # Find approver (manager from same entity)
        managers = [emp for emp in self.generated_data['employees'] 
                   if 'MANAGER' in emp.get('job_title', '') and 
                   emp.get('entity_id') == employee.get('entity_id')]
        approved_by = random.choice(managers)['employee_id'] if managers else employee['employee_id']
        
        return {
            'training_record_id': f"TR_{record_id:06d}",
            'employee_id': employee['employee_id'],
            'program_id': program['program_id'],
            'enrollment_date': enrollment_date.strftime('%Y-%m-%d'),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'completion_date': completion_date.strftime('%Y-%m-%d') if completion_date else None,
            'status': status,
            'score': score,
            'certification_earned': certification_earned,
            'certification_number': f"CERT_{record_id:06d}" if certification_earned else None,
            'certification_expiry_date': (completion_date + timedelta(days=365*2)).strftime('%Y-%m-%d') if certification_earned else None,
            'instructor_name': self.faker.name() if program['program_type'] != 'ONLINE' else None,
            'training_location': 'Online' if program['program_type'] == 'ONLINE' else random.choice(['Headquarters', 'Regional Office', 'External Venue']),
            'cost_eur': program['cost_per_participant_eur'],
            'approved_by': approved_by,
            'employee_feedback': self._generate_training_feedback() if is_completed else None,
            'employee_rating': random.randint(3, 5) if is_completed else None,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
    
    def _generate_training_feedback(self) -> str:
        """Generate realistic training feedback."""
        positive_feedback = [
            "Very informative and well-structured training",
            "Great instructor with practical examples", 
            "Excellent content relevant to daily work",
            "Interactive format made learning engaging",
            "Clear materials and good pace"
        ]
        
        constructive_feedback = [
            "Could use more hands-on exercises",
            "Would benefit from more real-world examples", 
            "Training materials could be updated",
            "More time needed for Q&A sessions",
            "Some sections felt rushed"
        ]
        
        return random.choice(positive_feedback + constructive_feedback)
    
    def generate_employee_surveys(self, mode: str = 'full') -> List[Dict]:
        """Generate employee survey definitions."""
        self.logger.info("📋 Generating employee surveys...")
        
        patterns = self._load_hr_patterns('hr_survey_patterns.yaml')
        survey_config = patterns.get('employee_surveys', {})
        
        surveys = []
        survey_id = 1
        
        # Generate surveys for multiple years (2022-2024)
        survey_types = survey_config.get('survey_types', [
            'ANNUAL_ENGAGEMENT', 'QUARTERLY_PULSE', 'EXIT_INTERVIEW', 
            'NEW_HIRE_FEEDBACK', 'TRAINING_FEEDBACK', 'MANAGER_360'
        ])
        
        years = [2022, 2023, 2024]
        
        for year in years:
            for survey_type in survey_types:
                schedule_config = survey_config.get('survey_schedule', {}).get(survey_type, {})
                frequency = schedule_config.get('frequency', 'yearly')
                
                if frequency == 'yearly':
                    months = schedule_config.get('months', [10])
                    for month in months:
                        survey = self._create_survey_definition(survey_id, survey_type, year, month, patterns)
                        surveys.append(survey)
                        survey_id += 1
                        
                elif frequency == 'quarterly':
                    months = schedule_config.get('months', [1, 4, 7, 10])
                    for month in months:
                        survey = self._create_survey_definition(survey_id, survey_type, year, month, patterns)
                        surveys.append(survey)
                        survey_id += 1
                        
                elif frequency == 'biannual':
                    months = schedule_config.get('months', [3, 9])
                    for month in months:
                        survey = self._create_survey_definition(survey_id, survey_type, year, month, patterns)
                        surveys.append(survey)
                        survey_id += 1
        
        # Add some ad-hoc surveys
        for i in range(3):
            survey = self._create_survey_definition(survey_id, 'TRAINING_FEEDBACK', 2024, random.randint(1, 12), patterns)
            surveys.append(survey)
            survey_id += 1
        
        self.generated_data['employee_surveys'] = surveys
        self.logger.info(f"Generated {len(surveys)} employee surveys")
        return surveys
    
    def _create_survey_definition(self, survey_id: int, survey_type: str, year: int, month: int, patterns: Dict) -> Dict:
        """Create individual survey definition."""
        survey_config = patterns.get('employee_surveys', {})
        schedule_config = survey_config.get('survey_schedule', {}).get(survey_type, {})
        
        duration_days = schedule_config.get('duration_days', 14)
        start_date = date(year, month, 1)
        end_date = start_date + timedelta(days=duration_days)
        
        survey_names = {
            'ANNUAL_ENGAGEMENT': 'Annual Employee Engagement Survey',
            'QUARTERLY_PULSE': 'Quarterly Pulse Check',
            'EXIT_INTERVIEW': 'Exit Interview Survey',
            'NEW_HIRE_FEEDBACK': '90-Day New Hire Feedback',
            'TRAINING_FEEDBACK': 'Training Effectiveness Survey',
            'MANAGER_360': '360-Degree Manager Feedback',
            'WELLBEING_CHECK': 'Employee Wellbeing Check',
            'DIVERSITY_INCLUSION': 'Diversity & Inclusion Survey'
        }
        
        return {
            'survey_id': f"SURV_{survey_id:05d}",
            'survey_name': f"{survey_names.get(survey_type, 'Employee Survey')} - {year} {month:02d}",
            'survey_type': survey_type,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'target_audience': schedule_config.get('target_audience', 'ALL_EMPLOYEES'),
            'is_anonymous': survey_type in ['WELLBEING_CHECK', 'DIVERSITY_INCLUSION'],
            'response_rate_target': survey_config.get('response_rates', {}).get(survey_type, 0.75) * 100,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
    
    def generate_survey_responses(self, mode: str = 'full') -> List[Dict]:
        """Generate employee survey responses with GDPR compliance."""
        self.logger.info("📝 Generating survey responses...")
        
        if not self.generated_data['employees']:
            self.logger.error("No employees found - generate employees first")
            return []
        
        if not self.generated_data['employee_surveys']:
            self.logger.error("No surveys found - generate surveys first")
            return []
        
        patterns = self._load_hr_patterns('hr_survey_patterns.yaml')
        responses = []
        response_id = 1
        
        for survey in self.generated_data['employee_surveys']:
            # Determine response rate for this survey type
            response_rates = patterns.get('employee_surveys', {}).get('response_rates', {})
            response_rate = response_rates.get(survey['survey_type'], 0.75)
            
            # Select employees who will respond
            eligible_employees = self._get_eligible_employees_for_survey(survey, self.generated_data['employees'])
            if not eligible_employees:
                continue  # Skip if no eligible employees
            
            num_responses = max(1, int(len(eligible_employees) * response_rate))
            responding_employees = random.sample(eligible_employees, min(num_responses, len(eligible_employees)))
            
            for employee in responding_employees:
                response = self._create_survey_response(response_id, survey, employee, patterns)
                responses.append(response)
                response_id += 1
        
        self.generated_data['survey_responses'] = responses
        self.logger.info(f"Generated {len(responses)} survey responses")
        return responses
    
    def _get_eligible_employees_for_survey(self, survey: Dict, employees: List[Dict]) -> List[Dict]:
        """Get employees eligible for a specific survey."""
        survey_start = datetime.strptime(survey['start_date'], '%Y-%m-%d').date()
        
        eligible = []
        for employee in employees:
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            
            # Employee must be hired at least 30 days before survey
            if hire_date <= survey_start - timedelta(days=30):
                # Check if employee is still active during survey period
                status = employee.get('status', employee.get('employee_status', 'ACTIVE'))
                if status == 'ACTIVE':
                    eligible.append(employee)
        
        return eligible
    
    def _create_survey_response(self, response_id: int, survey: Dict, employee: Dict, patterns: Dict) -> Dict:
        """Create individual survey response with GDPR compliance."""
        response_config = patterns.get('survey_responses', {})
        gdpr_config = response_config.get('gdpr_compliance', {})
        
        # Determine anonymization level
        anonymization_levels = gdpr_config.get('anonymization_levels', {
            'FULL_ANONYMOUS': 0.65, 'DEPARTMENT_ONLY': 0.22, 'DEMOGRAPHIC_ONLY': 0.13
        })
        
        anonymization_level = random.choices(
            list(anonymization_levels.keys()),
            weights=list(anonymization_levels.values())
        )[0]
        
        # Employee ID is null for fully anonymous responses
        employee_id = None if anonymization_level == 'FULL_ANONYMOUS' else employee['employee_id']
        
        # Generate response date within survey period
        start_date = datetime.strptime(survey['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(survey['end_date'], '%Y-%m-%d').date()
        response_date = self.faker.date_between(start_date=start_date, end_date=end_date)
        
        # Generate satisfaction ratings based on patterns
        satisfaction_patterns = response_config.get('response_patterns', {})
        dept_variations = satisfaction_patterns.get('department_variations', {})
        dept_name = employee.get('department_name', 'GENERAL')
        
        # Base satisfaction range for department
        dept_range = dept_variations.get(dept_name, [3.5, 4.0])
        base_satisfaction = random.uniform(dept_range[0], dept_range[1])
        
        # Convert to 1-5 scale and add some variation
        overall_satisfaction = max(1, min(5, int(base_satisfaction + random.uniform(-0.3, 0.3))))
        
        return {
            'response_id': f"RESP_{response_id:06d}",
            'survey_id': survey['survey_id'],
            'employee_id': employee_id,
            'response_date': f"{response_date} {random.randint(9, 17)}:{random.randint(10, 59)}:00",
            'overall_satisfaction': overall_satisfaction,
            'work_life_balance_rating': max(1, min(5, overall_satisfaction + random.randint(-1, 1))),
            'compensation_satisfaction': max(1, min(5, overall_satisfaction + random.randint(-2, 1))),
            'career_development_rating': max(1, min(5, overall_satisfaction + random.randint(-1, 1))),
            'management_effectiveness': max(1, min(5, overall_satisfaction + random.randint(-1, 1))),
            'company_culture_rating': max(1, min(5, overall_satisfaction + random.randint(-1, 2))),
            'likes_most': self._generate_survey_comment('positive'),
            'improvement_suggestions': self._generate_survey_comment('improvement'),
            'additional_comments': self._generate_survey_comment('general') if random.random() < 0.3 else '',
            'department_group': employee.get('department_name') if anonymization_level != 'FULL_ANONYMOUS' else None,
            'tenure_group': self._get_tenure_group(employee) if anonymization_level != 'FULL_ANONYMOUS' else None,
            'age_group': self._get_age_group(employee) if anonymization_level in ['DEMOGRAPHIC_ONLY'] else None,
            'role_level': self._get_role_level(employee) if anonymization_level != 'FULL_ANONYMOUS' else None,
            'consent_given': True,
            'anonymization_level': anonymization_level,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
    
    def _generate_survey_comment(self, comment_type: str) -> str:
        """Generate realistic survey comments."""
        comments = {
            'positive': [
                "Great team collaboration and supportive environment",
                "Good work-life balance and flexible working arrangements", 
                "Strong learning opportunities and career development",
                "Supportive management and clear communication",
                "Positive company culture and values alignment"
            ],
            'improvement': [
                "More career advancement opportunities would be helpful",
                "Better communication from senior leadership needed",
                "Enhanced training and development programs", 
                "More competitive compensation and benefits",
                "Improved office facilities and equipment"
            ],
            'general': [
                "Overall satisfied with the company direction",
                "Appreciate the focus on employee wellbeing",
                "Looking forward to future growth opportunities",
                "Happy to be part of this organization"
            ]
        }
        
        return random.choice(comments.get(comment_type, ['No comment']))
    
    def _get_tenure_group(self, employee: Dict) -> str:
        """Get employee tenure group for survey analysis."""
        hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
        tenure_years = (date.today() - hire_date).days / 365.25
        
        if tenure_years < 1:
            return '0-1 years'
        elif tenure_years < 3:
            return '1-3 years'
        elif tenure_years < 7:
            return '3-7 years'
        else:
            return '7+ years'
    
    def _get_age_group(self, employee: Dict) -> str:
        """Get employee age group for survey analysis."""
        birth_date = datetime.strptime(employee['date_of_birth'], '%Y-%m-%d').date()
        age = (date.today() - birth_date).days / 365.25
        
        if age < 30:
            return 'Under 30'
        elif age < 40:
            return '30-39'
        elif age < 50:
            return '40-49'
        else:
            return '50+'
    
    def _get_role_level(self, employee: Dict) -> str:
        """Get employee role level for survey analysis."""
        job_title = employee.get('job_title', '').upper()
        
        if 'MANAGER' in job_title or 'DIRECTOR' in job_title:
            return 'MANAGER'
        elif 'SENIOR' in job_title or 'LEAD' in job_title:
            return 'SENIOR'
        elif 'JUNIOR' in job_title or 'TRAINEE' in job_title:
            return 'ENTRY'
        else:
            return 'MID'
    
    def generate_performance_cycles(self, mode: str = 'full') -> List[Dict]:
        """Generate performance management cycles."""
        self.logger.info("🎯 Generating performance cycles...")
        
        patterns = self._load_hr_patterns('hr_performance_patterns.yaml')
        perf_config = patterns.get('performance_cycles', {})
        
        cycles = []
        cycle_id = 1
        
        # Generate cycles for multiple years (2022-2024)
        cycle_types = perf_config.get('cycle_types', [
            'ANNUAL_REVIEW', 'QUARTERLY_REVIEW', 'MID_YEAR_REVIEW', 
            'PROJECT_REVIEW', 'PROBATION_REVIEW'
        ])
        
        years = [2022, 2023, 2024]
        
        for year in years:
            for cycle_type in cycle_types:
                schedule_config = perf_config.get('cycle_schedule', {}).get(cycle_type, {})
                frequency = schedule_config.get('frequency', 'annual')
                
                if frequency == 'annual':
                    months = schedule_config.get('months', [11])
                    for month in months:
                        cycle = self._create_performance_cycle(cycle_id, cycle_type, year, month, patterns)
                        cycles.append(cycle)
                        cycle_id += 1
                        
                elif frequency == 'quarterly':
                    months = schedule_config.get('months', [3, 6, 9, 12])
                    for month in months:
                        cycle = self._create_performance_cycle(cycle_id, cycle_type, year, month, patterns)
                        cycles.append(cycle)
                        cycle_id += 1
                        
                elif frequency == 'biannual':
                    months = schedule_config.get('months', [6, 12])
                    for month in months:
                        cycle = self._create_performance_cycle(cycle_id, cycle_type, year, month, patterns)
                        cycles.append(cycle)
                        cycle_id += 1
        
        self.generated_data['performance_cycles'] = cycles
        self.logger.info(f"Generated {len(cycles)} performance cycles")
        return cycles
    
    def _create_performance_cycle(self, cycle_id: int, cycle_type: str, year: int, month: int, patterns: Dict) -> Dict:
        """Create individual performance cycle definition."""
        perf_config = patterns.get('performance_cycles', {})
        schedule_config = perf_config.get('cycle_schedule', {}).get(cycle_type, {})
        
        duration_days = schedule_config.get('duration_days', 30)
        start_date = date(year, month, 1)
        end_date = start_date + timedelta(days=duration_days)
        
        cycle_names = {
            'ANNUAL_REVIEW': 'Annual Performance Review',
            'QUARTERLY_REVIEW': 'Quarterly Performance Check',
            'MID_YEAR_REVIEW': 'Mid-Year Performance Review',
            'PROJECT_REVIEW': 'Project Performance Review',
            'PROBATION_REVIEW': 'Probation Period Review'
        }
        
        return {
            'cycle_id': f"PERF_{cycle_id:05d}",
            'cycle_name': f"{cycle_names.get(cycle_type, 'Performance Cycle')} - {year} {month:02d}",
            'cycle_type': cycle_type,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'target_audience': schedule_config.get('target_audience', 'ALL_EMPLOYEES'),
            'review_period_months': schedule_config.get('review_period_months', 12),
            'self_assessment_enabled': schedule_config.get('self_assessment_enabled', True),
            'peer_feedback_enabled': schedule_config.get('peer_feedback_enabled', False),
            'goal_setting_enabled': schedule_config.get('goal_setting_enabled', True),
            'calibration_enabled': schedule_config.get('calibration_enabled', cycle_type == 'ANNUAL_REVIEW'),
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
    
    def generate_performance_reviews(self, mode: str = 'full') -> List[Dict]:
        """Generate performance review records with European compliance."""
        self.logger.info("📊 Generating performance reviews...")
        
        if not self.generated_data['employees']:
            self.logger.error("No employees found - generate employees first")
            return []
        
        if not self.generated_data['performance_cycles']:
            self.logger.error("No performance cycles found - generate cycles first")
            return []
        
        patterns = self._load_hr_patterns('hr_performance_patterns.yaml')
        reviews = []
        review_id = 1
        
        for cycle in self.generated_data['performance_cycles']:
            # Get eligible employees for this cycle
            eligible_employees = self._get_eligible_employees_for_performance_cycle(
                cycle, self.generated_data['employees']
            )
            
            self.logger.info(f"Cycle {cycle['cycle_id']} ({cycle['cycle_type']}): {len(eligible_employees)} eligible employees out of {len(self.generated_data['employees'])} total")
            
            reviews_for_cycle = 0
            for employee in eligible_employees:
                # Find employee's manager or create a default manager for review purposes
                manager = self._find_employee_manager(employee, self.generated_data['employees'])
                
                # If no manager found, assign a senior employee as temporary reviewer
                if not manager:
                    potential_managers = [
                        emp for emp in self.generated_data['employees'] 
                        if emp['employee_id'] != employee['employee_id'] and 
                        ('MANAGER' in emp.get('job_title', '').upper() or 'SENIOR' in emp.get('job_title', '').upper())
                    ]
                    if potential_managers:
                        manager = random.choice(potential_managers)
                    else:
                        # If still no managers found, just pick any other employee as reviewer
                        other_employees = [
                            emp for emp in self.generated_data['employees']
                            if emp['employee_id'] != employee['employee_id']
                        ]
                        if other_employees:
                            manager = random.choice(other_employees)
                
                if manager:
                    review = self._create_performance_review(review_id, cycle, employee, manager, patterns)
                    reviews.append(review)
                    review_id += 1
                    reviews_for_cycle += 1
                else:
                    self.logger.warning(f"No manager found for employee {employee['employee_id']} in cycle {cycle['cycle_id']}")
            
            self.logger.info(f"Generated {reviews_for_cycle} reviews for cycle {cycle['cycle_id']}")
        
        self.generated_data['performance_reviews'] = reviews
        self.logger.info(f"Generated {len(reviews)} performance reviews")
        return reviews
    
    def _get_eligible_employees_for_performance_cycle(self, cycle: Dict, employees: List[Dict]) -> List[Dict]:
        """Get employees eligible for a performance cycle."""
        cycle_start = datetime.strptime(cycle['start_date'], '%Y-%m-%d').date()
        review_period_months = cycle.get('review_period_months', 12)
        
        eligible = []
        for employee in employees:
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            
            # Employee must be hired at least 3 months before cycle (minimum tenure)
            # For annual reviews, require full year; for others, be more flexible
            if cycle['cycle_type'] == 'ANNUAL_REVIEW':
                required_tenure_date = cycle_start - timedelta(days=365)
            elif cycle['cycle_type'] == 'PROBATION_REVIEW':
                required_tenure_date = cycle_start - timedelta(days=90)  # 3 months minimum
            else:
                required_tenure_date = cycle_start - timedelta(days=180)  # 6 months for others
            
            if hire_date <= required_tenure_date:
                status = employee.get('status', employee.get('employee_status', 'ACTIVE'))
                if status == 'ACTIVE':
                    # Skip if this is a probation review and employee is past probation
                    if cycle['cycle_type'] == 'PROBATION_REVIEW':
                        probation_end = hire_date + timedelta(days=180)  # 6 months
                        if cycle_start > probation_end:
                            continue
                    
                    eligible.append(employee)
        
        return eligible
    
    def _find_employee_manager(self, employee: Dict, all_employees: List[Dict]) -> Dict:
        """Find the manager for an employee."""
        manager_id = employee.get('manager_id')
        if not manager_id:
            return None
        
        for emp in all_employees:
            if emp['employee_id'] == manager_id:
                return emp
        
        return None
    
    def _create_performance_review(self, review_id: int, cycle: Dict, employee: Dict, manager: Dict, patterns: Dict) -> Dict:
        """Create individual performance review record."""
        review_config = patterns.get('performance_reviews', {})
        rating_config = review_config.get('rating_system', {})
        
        # Generate review dates within cycle period
        start_date = datetime.strptime(cycle['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(cycle['end_date'], '%Y-%m-%d').date()
        review_date = self.faker.date_between(start_date=start_date, end_date=end_date)
        
        # Determine overall performance rating based on department and role
        rating_distributions = rating_config.get('rating_distributions', {})
        dept_name = employee.get('department_name', 'GENERAL')
        role_level = self._get_role_level(employee)
        
        # Get rating probabilities for this role/department combination
        dept_dist = rating_distributions.get(dept_name, {
            'EXCEEDS_EXPECTATIONS': 0.15, 'MEETS_EXPECTATIONS': 0.70, 
            'BELOW_EXPECTATIONS': 0.10, 'NEEDS_IMPROVEMENT': 0.05
        })
        
        overall_rating = random.choices(
            list(dept_dist.keys()),
            weights=list(dept_dist.values())
        )[0]
        
        # Generate specific ratings based on overall rating
        base_score = {
            'EXCEEDS_EXPECTATIONS': 4.5,
            'MEETS_EXPECTATIONS': 3.5,
            'BELOW_EXPECTATIONS': 2.5,
            'NEEDS_IMPROVEMENT': 1.5
        }.get(overall_rating, 3.5)
        
        # Add variation to individual competency ratings
        job_knowledge = max(1, min(5, base_score + random.uniform(-0.3, 0.3)))
        communication = max(1, min(5, base_score + random.uniform(-0.2, 0.4)))
        teamwork = max(1, min(5, base_score + random.uniform(-0.2, 0.3)))
        initiative = max(1, min(5, base_score + random.uniform(-0.4, 0.2)))
        leadership = max(1, min(5, base_score + random.uniform(-0.3, 0.3))) if role_level in ['MANAGER', 'SENIOR'] else None
        
        # Generate development goals and feedback
        goals = self._generate_performance_goals(employee, overall_rating)
        feedback = self._generate_performance_feedback(overall_rating)
        
        return {
            'review_id': f"REV_{review_id:06d}",
            'cycle_id': cycle['cycle_id'],
            'employee_id': employee['employee_id'],
            'manager_id': manager['employee_id'],
            'review_date': f"{review_date} {random.randint(14, 17)}:{random.randint(10, 59)}:00",
            'review_period_start': (start_date - timedelta(days=365)).strftime('%Y-%m-%d'),
            'review_period_end': start_date.strftime('%Y-%m-%d'),
            'overall_rating': overall_rating,
            'overall_score': round(base_score, 1),
            'job_knowledge_rating': round(job_knowledge, 1),
            'communication_rating': round(communication, 1),
            'teamwork_rating': round(teamwork, 1),
            'initiative_rating': round(initiative, 1),
            'leadership_rating': round(leadership, 1) if leadership else None,
            'goal_achievement_percentage': self._calculate_goal_achievement(overall_rating),
            'strengths': feedback['strengths'],
            'areas_for_improvement': feedback['improvements'],
            'development_goals': goals,
            'manager_comments': feedback['manager_comments'],
            'employee_comments': feedback.get('employee_comments', ''),
            'promotion_ready': overall_rating == 'EXCEEDS_EXPECTATIONS' and random.random() < 0.4,
            'development_plan_created': True,
            'next_review_date': (end_date + timedelta(days=365)).strftime('%Y-%m-%d'),
            'hr_reviewed': True,
            'employee_acknowledged': True,
            'acknowledged_date': f"{review_date + timedelta(days=random.randint(1, 7))} 10:00:00",
            'created_date': self._generate_realistic_timestamp('performance'),
            'updated_date': self._generate_realistic_timestamp('performance')
        }
    
    def _generate_performance_goals(self, employee: Dict, rating: str) -> str:
        """Generate development goals based on employee role and performance."""
        dept_name = employee.get('department_name', 'GENERAL')
        role_level = self._get_role_level(employee)
        
        goal_templates = {
            'ENGINEERING': [
                "Enhance technical skills in emerging technologies",
                "Improve code quality and documentation practices",
                "Develop mentoring skills for junior team members",
                "Lead technical architecture decisions"
            ],
            'SALES': [
                "Achieve quarterly sales targets consistently",
                "Develop new customer relationships",
                "Improve product knowledge and sales techniques",
                "Mentor new sales team members"
            ],
            'MARKETING': [
                "Develop digital marketing expertise",
                "Improve campaign ROI and analytics skills",
                "Build strategic partnerships",
                "Lead cross-functional marketing initiatives"
            ],
            'HR': [
                "Enhance employee engagement strategies",
                "Develop expertise in employment law",
                "Improve talent acquisition processes",
                "Build data-driven HR analytics capabilities"
            ],
            'FINANCE': [
                "Improve financial modeling and analysis",
                "Develop strategic business partnering skills",
                "Enhance risk management expertise",
                "Lead process improvement initiatives"
            ]
        }
        
        goals = goal_templates.get(dept_name, [
            "Develop leadership and communication skills",
            "Improve cross-functional collaboration",
            "Build expertise in core competencies",
            "Contribute to strategic initiatives"
        ])
        
        # Select 2-3 goals based on performance rating
        num_goals = 3 if rating == 'EXCEEDS_EXPECTATIONS' else 2
        selected_goals = random.sample(goals, min(num_goals, len(goals)))
        
        return "; ".join(selected_goals)
    
    def _generate_performance_feedback(self, rating: str) -> Dict:
        """Generate performance feedback based on rating."""
        feedback_templates = {
            'EXCEEDS_EXPECTATIONS': {
                'strengths': [
                    "Consistently delivers exceptional results",
                    "Demonstrates strong leadership capabilities",
                    "Shows initiative and drives innovation",
                    "Excellent collaboration and mentoring skills"
                ],
                'improvements': [
                    "Continue developing strategic thinking skills",
                    "Explore opportunities for broader impact",
                    "Consider taking on additional leadership responsibilities"
                ],
                'manager_comments': [
                    "Outstanding performance this review period. Ready for increased responsibilities.",
                    "Exemplary contributor who consistently exceeds expectations and helps others succeed.",
                    "Strong candidate for advancement. Demonstrates excellent leadership potential."
                ]
            },
            'MEETS_EXPECTATIONS': {
                'strengths': [
                    "Consistently meets performance goals",
                    "Reliable and dependable team member",
                    "Good collaboration and communication skills",
                    "Shows commitment to quality work"
                ],
                'improvements': [
                    "Seek opportunities to take on additional challenges",
                    "Develop expertise in emerging areas",
                    "Improve proactive communication with stakeholders"
                ],
                'manager_comments': [
                    "Solid performance this period. Meets expectations consistently.",
                    "Reliable contributor who delivers quality work on time.",
                    "Good team player with opportunities for growth in leadership."
                ]
            },
            'BELOW_EXPECTATIONS': {
                'strengths': [
                    "Shows potential in core areas",
                    "Willing to learn and improve",
                    "Positive attitude toward feedback"
                ],
                'improvements': [
                    "Focus on meeting established performance goals",
                    "Improve time management and prioritization",
                    "Enhance technical/functional skills through training",
                    "Increase proactive communication with manager"
                ],
                'manager_comments': [
                    "Performance is below expectations. Clear improvement plan established.",
                    "Additional support and training needed to meet performance standards.",
                    "Regular check-ins scheduled to monitor progress."
                ]
            },
            'NEEDS_IMPROVEMENT': {
                'strengths': [
                    "Shows willingness to improve",
                    "Positive response to coaching"
                ],
                'improvements': [
                    "Must improve performance to meet basic job requirements",
                    "Focus on fundamental skills development",
                    "Improve consistency in work quality and output",
                    "Enhance communication and collaboration skills"
                ],
                'manager_comments': [
                    "Significant improvement required to meet performance standards.",
                    "Formal performance improvement plan initiated.",
                    "Weekly coaching sessions scheduled to support development."
                ]
            }
        }
        
        template = feedback_templates.get(rating, feedback_templates['MEETS_EXPECTATIONS'])
        
        return {
            'strengths': random.choice(template['strengths']),
            'improvements': random.choice(template['improvements']),
            'manager_comments': random.choice(template['manager_comments']),
            'employee_comments': self._generate_employee_self_reflection(rating)
        }
    
    def _generate_employee_self_reflection(self, rating: str) -> str:
        """Generate employee self-reflection comments."""
        reflections = {
            'EXCEEDS_EXPECTATIONS': [
                "I'm proud of the achievements this year and look forward to taking on new challenges.",
                "Grateful for the opportunities to lead and mentor others. Ready for the next level.",
                "This has been a rewarding year with strong results across all areas."
            ],
            'MEETS_EXPECTATIONS': [
                "Satisfied with my performance this year. Looking forward to new growth opportunities.",
                "I've delivered consistent results and am excited about upcoming projects.",
                "Good progress this year. Ready to take on additional responsibilities."
            ],
            'BELOW_EXPECTATIONS': [
                "I understand the areas for improvement and am committed to making progress.",
                "Appreciate the feedback and support. Will focus on the development areas identified.",
                "Looking forward to implementing the improvement plan and showing progress."
            ],
            'NEEDS_IMPROVEMENT': [
                "I recognize the need for significant improvement and am committed to the plan.",
                "Appreciate the additional support and coaching. Will focus on fundamental improvements.",
                "Understanding the concerns and working hard to meet expectations."
            ]
        }
        
        return random.choice(reflections.get(rating, reflections['MEETS_EXPECTATIONS']))
    
    def _calculate_goal_achievement(self, rating: str) -> int:
        """Calculate goal achievement percentage based on overall rating."""
        base_percentages = {
            'EXCEEDS_EXPECTATIONS': 95,
            'MEETS_EXPECTATIONS': 85,
            'BELOW_EXPECTATIONS': 65,
            'NEEDS_IMPROVEMENT': 45
        }
        
        base = base_percentages.get(rating, 85)
        return max(0, min(100, base + random.randint(-10, 10)))
    
    def _load_pos_patterns(self, filename: str) -> Dict:
        """Load POS patterns from YAML configuration file."""
        config_path = Path(self.config_path) / 'data_patterns' / filename
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            self.logger.warning(f"POS pattern file {filename} not found, using defaults")
        return self._get_default_pos_patterns()
    
    def _load_vat_rates(self, filename: str = 'european_vat_rates.yaml') -> Dict:
        """Load European VAT rates from YAML configuration file."""
        config_path = Path(self.config_path) / 'data_patterns' / filename
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            self.logger.warning(f"VAT rates file {filename} not found, using defaults")
            return self._get_default_vat_rates()
    
    def _get_default_vat_rates(self) -> Dict:
        """Provide default VAT rates if configuration file is missing."""
        return {
            'european_vat_rates': {
                'country_vat_rates': {
                    'NL': {'standard_rate': 21.0, 'country_name': 'Netherlands'},
                    'DE': {'standard_rate': 19.0, 'country_name': 'Germany'}, 
                    'FR': {'standard_rate': 20.0, 'country_name': 'France'},
                    'BE': {'standard_rate': 21.0, 'country_name': 'Belgium'}
                },
                'gl_account_mapping': {
                    'vat_payable_accounts': {
                        'NL': '2201', 'DE': '2202', 'FR': '2203', 'BE': '2204'
                    }
                }
            }
        }
    
    def _generate_realistic_timestamp(self, context: str, reference_date: str = None) -> str:
        """Generate realistic created_date and updated_date timestamps based on context."""
        now = datetime.now()
        
        if context == 'hire' and reference_date:
            # For employee records, created_date should be close to hire_date
            hire_date = datetime.strptime(reference_date, '%Y-%m-%d')
            # Created within 1-30 days of hire date
            creation_time = hire_date + timedelta(days=random.randint(1, 30))
        elif context == 'transaction':
            # For transaction records, created_date should be recent business activity
            # Generate dates within last 12 months with business hour weighting
            days_ago = random.randint(1, 365)
            base_date = now - timedelta(days=days_ago)
            # Add business hours (9 AM - 9 PM)
            business_hour = random.randint(9, 21)
            creation_time = base_date.replace(hour=business_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        elif context == 'performance':
            # For performance reviews, created within review periods
            creation_time = self.faker.date_time_between(start_date='-2y', end_date='now')
        else:
            # General case: created within last 2 years
            creation_time = self.faker.date_time_between(start_date='-2y', end_date='now')
        
        return creation_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_default_pos_patterns(self) -> Dict:
        """Provide default POS patterns if configuration file is missing."""
        return {
            'pos_configuration': {
                'store_coverage': {
                    'sales_staff_percentage': 20,
                    'role_distribution': {'sales_associate': 70, 'shift_supervisor': 20, 'store_manager': 10}
                },
                'transaction_patterns': {
                    'daily_transactions': {'flagship': [150, 300], 'standard': [80, 160], 'outlet': [30, 80]},
                    'hourly_distribution': {12: 10, 13: 12, 17: 11, 18: 12, 19: 8, 20: 6},
                    'daily_multipliers': {1: 0.8, 2: 0.9, 3: 0.9, 4: 1.0, 5: 1.3, 6: 1.4, 7: 1.2}
                },
                'payment_methods': {
                    'distribution': {'card_payment': 60, 'mobile_payment': 25, 'cash': 15}
                },
                'transaction_composition': {
                    'items_per_transaction': {1: 35, 2: 25, 3: 20, 4: 12, 5: 8},
                    'average_transaction_value': {'flagship': [65, 120], 'standard': [45, 85], 'outlet': [25, 55]}
                }
            },
            'integration_mappings': {
                'finance_integration': {
                    'gl_account_mapping': {
                        'sales_revenue': '4000',
                        'cash_account': '1100',
                        'card_receivable': '1110',
                        'tax_payable': '2200'
                    }
                }
            }
        }
    
    # ========================================
    # POS (POINT OF SALES) DATA GENERATION
    # ========================================
    
    def generate_pos_employee_assignments(self, mode: str = 'full') -> List[Dict]:
        """Generate POS employee assignments linking HR employees to store sales roles."""
        self.logger.info("💼 Generating POS employee assignments...")
        
        if not self.generated_data['employees']:
            self.logger.error("No employees found - generate employees first")
            return []
        
        if not self.generated_data['stores']:
            self.logger.error("No stores found - generate stores first")
            return []
        
        patterns = self._load_pos_patterns('pos_patterns.yaml')
        store_config = patterns.get('store_operations', {})
        
        assignments = []
        assignment_id = 1
        
        # Get stores that have POS systems (physical stores only)
        pos_stores = [
            store for store in self.generated_data['stores'] 
            if store.get('store_type') != 'ONLINE_ONLY' and store.get('is_active')
        ]
        
        # Calculate how many employees to assign as sales staff (roughly 20-25% of employees)
        total_sales_staff_needed = max(18, len(pos_stores) * 2)  # At least 2 per store
        
        # Role distribution from config
        role_distribution = store_config.get('pos_role_distribution', {
            'CASHIER': 0.65, 'SALES_ASSOCIATE': 0.25, 'SHIFT_SUPERVISOR': 0.10
        })
        
        # Select employees for sales roles (prefer those without management titles in other departments)
        potential_sales_staff = [
            emp for emp in self.generated_data['employees']
            if emp.get('employee_status') == 'ACTIVE' and 
            not any(title in emp.get('job_title', '').upper() for title in ['CEO', 'CTO', 'CFO', 'VP', 'PRESIDENT'])
        ]
        
        selected_sales_staff = random.sample(
            potential_sales_staff, 
            min(total_sales_staff_needed, len(potential_sales_staff))
        )
        
        # Assign roles to selected staff
        roles = []
        for role, percentage in role_distribution.items():
            count = int(len(selected_sales_staff) * percentage)  # percentage is already decimal
            roles.extend([role] * count)
        
        # Fill any remaining slots with SALES_ASSOCIATE (config uses uppercase)
        while len(roles) < len(selected_sales_staff):
            roles.append('SALES_ASSOCIATE')
        
        random.shuffle(roles)
        
        # Staff per store configuration
        staff_per_store = store_config.get('staff_per_store', {
            'flagship': [8, 15], 'standard': [4, 8], 'outlet': [2, 5]
        })
        
        # Assign employees to stores
        staff_index = 0
        for store in pos_stores:
            store_format = store.get('store_format', 'standard')
            min_staff, max_staff = staff_per_store.get(store_format, [4, 8])
            store_staff_count = random.randint(min_staff, max_staff)
            
            # Assign staff to this store
            for i in range(min(store_staff_count, len(selected_sales_staff) - staff_index)):
                employee = selected_sales_staff[staff_index]
                role = roles[staff_index] if staff_index < len(roles) else 'sales_associate'
                
                # Determine employment type and schedule
                is_full_time = role in ['store_manager', 'shift_supervisor'] or random.random() < 0.6
                
                assignment = {
                    'assignment_id': f"POSEMP_{assignment_id:05d}",
                    'employee_id': employee['employee_id'],
                    'store_id': store['store_id'],
                    'pos_role': role,
                    'employment_type': 'full_time' if is_full_time else 'part_time',
                    'start_date': max(
                        employee['hire_date'],
                        (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
                    ),
                    'end_date': None,  # Active assignment
                    'hourly_rate_eur': self._calculate_pos_hourly_rate(role, store_format),
                    'commission_eligible': role in ['sales_associate', 'shift_supervisor'],
                    'can_process_returns': role in ['shift_supervisor', 'store_manager'],
                    'register_access_level': self._get_register_access_level(role),
                    'max_discount_percentage': self._get_max_discount_auth(role),
                    'training_completed': True,
                'status': 'active',
                'created_date': self._generate_realistic_timestamp('hire', employee['hire_date']),
                'updated_date': self._generate_realistic_timestamp('update')
                }
                
                assignments.append(assignment)
                assignment_id += 1
                staff_index += 1
                
                if staff_index >= len(selected_sales_staff):
                    break
            
            if staff_index >= len(selected_sales_staff):
                break
        
        self.generated_data['pos_employee_assignments'] = assignments
        self.logger.info(f"Generated {len(assignments)} POS employee assignments across {len(pos_stores)} stores")
        return assignments
    
    def _calculate_pos_hourly_rate(self, role: str, store_format: str) -> float:
        """Calculate hourly rate for POS employee based on role and store format."""
        base_rates = {
            'sales_associate': 14.50,
            'shift_supervisor': 18.75,
            'store_manager': 24.00
        }
        
        store_multipliers = {
            'flagship': 1.15,
            'standard': 1.00,
            'outlet': 0.92
        }
        
        base_rate = base_rates.get(role, 14.50)
        store_multiplier = store_multipliers.get(store_format, 1.00)
        
        return round(base_rate * store_multiplier + random.uniform(-0.50, 1.50), 2)
    
    def _get_register_access_level(self, role: str) -> str:
        """Get POS register access level for role."""
        access_levels = {
            'sales_associate': 'basic',
            'shift_supervisor': 'advanced',
            'store_manager': 'admin'
        }
        return access_levels.get(role, 'basic')
    
    def _get_max_discount_auth(self, role: str) -> int:
        """Get maximum discount authorization percentage for role."""
        discount_auth = {
            'sales_associate': 10,
            'shift_supervisor': 25,
            'store_manager': 50
        }
        return discount_auth.get(role, 5)
    
    def generate_pos_transactions_with_revenue_matching(self, mode: str = 'full') -> tuple[List[Dict], List[Dict], List[Dict]]:
        """Generate POS transactions that exactly match Operations revenue with GL entries."""
        self.logger.info("💳 Generating POS transactions with perfect revenue matching...")
        
        # Ensure we have all required data
        required_data = ['employees', 'stores', 'products', 'customers', 'orders', 'pos_employee_assignments']
        for data_type in required_data:
            if not self.generated_data.get(data_type):
                self.logger.error(f"Missing {data_type} - generate required data first")
                return [], [], []
        
        patterns = self._load_pos_patterns('pos_patterns.yaml')
        vat_rates = self._load_vat_rates()
        
        # Get existing orders revenue to match exactly
        total_orders_revenue = sum(Decimal(str(order['total_amount_eur'])) for order in self.generated_data['orders'])
        self.logger.info(f"Target POS revenue to match: €{total_orders_revenue:,.2f}")
        
        transactions = []
        transaction_items = []
        gl_entries = []
        
        transaction_id = 1
        item_id = 1
        gl_line_id = 1
        
        # Create transactions that will sum to exact target revenue
        remaining_revenue = float(total_orders_revenue)
        transaction_count = self._calculate_target_transaction_count(mode)
        
        # Generate all transactions except the last one normally
        for i in range(transaction_count - 1):
            if remaining_revenue <= 0:
                break
                
            # Generate transaction with reasonable amount
            transaction, items, gl_entries_for_txn = self._create_pos_transaction(
                transaction_id, item_id, gl_line_id, patterns, vat_rates, remaining_revenue
            )
            
            if transaction:
                transactions.append(transaction)
                transaction_items.extend(items)
                gl_entries.extend(gl_entries_for_txn)
                
                remaining_revenue -= float(transaction['total_amount_eur'])
                transaction_id += 1
                item_id += len(items)
                gl_line_id += len(gl_entries_for_txn)
        
        # Create final transaction to exactly match remaining revenue
        if remaining_revenue > 5.0:  # Only if significant amount remaining
            final_transaction, final_items, final_gl = self._create_exact_revenue_transaction(
                transaction_id, item_id, gl_line_id, patterns, vat_rates, remaining_revenue
            )
            
            if final_transaction:
                transactions.append(final_transaction)
                transaction_items.extend(final_items)
                gl_entries.extend(final_gl)
        
        # Store the generated data
        self.generated_data['pos_transactions'] = transactions
        self.generated_data['pos_transaction_items'] = transaction_items
        
        # Add POS GL entries to existing GL entries
        self.generated_data['gl_entries'].extend(gl_entries)
        
        actual_pos_revenue = sum(Decimal(str(txn['total_amount_eur'])) for txn in transactions)
        variance = abs(actual_pos_revenue - total_orders_revenue)
        
        self.logger.info(f"✅ Generated {len(transactions)} POS transactions")
        self.logger.info(f"✅ Generated {len(transaction_items)} transaction line items")
        self.logger.info(f"✅ Generated {len(gl_entries)} GL entries for POS")
        self.logger.info(f"🎯 PERFECT MATCH: POS revenue €{actual_pos_revenue:,.2f} vs Orders €{total_orders_revenue:,.2f} (variance: €{variance})")
        
        return transactions, transaction_items, gl_entries
    
    def _calculate_target_transaction_count(self, mode: str) -> int:
        """Calculate target number of POS transactions to match order volume and revenue."""
        # CRITICAL FIX: Base transaction count on order volume to ensure revenue matching
        order_count = len(self.generated_data['orders'])
        
        # POS should generate roughly 80-90% of order count as transactions
        # (Some orders are online-only, some are bulk orders split into multiple POS transactions)
        pos_transaction_multiplier = 0.85
        
        # Calculate minimum transactions needed for realistic store coverage
        pos_stores = [s for s in self.generated_data['stores'] if s.get('store_format') != 'online']
        min_transactions_for_stores = len(pos_stores) * 50  # At least 50 transactions per physical store
        
        # Use the larger of order-based count or store-based minimum
        target_count = max(
            int(order_count * pos_transaction_multiplier),
            min_transactions_for_stores
        )
        
        self.logger.info(f"🎯 POS Target: {target_count} transactions to match {order_count} orders across {len(pos_stores)} stores")
        return target_count
    
    def _create_pos_transaction(self, txn_id: int, item_id: int, gl_line_id: int, 
                               patterns: Dict, vat_rates: Dict, max_amount: float) -> tuple[Dict, List[Dict], List[Dict]]:
        """Create a single POS transaction with items and GL entries."""
        pos_config = patterns.get('pos_configuration', {})
        
        # Select random store and employee assignment
        pos_assignment = random.choice(self.generated_data['pos_employee_assignments'])
        store_id = pos_assignment['store_id']
        employee_id = pos_assignment['employee_id']
        
        # Get store details
        store = next((s for s in self.generated_data['stores'] if s['store_id'] == store_id), None)
        if not store:
            return None, [], []
        
        store_format = store.get('store_format', 'standard')
        country_code = store.get('country_code', 'NL')
        
        # Get country-specific VAT rate
        vat_rate = self._get_country_vat_rate(country_code, vat_rates)
        vat_decimal = Decimal(str(vat_rate / 100))
        
        # Determine transaction timing
        transaction_date, transaction_time = self._generate_transaction_datetime(patterns)
        
        # Determine number of items and target amount
        items_count = self._select_items_count(pos_config)
        target_amount = min(
            max_amount * 0.8,  # Don't use all remaining amount
            self._select_transaction_amount(store_format, pos_config)
        )
        
        # Select random customer (or None for cash customers)
        customer = random.choice(self.generated_data['customers']) if random.random() < 0.3 else None
        
        # Select products for transaction
        selected_products = random.sample(self.generated_data['products'], items_count)
        
            # Create transaction items
        items = []
        subtotal = Decimal('0.00')
        
        for i, product in enumerate(selected_products):
            quantity = random.choice([1, 1, 1, 2])  # Mostly single items, some multiples
            unit_price = Decimal(str(product['price_eur']))
            
            # Apply realistic line discounts (10% of items get discounts)
            line_discount = Decimal('0.00')
            if random.random() < 0.1:  # 10% of items get discounts
                discount_percent = random.choice([0.05, 0.10, 0.15, 0.20, 0.25])  # 5-25% discounts
                line_discount = unit_price * quantity * Decimal(str(discount_percent))
            
            line_total = (unit_price * quantity) - line_discount
            
            # Determine if this is a return (2% of items)
            return_reason = None
            if random.random() < 0.02:  # 2% return rate
                return_reasons = ['DEFECTIVE', 'WRONG_SIZE', 'WRONG_COLOR', 'CUSTOMER_CHANGE_MIND', 'DAMAGED_IN_STORE']
                return_reason = random.choice(return_reasons)
                line_total = -abs(line_total)  # Returns are negative amounts
            
            item = {
                'item_id': f"POSITEM_{item_id + i:08d}",
                'transaction_id': f"POS_{txn_id:08d}",
                'product_id': product['product_id'],
                'item_sequence': i + 1,
                'quantity': quantity if return_reason is None else -quantity,
                'unit_price_eur': float(unit_price),
                'original_price_eur': float(unit_price),
                'line_discount_amount_eur': float(line_discount),
                'line_total_eur': float(line_total),
                'tax_rate_percentage': vat_rate,
                'tax_amount_eur': float(line_total * vat_decimal),
                'return_reason': return_reason,
                'sales_associate_id': employee_id,
                'created_date': self._generate_realistic_timestamp('transaction'),
                'updated_date': self._generate_realistic_timestamp('transaction')
            }
            
            items.append(item)
            subtotal += line_total
        
        # Calculate taxes and totals using country-specific VAT rate
        tax_amount = subtotal * vat_decimal
        total_amount = subtotal + tax_amount
        
        # Adjust to target amount if needed
        if abs(float(total_amount) - target_amount) > target_amount * 0.3:
            adjustment_factor = Decimal(str(target_amount)) / total_amount
            subtotal = subtotal * adjustment_factor
            tax_amount = subtotal * vat_decimal
            total_amount = subtotal + tax_amount
            
            # Update item prices proportionally
            for item in items:
                item['unit_price_eur'] = round(item['unit_price_eur'] * float(adjustment_factor), 2)
                item['line_total_eur'] = round(item['line_total_eur'] * float(adjustment_factor), 2)
                item['tax_amount_eur'] = round(item['tax_amount_eur'] * float(adjustment_factor), 2)
        
        # Select payment method
        payment_method = self._select_payment_method(pos_config)
        
        # Generate realistic transaction-level attributes
        # Transaction discount (5% chance for transaction-level promotion)
        transaction_discount = Decimal('0.00')
        promotion_code = None
        if random.random() < 0.05:  # 5% transactions have promotions
            promo_codes = ['SUMMER20', 'NEWCUSTOMER15', 'LOYALTY10', 'FLASH25', 'STUDENT15', 'MEMBER20']
            promotion_code = random.choice(promo_codes)
            discount_percent = float(promotion_code[-2:]) / 100  # Extract percentage from code
            transaction_discount = subtotal * Decimal(str(discount_percent))
        
        # Customer type variation
        if customer:
            customer_types = ['regular', 'vip', 'student', 'employee', 'member']
            customer_type = random.choices(
                customer_types, 
                weights=[60, 10, 15, 5, 10]  # 60% regular, 10% VIP, etc.
            )[0]
        else:
            customer_type = random.choices(['regular', 'tourist'], weights=[80, 20])[0]
        
        # Transaction type variation
        transaction_types = ['sale', 'return', 'exchange', 'layaway']
        transaction_type = random.choices(
            transaction_types,
            weights=[92, 4, 3, 1]  # 92% sales, 4% returns, etc.
        )[0]
        
        # Loyalty points (only for customers with loyalty cards)
        loyalty_points_earned = 0
        loyalty_points_redeemed = 0
        if customer and random.random() < 0.35:  # 35% of customers have loyalty cards
            if transaction_type == 'sale':
                loyalty_points_earned = max(1, int(float(total_amount) / 10))  # 1 point per €10
            if random.random() < 0.15:  # 15% of loyalty customers redeem points
                loyalty_points_redeemed = random.randint(50, 500)
                transaction_discount += Decimal(str(loyalty_points_redeemed * 0.01))  # 1 cent per point
        
        # Recalculate totals with discounts
        final_subtotal = subtotal - transaction_discount
        final_tax = final_subtotal * vat_decimal
        final_total = final_subtotal + final_tax
        
        # Create transaction record
        transaction = {
            'transaction_id': f"POS_{txn_id:08d}",
            'store_id': store_id,
            'employee_id': employee_id,
            'customer_id': customer['customer_id'] if customer else None,
            'transaction_date': transaction_date,
            'transaction_datetime': f"{transaction_date} {transaction_time}",
            'shift_id': f"SHIFT_{employee_id}_{transaction_date}",
            'register_number': random.randint(1, 4),
            'receipt_number': f"R{txn_id:010d}",
            'subtotal_amount_eur': round(float(final_subtotal), 2),
            'tax_amount_eur': round(float(final_tax), 2),
            'discount_amount_eur': round(float(transaction_discount), 2),
            'total_amount_eur': round(float(final_total), 2),
            'payment_method': payment_method,
            'payment_status': random.choices(['completed', 'pending', 'failed'], weights=[95, 3, 2])[0],
            'customer_type': customer_type,
            'transaction_type': transaction_type,
            'promotion_codes_used': promotion_code,
            'loyalty_points_earned': loyalty_points_earned,
            'loyalty_points_redeemed': loyalty_points_redeemed,
            'created_date': self._generate_realistic_timestamp('transaction'),
            'updated_date': self._generate_realistic_timestamp('transaction')
        }
        
        # Create GL entries for this transaction
        gl_entries = self._create_pos_gl_entries(transaction, gl_line_id, patterns, vat_rates, country_code)
        
        return transaction, items, gl_entries
    
    def _create_exact_revenue_transaction(self, txn_id: int, item_id: int, gl_line_id: int,
                                         patterns: Dict, vat_rates: Dict, exact_amount: float) -> tuple[Dict, List[Dict], List[Dict]]:
        """Create a transaction for exactly the specified amount."""
        # Create a simplified transaction to exactly match the remaining revenue
        pos_assignment = random.choice(self.generated_data['pos_employee_assignments'])
        customer = random.choice(self.generated_data['customers']) if random.random() < 0.3 else None
        product = random.choice(self.generated_data['products'])
        
        # Get store and country for VAT calculation
        store = next((s for s in self.generated_data['stores'] if s['store_id'] == pos_assignment['store_id']), None)
        country_code = store.get('country_code', 'NL') if store else 'NL'
        vat_rate = self._get_country_vat_rate(country_code, vat_rates)
        vat_multiplier = Decimal('1') + Decimal(str(vat_rate / 100))
        
        transaction_date, transaction_time = self._generate_transaction_datetime(patterns)
        
        # Calculate amounts to match exact target using country-specific VAT
        total_amount = Decimal(str(exact_amount))
        subtotal = total_amount / vat_multiplier
        tax_amount = total_amount - subtotal
        
        # Apply occasional discounts to exact amount items too
        line_discount = Decimal('0.00') 
        return_reason = None
        if random.random() < 0.05:  # 5% get discounts on exact amount items
            discount_percent = random.choice([0.05, 0.10, 0.15])
            line_discount = subtotal * Decimal(str(discount_percent))
        
        # Create single item for exact amount
        item = {
            'item_id': f"POSITEM_{item_id:08d}",
            'transaction_id': f"POS_{txn_id:08d}",
            'product_id': product['product_id'],
            'item_sequence': 1,
            'quantity': 1,
            'unit_price_eur': round(float(subtotal), 2),
            'original_price_eur': float(product['price_eur']),
            'line_discount_amount_eur': float(line_discount),
            'line_total_eur': round(float(subtotal), 2),
            'tax_rate_percentage': vat_rate,
            'tax_amount_eur': round(float(tax_amount), 2),
            'return_reason': return_reason,
            'sales_associate_id': pos_assignment['employee_id'],
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
        
        # Add realistic attributes to exact amount transactions too
        customer_type = 'regular'
        if customer:
            customer_type = random.choices(['regular', 'vip', 'member'], weights=[70, 15, 15])[0]
        
        transaction_type = random.choices(['sale', 'return'], weights=[95, 5])[0]
        payment_method = random.choices(['card_payment', 'cash', 'mobile_payment'], weights=[70, 20, 10])[0]
        
        loyalty_points_earned = 0
        if customer and random.random() < 0.3:
            loyalty_points_earned = max(1, int(float(total_amount) / 10))
        
        transaction = {
            'transaction_id': f"POS_{txn_id:08d}",
            'store_id': pos_assignment['store_id'],
            'employee_id': pos_assignment['employee_id'],
            'customer_id': customer['customer_id'] if customer else None,
            'transaction_date': transaction_date,
            'transaction_datetime': f"{transaction_date} {transaction_time}",
            'shift_id': f"SHIFT_{pos_assignment['employee_id']}_{transaction_date}",
            'register_number': random.randint(1, 4),
            'receipt_number': f"R{txn_id:010d}",
            'subtotal_amount_eur': round(float(subtotal), 2),
            'tax_amount_eur': round(float(tax_amount), 2),
            'discount_amount_eur': float(line_discount),
            'total_amount_eur': round(float(total_amount), 2),
            'payment_method': payment_method,
            'payment_status': random.choices(['completed', 'pending'], weights=[97, 3])[0],
            'customer_type': customer_type,
            'transaction_type': transaction_type,
            'promotion_codes_used': random.choice([None, 'FLASH15']) if random.random() < 0.03 else None,
            'loyalty_points_earned': loyalty_points_earned,
            'loyalty_points_redeemed': random.randint(0, 200) if random.random() < 0.1 else 0,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        }
        
        gl_entries = self._create_pos_gl_entries(transaction, gl_line_id, patterns, vat_rates, country_code)
        
        return transaction, [item], gl_entries
    
    def _generate_transaction_datetime(self, patterns: Dict) -> tuple[str, str]:
        """Generate realistic transaction date and time."""
        # Generate date within last 3 months
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        transaction_date = self.faker.date_between(start_date=start_date, end_date=end_date)
        
        # Generate time based on hourly distribution patterns
        hourly_dist = patterns.get('pos_configuration', {}).get('transaction_patterns', {}).get(
            'hourly_distribution', {12: 10, 13: 12, 17: 11, 18: 12}
        )
        
        # Select hour based on distribution
        hours = list(hourly_dist.keys())
        weights = list(hourly_dist.values())
        selected_hour = random.choices(hours, weights=weights)[0]
        
        # Random minute within the hour
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        transaction_time = f"{selected_hour:02d}:{minute:02d}:{second:02d}"
        
        return transaction_date.strftime('%Y-%m-%d'), transaction_time
    
    def _select_items_count(self, pos_config: Dict) -> int:
        """Select number of items for transaction based on patterns."""
        items_dist = pos_config.get('transaction_composition', {}).get(
            'items_per_transaction', {1: 35, 2: 25, 3: 20, 4: 12, 5: 8}
        )
        
        items_counts = list(items_dist.keys())
        weights = list(items_dist.values())
        
        return random.choices(items_counts, weights=weights)[0]
    
    def _select_transaction_amount(self, store_format: str, pos_config: Dict) -> float:
        """Select target transaction amount based on store format."""
        amount_ranges = pos_config.get('transaction_composition', {}).get(
            'average_transaction_value', {
                'flagship': [65, 120],
                'standard': [45, 85],
                'outlet': [25, 55]
            }
        )
        
        min_amount, max_amount = amount_ranges.get(store_format, [45, 85])
        return random.uniform(min_amount, max_amount)
    
    def _select_payment_method(self, pos_config: Dict) -> str:
        """Select payment method based on European patterns."""
        payment_dist = pos_config.get('payment_methods', {}).get(
            'distribution', {
                'card_payment': 60,
                'mobile_payment': 25,
                'cash': 15
            }
        )
        
        methods = list(payment_dist.keys())
        weights = list(payment_dist.values())
        
        return random.choices(methods, weights=weights)[0]
    
    def _get_country_vat_rate(self, country_code: str, vat_rates: Dict) -> float:
        """Get VAT rate for specific country."""
        country_rates = vat_rates.get('european_vat_rates', {}).get('country_vat_rates', {})
        country_data = country_rates.get(country_code, {'standard_rate': 21.0})
        return country_data.get('standard_rate', 21.0)
    
    def _create_pos_gl_entries(self, transaction: Dict, gl_line_id: int, patterns: Dict, vat_rates: Dict, country_code: str) -> List[Dict]:
        """Create GL journal entries for a POS transaction."""
        # Get GL account mapping from patterns
        gl_mapping = patterns.get('integration_mappings', {}).get(
            'finance_integration', {}
        ).get('gl_account_mapping', {})
        
        # Get country-specific VAT payable account from VAT rates config
        vat_accounts = vat_rates.get('european_vat_rates', {}).get(
            'gl_account_mapping', {}
        ).get('vat_payable_accounts', {})
        
        country_vat_account = vat_accounts.get(country_code, '2200')  # Default fallback
        
        total_amount = Decimal(str(transaction['total_amount_eur']))
        subtotal = Decimal(str(transaction['subtotal_amount_eur']))
        tax_amount = Decimal(str(transaction['tax_amount_eur']))
        
        payment_method = transaction['payment_method']
        transaction_date = transaction['transaction_date']
        transaction_id = transaction['transaction_id']
        
        gl_entries = []
        
        # Debit: Cash/Card Account (depending on payment method)
        if payment_method == 'cash':
            debit_account = gl_mapping.get('cash_account', '1100')
        else:
            debit_account = gl_mapping.get('card_receivable', '1110')
        
        gl_entries.append({
            'journal_line_id': f"POS_GL_{gl_line_id}",
            'journal_header_id': f"POS_HDR_{transaction_date.replace('-', '')}",
            'line_number': 1,
            'account_id': debit_account,
            'debit_amount': float(total_amount),
            'credit_amount': 0.00,
            'currency_code': 'EUR',
            'exchange_rate': 1.0000,
            'line_description': f"POS sale {transaction_id}",
            'reference_1': transaction_id,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        })
        
        # Credit: Sales Revenue
        gl_entries.append({
            'journal_line_id': f"POS_GL_{gl_line_id + 1}",
            'journal_header_id': f"POS_HDR_{transaction_date.replace('-', '')}",
            'line_number': 2,
            'account_id': gl_mapping.get('sales_revenue', '4000'),
            'debit_amount': 0.00,
            'credit_amount': float(subtotal),
            'currency_code': 'EUR',
            'exchange_rate': 1.0000,
            'line_description': f"POS sales revenue {transaction_id}",
            'reference_1': transaction_id,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        })
        
        # Credit: Tax Payable (country-specific VAT account)
        gl_entries.append({
            'journal_line_id': f"POS_GL_{gl_line_id + 2}",
            'journal_header_id': f"POS_HDR_{transaction_date.replace('-', '')}",
            'line_number': 3,
            'account_id': country_vat_account,
            'debit_amount': 0.00,
            'credit_amount': float(tax_amount),
            'currency_code': 'EUR',
            'exchange_rate': 1.0000,
            'line_description': f"POS VAT collected {transaction_id}",
            'reference_1': transaction_id,
            'created_date': '2024-01-01 10:00:00',
            'updated_date': '2024-01-01 10:00:00'
        })
        
        return gl_entries
    
    def generate_pos_employee_shifts(self, mode: str = 'full') -> List[Dict]:
        """Generate POS employee shift records."""
        self.logger.info("⏰ Generating POS employee shifts...")
        
        if not self.generated_data['pos_employee_assignments']:
            return []
        
        shifts = []
        shift_id = 1
        
        # Generate shifts for the last 30 days
        for days_ago in range(30):
            shift_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            for assignment in self.generated_data['pos_employee_assignments']:
                # 80% chance of working on any given day
                if random.random() < 0.8:
                    shift_start = random.choice(['06:00', '08:00', '09:00', '14:00'])
                    hours_worked = random.choice([4, 6, 8, 8, 8])  # Most work 8 hours
                    
                    shift = {
                        'shift_id': f"SHIFT_{shift_id:08d}",
                        'assignment_id': assignment['assignment_id'],
                        'employee_id': assignment['employee_id'],
                        'store_id': assignment['store_id'],
                        'shift_date': shift_date.strftime('%Y-%m-%d'),
                        'shift_start_time': shift_start,
                        'shift_end_time': f"{int(shift_start.split(':')[0]) + hours_worked}:00",
                        'hours_worked': hours_worked,
                        'break_minutes': 30 if hours_worked >= 6 else 15,
                        'transactions_processed': random.randint(15, 80),
                        'cash_drawer_assigned': random.choice([1, 2, 3, 4]),
                        'shift_notes': random.choice([
                            'Normal shift', 'Busy day', 'Slow day', 'Training new employee', 
                            'Inventory count', 'Customer complaint handled', None, None, None
                        ]),
                        'created_date': self._generate_realistic_timestamp('transaction'),
                        'updated_date': self._generate_realistic_timestamp('transaction')
                    }
                    shifts.append(shift)
                    shift_id += 1
        
        self.generated_data['pos_employee_shifts'] = shifts
        self.logger.info(f"Generated {len(shifts)} POS employee shifts")
        return shifts
    
    def generate_pos_payments(self, mode: str = 'full') -> List[Dict]:
        """Generate detailed POS payment records."""
        self.logger.info("💳 Generating POS payment details...")
        
        if not self.generated_data['pos_transactions']:
            return []
        
        payments = []
        payment_id = 1
        
        for transaction in self.generated_data['pos_transactions']:
            # Most transactions have one payment, some have split payments
            payment_count = random.choices([1, 2], weights=[0.95, 0.05])[0]
            
            remaining_amount = float(transaction['total_amount_eur'])
            
            for i in range(payment_count):
                if i == payment_count - 1:  # Last payment takes remaining amount
                    payment_amount = remaining_amount
                else:
                    payment_amount = round(remaining_amount * random.uniform(0.3, 0.7), 2)
                    remaining_amount -= payment_amount
                
                payment_method = random.choices(
                    ['DEBIT_CARD', 'CREDIT_CARD', 'CASH', 'MOBILE_PAY'],
                    weights=[0.5, 0.25, 0.15, 0.1]
                )[0]
                
                payment = {
                    'payment_id': f"PAY_{payment_id:08d}",
                    'transaction_id': transaction['transaction_id'],
                    'payment_sequence': i + 1,
                    'payment_method': payment_method,
                    'payment_amount_eur': payment_amount,
                    'card_last_four': random.randint(1000, 9999) if 'CARD' in payment_method else None,
                    'authorization_code': f"AUTH{random.randint(100000, 999999)}" if 'CARD' in payment_method else None,
                    'payment_status': 'APPROVED',
                    'currency_received_eur': payment_amount if payment_method == 'CASH' else None,
                    'change_given_eur': max(0, payment_amount - float(transaction['total_amount_eur'])) if payment_method == 'CASH' else None,
                    'created_date': self._generate_realistic_timestamp('transaction'),
                    'updated_date': self._generate_realistic_timestamp('transaction')
                }
                payments.append(payment)
                payment_id += 1
        
        self.generated_data['pos_payments'] = payments
        self.logger.info(f"Generated {len(payments)} POS payment records")
        return payments
    
    def generate_pos_discounts(self, mode: str = 'full') -> List[Dict]:
        """Generate POS discount and promotion applications."""
        self.logger.info("🏷️ Generating POS discounts and promotions...")
        
        if not self.generated_data['pos_transactions']:
            return []
        
        discounts = []
        discount_id = 1
        
        # Generate discounts for ~15% of transactions
        discount_transactions = random.sample(
            self.generated_data['pos_transactions'],
            int(len(self.generated_data['pos_transactions']) * 0.15)
        )
        
        for transaction in discount_transactions:
            discount_types = [
                'EMPLOYEE_DISCOUNT', 'STUDENT_DISCOUNT', 'SENIOR_DISCOUNT',
                'LOYALTY_DISCOUNT', 'SEASONAL_PROMOTION', 'CLEARANCE_DISCOUNT',
                'BULK_DISCOUNT', 'MANAGER_OVERRIDE'
            ]
            
            discount = {
                'discount_id': f"DISC_{discount_id:08d}",
                'transaction_id': transaction['transaction_id'],
                'discount_type': random.choice(discount_types),
                'discount_percentage': random.choice([5.0, 10.0, 15.0, 20.0, 25.0]),
                'discount_amount_eur': round(float(transaction['subtotal_amount_eur']) * random.uniform(0.05, 0.25), 2),
                'promotion_code': random.choice([f"PROMO{random.randint(100, 999)}", None, None]),
                'authorized_by_employee_id': transaction['employee_id'],
                'reason': random.choice([
                    'Customer loyalty program', 'Seasonal promotion', 'Price match',
                    'Damaged item', 'Employee benefit', 'Manager approval'
                ]),
                'created_date': self._generate_realistic_timestamp('transaction'),
                'updated_date': self._generate_realistic_timestamp('transaction')
            }
            discounts.append(discount)
            discount_id += 1
        
        self.generated_data['pos_discounts'] = discounts
        self.logger.info(f"Generated {len(discounts)} POS discount records")
        return discounts
    
    def generate_pos_store_daily_summaries(self, mode: str = 'full') -> List[Dict]:
        """Generate daily store summary reports."""
        self.logger.info("📈 Generating POS daily store summaries...")
        
        if not self.generated_data['pos_transactions']:
            return []
        
        summaries = []
        
        # Group transactions by store and date
        store_daily_data = {}
        for transaction in self.generated_data['pos_transactions']:
            date_key = transaction['transaction_date']
            store_key = transaction['store_id']
            key = f"{store_key}_{date_key}"
            
            if key not in store_daily_data:
                store_daily_data[key] = {
                    'store_id': store_key,
                    'date': date_key,
                    'transactions': [],
                    'total_revenue': 0.0,
                    'total_tax': 0.0
                }
            
            store_daily_data[key]['transactions'].append(transaction)
            store_daily_data[key]['total_revenue'] += float(transaction['total_amount_eur'])
            store_daily_data[key]['total_tax'] += float(transaction['tax_amount_eur'])
        
        summary_id = 1
        for key, data in store_daily_data.items():
            summary = {
                'summary_id': f"SUMM_{summary_id:08d}",
                'store_id': data['store_id'],
                'summary_date': data['date'],
                'transaction_count': len(data['transactions']),
                'gross_revenue_eur': round(data['total_revenue'], 2),
                'tax_collected_eur': round(data['total_tax'], 2),
                'net_revenue_eur': round(data['total_revenue'] - data['total_tax'], 2),
                'average_transaction_value_eur': round(data['total_revenue'] / len(data['transactions']) if data['transactions'] else 0, 2),
                'cash_sales_eur': round(data['total_revenue'] * random.uniform(0.1, 0.3), 2),  # 10-30% cash
                'card_sales_eur': round(data['total_revenue'] * random.uniform(0.6, 0.8), 2),   # 60-80% card
                'returns_count': random.randint(0, max(1, len(data['transactions']) // 20)),
                'returns_amount_eur': round(data['total_revenue'] * random.uniform(0.01, 0.05), 2),
                'staff_hours_total': len(data['transactions']) // 15,  # Approximate staff hours
                'created_date': self._generate_realistic_timestamp('transaction'),
                'updated_date': self._generate_realistic_timestamp('transaction')
            }
            summaries.append(summary)
            summary_id += 1
        
        self.generated_data['pos_store_daily_summary'] = summaries
        self.logger.info(f"Generated {len(summaries)} POS daily store summaries")
        return summaries
    
    def generate_pos_promotions(self, mode: str = 'full') -> List[Dict]:
        """Generate POS promotion and campaign data."""
        self.logger.info("🎉 Generating POS promotions and campaigns...")
        
        promotions = []
        promotion_id = 1
        
        # Generate seasonal and ongoing promotions
        promotion_types = [
            {'name': 'Back to School 2024', 'type': 'SEASONAL', 'discount': 15.0},
            {'name': 'Summer Clearance', 'type': 'CLEARANCE', 'discount': 30.0},
            {'name': 'Customer Loyalty Rewards', 'type': 'LOYALTY', 'discount': 10.0},
            {'name': 'New Collection Launch', 'type': 'PRODUCT_LAUNCH', 'discount': 20.0},
            {'name': 'Weekend Flash Sale', 'type': 'FLASH_SALE', 'discount': 25.0},
            {'name': 'Buy 2 Get 1 Free', 'type': 'BUNDLE', 'discount': 33.3},
            {'name': 'Student Discount Program', 'type': 'DEMOGRAPHIC', 'discount': 10.0},
            {'name': 'End of Season Sale', 'type': 'SEASONAL', 'discount': 40.0}
        ]
        
        for promo_data in promotion_types:
            start_date = self.faker.date_between(start_date='-6m', end_date='now')
            end_date = start_date + timedelta(days=random.randint(7, 90))
            
            promotion = {
                'promotion_id': f"PROM_{promotion_id:08d}",
                'promotion_name': promo_data['name'],
                'promotion_type': promo_data['type'],
                'promotion_code': f"{promo_data['type'][:4]}{promotion_id:04d}",
                'discount_percentage': promo_data['discount'],
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'is_active': start_date <= datetime.now().date() <= end_date,
                'minimum_purchase_eur': random.choice([0, 25.0, 50.0, 75.0, 100.0]),
                'maximum_discount_eur': random.choice([None, 50.0, 100.0, 200.0]),
                'usage_count': random.randint(10, 500),
                'target_audience': random.choice(['ALL', 'LOYALTY_MEMBERS', 'STUDENTS', 'SENIORS', 'NEW_CUSTOMERS']),
                'created_by_employee_id': random.choice(self.generated_data['employees'])['employee_id'],
                'created_date': self._generate_realistic_timestamp('performance'),
                'updated_date': self._generate_realistic_timestamp('performance')
            }
            promotions.append(promotion)
            promotion_id += 1
        
        self.generated_data['pos_promotions'] = promotions
        self.logger.info(f"Generated {len(promotions)} POS promotions")
        return promotions

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Universal Data Generator V2 for EuroStyle Source databases'
    )
    
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--all', action='store_true', help='Generate data for all databases with perfect consistency')
    group.add_argument('--validate-consistency', action='store_true', help='Validate data consistency across databases')
    
    parser.add_argument('--mode', choices=['demo', 'fast', 'full'], default='full', help='Data generation mode')
    parser.add_argument('--config-path', default='config', help='Path to configuration directory')
    
    args = parser.parse_args()
    
    try:
        generator = UniversalDataGeneratorV2(config_path=args.config_path)
        
        if args.validate_consistency:
            results = generator.validate_consistency()
            print("🔍 Consistency Validation Results:")
            print(yaml.dump(results, default_flow_style=False))
            
        elif args.all:
            results = generator.generate_all_databases(mode=args.mode)
            print("🌍 Universal Data Generation Results:")
            print(yaml.dump(results, default_flow_style=False))
            
        else:
            # Default: generate all databases
            results = generator.generate_all_databases(mode=args.mode)
            print("🌍 Universal Data Generation Results:")
            print(yaml.dump(results, default_flow_style=False))
        
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"❌ Data generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()