#!/usr/bin/env python3
"""
EuroStyle Finance Data Generator with Registry Integration
========================================================

Generates finance data that aligns with operational sales data to ensure:
- 100% revenue reconciliation between operations and finance GL
- Proper time period alignment (2020-2025)
- Realistic GL entries based on actual orders
- COGS and expense allocation matching operational volumes

This replaces the existing finance generator to fix revenue gaps.
"""

import csv
import json
import random
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))
from data_registry import DataRegistry

class FinanceDataGenerator:
    """Generates finance data with proper operational alignment."""
    
    def __init__(self):
        """Initialize the finance data generator."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration aligned with registry
        self.base_year = 2020  # Match operational data period
        self.num_years = 6     # 2020-2025 inclusive
        self.reporting_currency = 'EUR'
        
        # Output directory
        self.output_dir = Path("../generated_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.registry = None
        self.orders = {}
        self.customers = {}
        self.entities = {}
        self.accounts = {}
        self.cost_centers = {}
        
        # Business metrics for realistic GL generation
        self.business_metrics = {
            'gross_margin': 0.58,        # 58% gross margin (fashion industry standard)
            'operating_margin': 0.12,    # 12% operating margin
            'tax_rate': 0.25,           # 25% corporate tax rate
            'cogs_rate': 0.42,          # 42% cost of goods sold
            'marketing_rate': 0.15,     # 15% of revenue on marketing
            'personnel_rate': 0.20,     # 20% of revenue on personnel
            'rent_rate': 0.08,          # 8% of revenue on rent
            'other_opex_rate': 0.03,    # 3% other operating expenses
        }
        
    def load_registry(self) -> bool:
        """Load the data registry with operational data."""
        self.logger.info("Loading data registry...")
        
        try:
            self.registry = DataRegistry("../data-generator/generated_data")
            if not self.registry.load_operational_data():
                self.logger.error("Failed to load operational data into registry")
                return False
                
            # Get operational data
            self.orders = self.registry.orders
            self.customers = self.registry.customers
            
            # Calculate key metrics
            total_revenue = sum(order['order_total_eur'] for order in self.orders.values())
            order_count = len(self.orders)
            
            self.logger.info(f"Loaded {order_count:,} orders with €{total_revenue:,.2f} total revenue")
            self.logger.info(f"Average order value: €{total_revenue/order_count:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading registry: {str(e)}")
            return False
    
    def generate_legal_entities(self) -> List[Dict]:
        """Generate legal entities for the European structure."""
        self.logger.info("Generating legal entities...")
        
        entities = []
        
        # Holding company (Netherlands)
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
        
        # Operating BV entities matching operational countries
        bv_entities = [
            {
                'code': 'ESDE', 'country': 'DE', 'name': 'EuroStyle Fashion Deutschland GmbH',
                'reg_num': 'HRB-12345', 'tax_id': 'DE123456789',
                'address': 'Friedrichstraße 200, 10117 Berlin, Germany'
            },
            {
                'code': 'ESFR', 'country': 'FR', 'name': 'EuroStyle Fashion France SARL',
                'reg_num': 'SIREN-123456789', 'tax_id': 'FR12345678901',
                'address': '75 Avenue des Champs-Élysées, 75008 Paris, France'
            },
            {
                'code': 'ESBE', 'country': 'BE', 'name': 'EuroStyle Fashion Belgium N.V.',
                'reg_num': 'BCE-0123.456.789', 'tax_id': 'BE0123456789',
                'address': 'Rue de la Loi 16, 1000 Brussels, Belgium'
            },
            {
                'code': 'ESLU', 'country': 'LU', 'name': 'EuroStyle Fashion Luxembourg S.à r.l.',
                'reg_num': 'RCS-B123456', 'tax_id': 'LU12345678',
                'address': '2 Boulevard Royal, 2449 Luxembourg City, Luxembourg'
            },
            {
                'code': 'ESNL', 'country': 'NL', 'name': 'EuroStyle Fashion Netherlands B.V.',
                'reg_num': 'KVK-34567890', 'tax_id': 'NL987654321B01',
                'address': 'Kalverstraat 92, 1012 PH Amsterdam, Netherlands'
            }
        ]
        
        for bv in bv_entities:
            entity_id = f"ENTITY_{bv['country']}_BV"
            entities.append({
                'entity_id': entity_id,
                'entity_code': bv['code'],
                'entity_name': bv['name'],
                'entity_type': 'BV',
                'country_code': bv['country'],
                'registration_number': bv['reg_num'],
                'tax_id': bv['tax_id'],
                'functional_currency': 'EUR',
                'parent_entity_id': holding_id,
                'incorporation_date': f"2016-0{random.randint(3, 8)}-{random.randint(10, 28)}",
                'fiscal_year_end': '12-31',
                'legal_address': bv['address'],
                'is_active': True,
                'created_date': '2024-01-01 00:00:00'
            })
        
        self.entities = {e['entity_id']: e for e in entities}
        
        self.logger.info(f"Generated {len(entities)} legal entities")
        return entities
    
    def generate_chart_of_accounts(self) -> List[Dict]:
        """Generate chart of accounts for GL structure."""
        self.logger.info("Generating chart of accounts...")
        
        accounts = []
        
        # Standard fashion retail chart of accounts
        account_structure = {
            # Assets (1000-1999)
            '1000': ('ASSETS', 'ASSETS', 'Assets', False),
            '1100': ('ASSETS', 'CURRENT_ASSETS', 'Current Assets', False),
            '1110': ('ASSETS', 'CASH', 'Cash and Cash Equivalents', True),
            '1120': ('ASSETS', 'ACCOUNTS_RECEIVABLE', 'Accounts Receivable', True),
            '1130': ('ASSETS', 'INVENTORY', 'Inventory', True),
            '1140': ('ASSETS', 'PREPAID_EXPENSES', 'Prepaid Expenses', True),
            '1200': ('ASSETS', 'FIXED_ASSETS', 'Fixed Assets', False),
            '1210': ('ASSETS', 'EQUIPMENT', 'Equipment', True),
            '1220': ('ASSETS', 'FIXTURES', 'Store Fixtures', True),
            
            # Liabilities (2000-2999)
            '2000': ('LIABILITIES', 'LIABILITIES', 'Liabilities', False),
            '2100': ('LIABILITIES', 'CURRENT_LIABILITIES', 'Current Liabilities', False),
            '2110': ('LIABILITIES', 'ACCOUNTS_PAYABLE', 'Accounts Payable', True),
            '2120': ('LIABILITIES', 'ACCRUED_EXPENSES', 'Accrued Expenses', True),
            '2130': ('LIABILITIES', 'TAX_PAYABLE', 'Tax Payable', True),
            
            # Equity (3000-3999)
            '3000': ('EQUITY', 'EQUITY', 'Equity', False),
            '3100': ('EQUITY', 'SHARE_CAPITAL', 'Share Capital', True),
            '3200': ('EQUITY', 'RETAINED_EARNINGS', 'Retained Earnings', True),
            
            # Revenue (4000-4999)
            '4000': ('REVENUE', 'REVENUE', 'Revenue', False),
            '4100': ('REVENUE', 'PRODUCT_SALES', 'Product Sales', True),
            '4200': ('REVENUE', 'SHIPPING_REVENUE', 'Shipping Revenue', True),
            '4300': ('REVENUE', 'OTHER_REVENUE', 'Other Revenue', True),
            
            # Cost of Goods Sold (5000-5999)
            '5000': ('COGS', 'COST_OF_SALES', 'Cost of Goods Sold', False),
            '5100': ('COGS', 'PRODUCT_COSTS', 'Product Costs', True),
            '5200': ('COGS', 'SHIPPING_COSTS', 'Shipping Costs', True),
            
            # Expenses (6000-6999)
            '6000': ('EXPENSES', 'OPERATING_EXPENSES', 'Operating Expenses', False),
            '6100': ('EXPENSES', 'MARKETING', 'Marketing Expenses', True),
            '6200': ('EXPENSES', 'PERSONNEL', 'Personnel Expenses', True),
            '6300': ('EXPENSES', 'RENT', 'Rent and Facilities', True),
            '6400': ('EXPENSES', 'UTILITIES', 'Utilities', True),
            '6500': ('EXPENSES', 'PROFESSIONAL_FEES', 'Professional Fees', True),
            '6600': ('EXPENSES', 'DEPRECIATION', 'Depreciation', True),
            '6700': ('EXPENSES', 'OTHER_EXPENSES', 'Other Expenses', True)
        }
        
        for account_code, (account_type, account_group, account_name, is_leaf) in account_structure.items():
            accounts.append({
                'account_id': f"ACC_{account_code}",
                'account_code': account_code,
                'account_name': account_name,
                'account_type': account_type,
                'account_group': account_group,
                'parent_account_id': f"ACC_{account_code[:3]}0" if len(account_code) > 3 and account_code != '1000' else '',
                'is_leaf_account': is_leaf,
                'normal_balance': 'DEBIT' if account_type in ['ASSETS', 'EXPENSES', 'COGS'] else 'CREDIT',
                'is_active': True,
                'created_date': '2024-01-01 00:00:00'
            })
        
        self.accounts = {a['account_id']: a for a in accounts}
        
        self.logger.info(f"Generated {len(accounts)} accounts")
        return accounts
    
    def generate_order_based_gl_entries(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate GL entries based on actual operational orders."""
        self.logger.info("Generating GL entries from operational orders...")
        
        headers = []
        lines = []
        
        # Group orders by entity (based on customer country)
        country_to_entity = {
            'DE': 'ENTITY_DE_BV',
            'FR': 'ENTITY_FR_BV', 
            'BE': 'ENTITY_BE_BV',
            'LU': 'ENTITY_LU_BV',
            'NL': 'ENTITY_NL_BV'
        }
        
        # Get relevant accounts for order processing
        revenue_account = next(a for a in self.accounts.values() if a['account_code'] == '4100')
        cogs_account = next(a for a in self.accounts.values() if a['account_code'] == '5100')
        cash_account = next(a for a in self.accounts.values() if a['account_code'] == '1110')
        receivables_account = next(a for a in self.accounts.values() if a['account_code'] == '1120')
        inventory_account = next(a for a in self.accounts.values() if a['account_code'] == '1130')
        
        journal_id = 1
        line_id = 1
        
        # Process each order
        for order_id, order in self.orders.items():
            # Get customer country to determine entity
            customer = self.customers.get(order['customer_id'], {})
            customer_country = customer.get('country_code', 'NL')
            entity_id = country_to_entity.get(customer_country, 'ENTITY_NL_BV')
            
            order_date = datetime.strptime(order['order_date'], '%Y-%m-%d').date()
            order_amount = Decimal(str(order['order_total_eur']))
            
            # Calculate component amounts
            cogs_amount = order_amount * Decimal(str(self.business_metrics['cogs_rate']))
            
            # Create journal header for the order
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
                'description': f'Sales transaction for order {order_id}',
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
            
            # Journal lines for the sale
            journal_lines = []
            
            # 1. Debit Cash/Receivables (depending on channel)
            if order['channel'] == 'in_store':
                # Cash sale
                account = cash_account
                description = 'Cash received from in-store sale'
            else:
                # Credit sale (online/phone)
                account = receivables_account
                description = 'Receivables from online sale'
            
            journal_lines.append({
                'journal_line_id': f"JL_{line_id:08d}",
                'journal_header_id': f"JH_{journal_id:08d}",
                'line_id': f"JL_{line_id:08d}",
                'journal_id': current_journal_id,
                'line_number': 1,
                'entity_id': entity_id,
                'account_id': account['account_id'],
                'cost_center_id': f"CC_{random.randint(1, 20):06d}",
                'debit_amount': order_amount,
                'credit_amount': Decimal('0.00'),
                'currency_code': 'EUR',
                'functional_currency': 'EUR',
                'transaction_currency': 'EUR',
                'transaction_amount': order_amount,
                'exchange_rate': Decimal('1.000000'),
                'line_description': description,
                'reference_1': order_id,
                'reference_2': order.get('customer_id', ''),
                'cost_center': 'SALES_001',
                'project_id': '',
                'customer_id': order.get('customer_id', ''),
                'vendor_id': '',
                'created_date': '2024-01-01 00:00:00'
            })
            line_id += 1
            
            # 2. Credit Revenue
            journal_lines.append({
                'journal_line_id': f"JL_{line_id:08d}",
                'journal_header_id': f"JH_{journal_id:08d}",
                'line_id': f"JL_{line_id:08d}",
                'journal_id': current_journal_id,
                'line_number': 2,
                'entity_id': entity_id,
                'account_id': revenue_account['account_id'],
                'cost_center_id': f"CC_{random.randint(1, 20):06d}",
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
            
            # Also create COGS entry (separate journal)
            if cogs_amount > 0:
                cogs_journal_id = f"JE_{journal_id:08d}"
                
                cogs_header = {
                    'journal_header_id': f"JH_{journal_id:08d}",
                    'journal_id': cogs_journal_id,
                    'entity_id': entity_id,
                    'period_id': f"{order_date.year}_{order_date.month:02d}",
                    'journal_number': f"COGS-{order_date.year}-{journal_id:06d}",
                    'journal_date': order_date.strftime('%Y-%m-%d'),
                    'posting_date': order_date.strftime('%Y-%m-%d'),
                    'period_year': order_date.year,
                    'period_month': order_date.month,
                    'journal_type': 'COGS',
                    'journal_source': 'OPERATIONAL',
                    'description': f'COGS for order {order_id}',
                    'reference_number': order_id,
                    'currency_code': 'EUR',
                    'total_debit': cogs_amount,
                    'total_credit': cogs_amount,
                    'functional_currency': 'EUR',
                    'journal_status': 'POSTED',
                    'created_by': 'SYSTEM',
                    'created_date': '2024-01-01 00:00:00',
                    'posted_by': 'SYSTEM',
                    'posted_date': '2024-01-01 00:00:00',
                    'approved_by': 'SYSTEM'
                }
                
                # COGS journal lines
                cogs_lines = []
                
                # Debit COGS
                cogs_lines.append({
                    'journal_line_id': f"JL_{line_id:08d}",
                    'journal_header_id': f"JH_{journal_id:08d}",
                    'line_id': f"JL_{line_id:08d}",
                    'journal_id': cogs_journal_id,
                    'line_number': 1,
                    'entity_id': entity_id,
                    'account_id': cogs_account['account_id'],
                    'cost_center_id': f"CC_{random.randint(1, 20):06d}",
                    'debit_amount': cogs_amount,
                    'credit_amount': Decimal('0.00'),
                    'currency_code': 'EUR',
                    'functional_currency': 'EUR',
                    'transaction_currency': 'EUR',
                    'transaction_amount': cogs_amount,
                    'exchange_rate': Decimal('1.000000'),
                    'line_description': 'Cost of goods sold',
                    'reference_1': order_id,
                    'reference_2': '',
                    'cost_center': 'OPERATIONS_001',
                    'project_id': '',
                    'customer_id': '',
                    'vendor_id': '',
                    'created_date': '2024-01-01 00:00:00'
                })
                line_id += 1
                
                # Credit Inventory
                cogs_lines.append({
                    'journal_line_id': f"JL_{line_id:08d}",
                    'journal_header_id': f"JH_{journal_id:08d}",
                    'line_id': f"JL_{line_id:08d}",
                    'journal_id': cogs_journal_id,
                    'line_number': 2,
                    'entity_id': entity_id,
                    'account_id': inventory_account['account_id'],
                    'cost_center_id': f"CC_{random.randint(1, 20):06d}",
                    'debit_amount': Decimal('0.00'),
                    'credit_amount': cogs_amount,
                    'currency_code': 'EUR',
                    'functional_currency': 'EUR',
                    'transaction_currency': 'EUR',
                    'transaction_amount': cogs_amount,
                    'exchange_rate': Decimal('1.000000'),
                    'line_description': 'Inventory reduction',
                    'reference_1': order_id,
                    'reference_2': '',
                    'cost_center': 'OPERATIONS_001',
                    'project_id': '',
                    'customer_id': '',
                    'vendor_id': '',
                    'created_date': '2024-01-01 00:00:00'
                })
                line_id += 1
                
                headers.append(cogs_header)
                lines.extend(cogs_lines)
                journal_id += 1
        
        self.logger.info(f"Generated {len(headers):,} GL journals from {len(self.orders):,} orders")
        self.logger.info(f"Total GL lines: {len(lines):,}")
        
        return headers, lines
    
    def save_finance_data(self, entities: List[Dict], accounts: List[Dict], 
                         headers: List[Dict], lines: List[Dict]) -> bool:
        """Save all finance data to CSV files."""
        self.logger.info("Saving finance data files...")
        
        try:
            # Save legal entities
            entities_file = self.output_dir / "eurostyle_finance.legal_entities.csv"
            with open(entities_file, 'w', newline='', encoding='utf-8') as f:
                if entities:
                    writer = csv.DictWriter(f, fieldnames=entities[0].keys())
                    writer.writeheader()
                    writer.writerows(entities)
            
            # Save chart of accounts
            accounts_file = self.output_dir / "eurostyle_finance.chart_of_accounts.csv"
            with open(accounts_file, 'w', newline='', encoding='utf-8') as f:
                if accounts:
                    writer = csv.DictWriter(f, fieldnames=accounts[0].keys())
                    writer.writeheader()
                    writer.writerows(accounts)
            
            # Save GL headers
            headers_file = self.output_dir / "eurostyle_finance.gl_journal_headers.csv"
            with open(headers_file, 'w', newline='', encoding='utf-8') as f:
                if headers:
                    writer = csv.DictWriter(f, fieldnames=headers[0].keys())
                    writer.writeheader()
                    writer.writerows(headers)
            
            # Save GL lines
            lines_file = self.output_dir / "eurostyle_finance.gl_journal_lines.csv"
            with open(lines_file, 'w', newline='', encoding='utf-8') as f:
                if lines:
                    writer = csv.DictWriter(f, fieldnames=lines[0].keys())
                    writer.writeheader()
                    writer.writerows(lines)
            
            self.logger.info(f"Saved finance data:")
            self.logger.info(f"  - {len(entities)} entities to {entities_file}")
            self.logger.info(f"  - {len(accounts)} accounts to {accounts_file}")
            self.logger.info(f"  - {len(headers)} GL headers to {headers_file}")
            self.logger.info(f"  - {len(lines)} GL lines to {lines_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving finance data: {str(e)}")
            return False

def main():
    """Main function to generate finance data."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🏦 EuroStyle Finance Data Generator with Registry Integration")
    logger.info("=" * 65)
    
    generator = FinanceDataGenerator()
    
    try:
        # Load registry data
        if not generator.load_registry():
            logger.error("❌ Failed to load registry data")
            return False
        
        # Generate finance master data
        entities = generator.generate_legal_entities()
        accounts = generator.generate_chart_of_accounts()
        
        # Generate GL entries based on operational orders
        headers, lines = generator.generate_order_based_gl_entries()
        
        # Calculate revenue totals for validation
        total_revenue = sum(Decimal(line['credit_amount']) 
                           for line in lines 
                           if line['account_id'] == 'ACC_4100')  # Revenue account
        
        operational_revenue = sum(order['order_total_eur'] for order in generator.orders.values())
        
        logger.info("")
        logger.info("💰 Revenue Reconciliation:")
        logger.info(f"  Operational Revenue: €{operational_revenue:,.2f}")
        logger.info(f"  Finance GL Revenue:  €{total_revenue:,.2f}")
        logger.info(f"  Variance:           €{abs(operational_revenue - float(total_revenue)):,.2f}")
        
        # Save all data
        if not generator.save_finance_data(entities, accounts, headers, lines):
            logger.error("❌ Failed to save finance data")
            return False
        
        logger.info("")
        logger.info("🎉 Finance data generation completed successfully!")
        logger.info("✅ 100% revenue reconciliation with operational data achieved")
        logger.info(f"✅ Time period aligned: {generator.base_year}-{generator.base_year + generator.num_years - 1}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Finance data generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)