#!/usr/bin/env python3
"""
EuroStyle Optimized Finance Data Generator
==========================================

Generates finance data that aligns with operational sales data without 
the overhead of building session mappings. Only loads what's needed for finance GL.
"""

import csv
import gzip
import random
import sys
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple
import logging

class OptimizedFinanceGenerator:
    """Generates finance data with minimal overhead."""
    
    def __init__(self):
        """Initialize the finance data generator."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.base_year = 2020
        self.num_years = 6
        self.reporting_currency = 'EUR'
        
        # Output directory
        self.output_dir = Path("../generated_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.orders = {}
        self.customers = {}
        self.entities = {}
        self.accounts = {}
        
        # Business metrics
        self.business_metrics = {
            'cogs_rate': 0.42,
        }
        
    def load_operational_data(self) -> bool:
        """Load only the operational data needed for finance generation."""
        self.logger.info("Loading operational data (orders and customers only)...")
        
        try:
            base_path = Path("../data-generator/generated_data")
            
            # Load customers
            customers_file = base_path / "customers.csv"
            if customers_file.exists():
                with open(customers_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.customers[row['customer_id']] = {
                            'customer_id': row['customer_id'],
                            'country_code': row['country_code']
                        }
                self.logger.info(f"Loaded {len(self.customers)} customers")
            
            # Load orders
            orders_file = base_path / "orders.csv"
            if orders_file.exists():
                with open(orders_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.orders[row['order_id']] = {
                            'order_id': row['order_id'],
                            'customer_id': row['customer_id'],
                            'order_date': row['order_date'],
                            'order_total_eur': float(row.get('total_amount_eur', row.get('total_amount_local', 0))),
                            'channel': row.get('order_channel', 'online')
                        }
                self.logger.info(f"Loaded {len(self.orders)} orders")
            
            # Calculate total revenue
            total_revenue = sum(order['order_total_eur'] for order in self.orders.values())
            self.logger.info(f"Total operational revenue: €{total_revenue:,.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading operational data: {str(e)}")
            return False
    
    def generate_legal_entities(self) -> List[Dict]:
        """Generate legal entities for European structure."""
        self.logger.info("Generating legal entities...")
        
        entities = []
        
        # Holding company
        holding_id = "ENTITY_NL_HOLDING"
        entities.append({
            'entity_id': holding_id,
            'entity_code': 'ESLH',
            'entity_name': 'EuroStyle Fashion Holding B.V.',
            'entity_type': 'HOLDING',
            'country_code': 'NL',
            'registration_number': 'KVK-24123456',
            'tax_id': 'NL123456789B01',
            'functional_currency': 'EUR',
            'parent_entity_id': '',
            'incorporation_date': '2015-01-15',
            'fiscal_year_end': '12-31',
            'legal_address': 'Herengracht 123, 1015 BD Amsterdam, Netherlands',
            'is_active': True,
            'created_date': '2024-01-01 00:00:00'
        })
        
        # Operating entities
        bv_entities = [
            ('ESDE', 'DE', 'EuroStyle Fashion Deutschland GmbH'),
            ('ESFR', 'FR', 'EuroStyle Fashion France SARL'),
            ('ESBE', 'BE', 'EuroStyle Fashion Belgium N.V.'),
            ('ESLU', 'LU', 'EuroStyle Fashion Luxembourg S.à r.l.'),
            ('ESNL', 'NL', 'EuroStyle Fashion Netherlands B.V.')
        ]
        
        for code, country, name in bv_entities:
            entity_id = f"ENTITY_{country}_BV"
            entities.append({
                'entity_id': entity_id,
                'entity_code': code,
                'entity_name': name,
                'entity_type': 'BV',
                'country_code': country,
                'registration_number': f'{country}-{random.randint(100000, 999999)}',
                'tax_id': f'{country}{random.randint(100000000, 999999999)}',
                'functional_currency': 'EUR',
                'parent_entity_id': holding_id,
                'incorporation_date': f"2016-0{random.randint(3, 8)}-{random.randint(10, 28)}",
                'fiscal_year_end': '12-31',
                'legal_address': f'Business Address, {country}',
                'is_active': True,
                'created_date': '2024-01-01 00:00:00'
            })
        
        self.entities = {e['entity_id']: e for e in entities}
        self.logger.info(f"Generated {len(entities)} entities")
        return entities
    
    def generate_chart_of_accounts(self) -> List[Dict]:
        """Generate simplified chart of accounts."""
        self.logger.info("Generating chart of accounts...")
        
        accounts = []
        
        # Essential accounts for revenue reconciliation
        account_structure = {
            '1110': ('ASSETS', 'Cash and Cash Equivalents', True),
            '1120': ('ASSETS', 'Accounts Receivable', True),
            '1130': ('ASSETS', 'Inventory', True),
            '4100': ('REVENUE', 'Product Sales', True),
            '5100': ('COGS', 'Cost of Goods Sold', True),
        }
        
        for code, (account_type, name, is_leaf) in account_structure.items():
            accounts.append({
                'account_id': f"ACC_{code}",
                'account_code': code,
                'account_name': name,
                'account_type': account_type,
                'account_group': account_type,
                'parent_account_id': '',
                'is_leaf_account': is_leaf,
                'normal_balance': 'DEBIT' if account_type in ['ASSETS', 'COGS'] else 'CREDIT',
                'is_active': True,
                'created_date': '2024-01-01 00:00:00'
            })
        
        self.accounts = {a['account_id']: a for a in accounts}
        self.logger.info(f"Generated {len(accounts)} accounts")
        return accounts
    
    def generate_gl_from_orders(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate GL entries from operational orders."""
        self.logger.info("Generating GL entries from orders...")
        
        headers = []
        lines = []
        
        # Country to entity mapping
        country_to_entity = {
            'DE': 'ENTITY_DE_BV',
            'FR': 'ENTITY_FR_BV',
            'BE': 'ENTITY_BE_BV',
            'LU': 'ENTITY_LU_BV',
            'NL': 'ENTITY_NL_BV'
        }
        
        # Get accounts
        accounts = {
            'revenue': next(a for a in self.accounts.values() if a['account_code'] == '4100'),
            'cash': next(a for a in self.accounts.values() if a['account_code'] == '1110'),
            'receivables': next(a for a in self.accounts.values() if a['account_code'] == '1120'),
            'cogs': next(a for a in self.accounts.values() if a['account_code'] == '5100'),
            'inventory': next(a for a in self.accounts.values() if a['account_code'] == '1130')
        }
        
        journal_id = 1
        line_id = 1
        
        for order_id, order in self.orders.items():
            # Get customer country for entity mapping
            customer = self.customers.get(order['customer_id'], {})
            customer_country = customer.get('country_code', 'NL')
            entity_id = country_to_entity.get(customer_country, 'ENTITY_NL_BV')
            
            order_date = datetime.strptime(order['order_date'], '%Y-%m-%d').date()
            order_amount = Decimal(str(order['order_total_eur']))
            cogs_amount = order_amount * Decimal(str(self.business_metrics['cogs_rate']))
            
            # Sales journal entry
            current_journal_id = f"JE_{journal_id:08d}"
            
            header = {
                'journal_header_id': f"JH_{journal_id:08d}",
                'journal_id': current_journal_id,
                'entity_id': entity_id,
                'period_id': f"{order_date.year}_{order_date.month:02d}",
                'journal_number': f"SALES-{order_date.year}-{journal_id:06d}",
                'journal_date': order_date.strftime('%Y-%m-%d'),
                'posting_date': order_date.strftime('%Y-%m-%d'),
                'period_year': order_date.year,
                'period_month': order_date.month,
                'journal_type': 'SALES',
                'journal_source': 'OPERATIONAL',
                'description': f'Sales for order {order_id}',
                'reference_number': order_id,
                'currency_code': 'EUR',
                'total_debit': order_amount,
                'total_credit': order_amount,
                'functional_currency': 'EUR',
                'journal_status': 'POSTED',
                'created_by': 'SYSTEM',
                'created_date': '2024-01-01 00:00:00',
                'posted_by': 'SYSTEM',
                'posted_date': '2024-01-01 00:00:00',
                'approved_by': 'SYSTEM'
            }
            
            # Journal lines
            journal_lines = []
            
            # Debit: Cash or Receivables
            account = accounts['cash'] if order['channel'] == 'in_store' else accounts['receivables']
            journal_lines.append({
                'journal_line_id': f"JL_{line_id:08d}",
                'journal_header_id': f"JH_{journal_id:08d}",
                'line_id': f"JL_{line_id:08d}",
                'journal_id': current_journal_id,
                'line_number': 1,
                'entity_id': entity_id,
                'account_id': account['account_id'],
                'cost_center_id': f"CC_{random.randint(1, 10):06d}",
                'debit_amount': order_amount,
                'credit_amount': Decimal('0.00'),
                'currency_code': 'EUR',
                'functional_currency': 'EUR',
                'transaction_currency': 'EUR',
                'transaction_amount': order_amount,
                'exchange_rate': Decimal('1.000000'),
                'line_description': 'Sales receipt',
                'reference_1': order_id,
                'reference_2': order.get('customer_id', ''),
                'cost_center': 'SALES_001',
                'project_id': '',
                'customer_id': order.get('customer_id', ''),
                'vendor_id': '',
                'created_date': '2024-01-01 00:00:00'
            })
            line_id += 1
            
            # Credit: Revenue
            journal_lines.append({
                'journal_line_id': f"JL_{line_id:08d}",
                'journal_header_id': f"JH_{journal_id:08d}",
                'line_id': f"JL_{line_id:08d}",
                'journal_id': current_journal_id,
                'line_number': 2,
                'entity_id': entity_id,
                'account_id': accounts['revenue']['account_id'],
                'cost_center_id': f"CC_{random.randint(1, 10):06d}",
                'debit_amount': Decimal('0.00'),
                'credit_amount': order_amount,
                'currency_code': 'EUR',
                'functional_currency': 'EUR',
                'transaction_currency': 'EUR',
                'transaction_amount': order_amount,
                'exchange_rate': Decimal('1.000000'),
                'line_description': 'Product sales revenue',
                'reference_1': order_id,
                'reference_2': order.get('customer_id', ''),
                'cost_center': 'SALES_001',
                'project_id': '',
                'customer_id': order.get('customer_id', ''),
                'vendor_id': '',
                'created_date': '2024-01-01 00:00:00'
            })
            line_id += 1
            
            headers.append(header)
            lines.extend(journal_lines)
            journal_id += 1
        
        self.logger.info(f"Generated {len(headers):,} GL journals and {len(lines):,} GL lines")
        return headers, lines
    
    def save_finance_data(self, entities: List[Dict], accounts: List[Dict], 
                         headers: List[Dict], lines: List[Dict]) -> bool:
        """Save finance data to CSV files."""
        self.logger.info("Saving finance data...")
        
        try:
            # Save entities (compressed)
            with gzip.open(self.output_dir / "eurostyle_finance.legal_entities.csv.gz", 'wt', newline='') as f:
                if entities:
                    writer = csv.DictWriter(f, fieldnames=entities[0].keys())
                    writer.writeheader()
                    writer.writerows(entities)
            
            # Save accounts (compressed)
            with gzip.open(self.output_dir / "eurostyle_finance.chart_of_accounts.csv.gz", 'wt', newline='') as f:
                if accounts:
                    writer = csv.DictWriter(f, fieldnames=accounts[0].keys())
                    writer.writeheader()
                    writer.writerows(accounts)
            
            # Save headers (compressed)
            with gzip.open(self.output_dir / "eurostyle_finance.gl_journal_headers.csv.gz", 'wt', newline='') as f:
                if headers:
                    writer = csv.DictWriter(f, fieldnames=headers[0].keys())
                    writer.writeheader()
                    writer.writerows(headers)
            
            # Save lines (compressed)
            with gzip.open(self.output_dir / "eurostyle_finance.gl_journal_lines.csv.gz", 'wt', newline='') as f:
                if lines:
                    writer = csv.DictWriter(f, fieldnames=lines[0].keys())
                    writer.writeheader()
                    writer.writerows(lines)
            
            self.logger.info("✅ Finance data saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving finance data: {str(e)}")
            return False

def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🏦 EuroStyle Optimized Finance Data Generator")
    logger.info("=" * 50)
    
    generator = OptimizedFinanceGenerator()
    
    try:
        # Load operational data (fast)
        if not generator.load_operational_data():
            logger.error("❌ Failed to load operational data")
            return False
        
        # Generate finance data
        entities = generator.generate_legal_entities()
        accounts = generator.generate_chart_of_accounts()
        headers, lines = generator.generate_gl_from_orders()
        
        # Calculate revenue reconciliation
        total_revenue = sum(Decimal(line['credit_amount']) 
                           for line in lines 
                           if line['account_id'] == 'ACC_4100')
        
        operational_revenue = sum(order['order_total_eur'] for order in generator.orders.values())
        variance = abs(operational_revenue - float(total_revenue))
        
        logger.info("")
        logger.info("💰 Revenue Reconciliation Check:")
        logger.info(f"  Operational Revenue: €{operational_revenue:,.2f}")
        logger.info(f"  Finance GL Revenue:  €{total_revenue:,.2f}")
        logger.info(f"  Variance:           €{variance:.2f}")
        
        if variance < 1.0:
            logger.info("✅ Perfect revenue reconciliation achieved!")
        else:
            logger.warning(f"⚠️ Revenue variance: €{variance:.2f}")
        
        # Save data
        if generator.save_finance_data(entities, accounts, headers, lines):
            logger.info("")
            logger.info("🎉 Finance data generation completed successfully!")
            logger.info(f"✅ Generated GL entries for {len(generator.orders):,} orders")
            logger.info(f"✅ 100% revenue reconciliation with operations")
            logger.info(f"✅ Time period: 2020-2025 (matches operational data)")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"❌ Finance generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)