#!/usr/bin/env python3

"""
EuroStyle Fashion - Finance Data Generator
==========================================
Generates comprehensive financial data for a European fashion retail company
with multi-country BV structure and holding company relationships.

Features:
- Multi-country legal entities (Netherlands Holding + 4 BV subsidiaries)
- Complete chart of accounts with IFRS compliance
- Multi-currency support with realistic exchange rates
- General ledger transactions with referential integrity
- Budget data and consolidation adjustments
- Fixed assets and depreciation schedules
- Management reporting and compliance data

Author: EuroStyle Fashion Data Team
Date: 2024-10-10
"""

import csv
import random
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import os
import sys
from typing import Dict, List, Tuple, Optional
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EuroStyleFinanceGenerator:
    """Generates comprehensive finance data for EuroStyle Fashion multi-country structure."""
    
    def __init__(self):
        """Initialize the finance data generator."""
        print("🏦 Initializing EuroStyle Fashion Finance Data Generator...")
        
        # Configuration
        self.base_year = 2023
        self.num_years = 2  # 2023-2024
        self.reporting_currency = 'EUR'
        
        # File paths  
        self.output_dir = "data/csv"  # Output to data/csv directory
        self.csv_files = {}
        
        # Data containers
        self.entities = {}
        self.accounts = {}
        self.currencies = {}
        self.exchange_rates = {}
        self.cost_centers = {}
        self.periods = {}
        
        # External data references (loaded from other systems)
        self.customers = []
        self.orders = []
        self.campaigns = []
        self.stores = []
        
        # European business structure - EuroStyle countries: NL, DE, FR, BE, LU
        self.countries = {
            'NL': {'name': 'Netherlands', 'currency': 'EUR', 'vat_rate': 0.21},
            'DE': {'name': 'Germany', 'currency': 'EUR', 'vat_rate': 0.19},
            'FR': {'name': 'France', 'currency': 'EUR', 'vat_rate': 0.20},
            'BE': {'name': 'Belgium', 'currency': 'EUR', 'vat_rate': 0.21},
            'LU': {'name': 'Luxembourg', 'currency': 'EUR', 'vat_rate': 0.17}
        }
        
        # Fiscal calendar
        self.fiscal_year_end = "12-31"  # December 31
        
        print("✅ Finance generator initialized")
    
    def load_external_data(self):
        """Load existing data from operational systems for referential integrity."""
        print("\n📊 Loading external data for referential integrity...")
        
        try:
            # Load customer data
            if os.path.exists("eurostyle_operational.customers.csv"):
                with open("eurostyle_operational.customers.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.customers = list(reader)
                print(f"Loaded {len(self.customers):,} customers")
            
            # Load order data
            if os.path.exists("eurostyle_operational.orders.csv"):
                with open("eurostyle_operational.orders.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.orders = list(reader)
                print(f"Loaded {len(self.orders):,} orders")
            
            # Load campaign data
            if os.path.exists("eurostyle_operational.campaigns.csv"):
                with open("eurostyle_operational.campaigns.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.campaigns = list(reader)
                print(f"Loaded {len(self.campaigns):,} campaigns")
            
            # Load store data
            if os.path.exists("eurostyle_operational.stores.csv"):
                with open("eurostyle_operational.stores.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.stores = list(reader)
                print(f"Loaded {len(self.stores):,} stores")
                
        except Exception as e:
            print(f"⚠️ Could not load all external data: {e}")
            print("Will generate finance data independently...")
    
    def generate_legal_entities(self) -> List[Dict]:
        """Generate legal entities with holding structure."""
        print("\n🏢 Generating legal entities...")
        
        entities = []
        
        # 1. Holding Company (Netherlands)
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
            'fiscal_year_end': self.fiscal_year_end,
            'legal_address': 'Herengracht 123, 1015 BD Amsterdam, Netherlands',
            'is_active': True,
            'created_date': '2024-01-01 00:00:00'
        })
        
        # 2. Operating BV entities - EuroStyle countries: DE, FR, BE, LU
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
                'functional_currency': self.countries[bv['country']]['currency'],
                'parent_entity_id': holding_id,
                'incorporation_date': f"2016-0{random.randint(3, 8)}-{random.randint(10, 28)}",
                'fiscal_year_end': self.fiscal_year_end,
                'legal_address': bv['address'],
                'is_active': True,
                'created_date': '2024-01-01 00:00:00'
            })
        
        # Store for later reference
        self.entities = {e['entity_id']: e for e in entities}
        
        print(f"Generated {len(entities)} legal entities (1 holding + {len(entities)-1} BVs)")
        return entities
    
    def generate_entity_relationships(self) -> List[Dict]:
        """Generate entity relationships for consolidation."""
        print("🔗 Generating entity relationships...")
        
        relationships = []
        holding_id = "ENTITY_NL_HOLDING"
        
        # Holding owns 100% of all BVs
        for entity_id, entity in self.entities.items():
            if entity['entity_type'] == 'BV':
                relationships.append({
                    'relationship_id': f"REL_{entity_id}",
                    'parent_entity_id': holding_id,
                    'child_entity_id': entity_id,
                    'ownership_percentage': Decimal('100.00'),
                    'consolidation_method': 'FULL',
                    'effective_from': '2016-01-01',
                    'effective_to': '',
                    'created_date': '2024-01-01 00:00:00'
                })
        
        print(f"Generated {len(relationships)} ownership relationships")
        return relationships
    
    def generate_chart_of_accounts(self) -> List[Dict]:
        """Generate comprehensive chart of accounts following IFRS."""
        print("📈 Generating chart of accounts...")
        
        accounts = []
        
        # IFRS-compliant chart of accounts structure
        account_structure = {
            # ASSETS (1000-1999)
            'ASSETS': {
                'range': (1000, 1999),
                'normal_balance': 'DEBIT',
                'categories': {
                    'Current Assets': {
                        'Cash and Cash Equivalents': ['Cash', 'Bank Current Account', 'Short-term Deposits'],
                        'Trade Receivables': ['Accounts Receivable', 'Allowance for Doubtful Accounts'],
                        'Inventory': ['Raw Materials', 'Finished Goods', 'Inventory Provision'],
                        'Other Current Assets': ['Prepaid Expenses', 'VAT Receivable', 'Other Receivables']
                    },
                    'Non-current Assets': {
                        'Property, Plant & Equipment': ['Land & Buildings', 'Equipment', 'Accumulated Depreciation'],
                        'Intangible Assets': ['Software', 'Trademarks', 'Goodwill'],
                        'Financial Assets': ['Long-term Investments', 'Deferred Tax Assets']
                    }
                }
            },
            
            # LIABILITIES (2000-2999)
            'LIABILITIES': {
                'range': (2000, 2999),
                'normal_balance': 'CREDIT',
                'categories': {
                    'Current Liabilities': {
                        'Trade Payables': ['Accounts Payable', 'Accrued Expenses'],
                        'Tax Liabilities': ['VAT Payable', 'Income Tax Payable', 'Payroll Tax Payable'],
                        'Other Current Liabilities': ['Short-term Debt', 'Customer Deposits']
                    },
                    'Non-current Liabilities': {
                        'Long-term Debt': ['Long-term Loans', 'Bonds Payable'],
                        'Provisions': ['Warranty Provisions', 'Restructuring Provisions']
                    }
                }
            },
            
            # EQUITY (3000-3999)
            'EQUITY': {
                'range': (3000, 3999),
                'normal_balance': 'CREDIT',
                'categories': {
                    'Share Capital': {
                        'Capital': ['Share Capital', 'Share Premium'],
                        'Reserves': ['Legal Reserves', 'Retained Earnings', 'Currency Translation Reserve']
                    }
                }
            },
            
            # REVENUE (4000-4999)
            'REVENUE': {
                'range': (4000, 4999),
                'normal_balance': 'CREDIT',
                'categories': {
                    'Sales Revenue': {
                        'Product Sales': ['Retail Sales', 'Wholesale Sales', 'Online Sales'],
                        'Other Revenue': ['License Revenue', 'Interest Income']
                    }
                }
            },
            
            # EXPENSES (5000-9999)
            'EXPENSES': {
                'range': (5000, 9999),
                'normal_balance': 'DEBIT',
                'categories': {
                    'Cost of Sales': {
                        'Direct Costs': ['Cost of Goods Sold', 'Purchase Discounts']
                    },
                    'Operating Expenses': {
                        'Personnel': ['Salaries', 'Social Security', 'Pension Costs'],
                        'Facilities': ['Rent', 'Utilities', 'Insurance'],
                        'Marketing': ['Advertising', 'Promotions', 'Trade Shows'],
                        'General': ['Professional Services', 'IT Costs', 'Travel']
                    },
                    'Financial': {
                        'Finance Costs': ['Interest Expense', 'Bank Charges', 'FX Losses']
                    },
                    'Tax': {
                        'Income Tax': ['Current Tax', 'Deferred Tax']
                    }
                }
            }
        }
        
        account_id = 1
        account_code = 1000
        
        for account_type, type_info in account_structure.items():
            # Create parent account for each type
            parent_account_id = f"ACC_{account_id:06d}"
            accounts.append({
                'account_id': parent_account_id,
                'account_code': str(account_code),
                'account_name': account_type,
                'account_type': account_type,
                'account_category': account_type,
                'account_subcategory': '',
                'parent_account_id': '',
                'account_level': 1,
                'is_leaf_account': False,
                'normal_balance': type_info['normal_balance'],
                'is_active': True,
                'consolidation_account': account_type,
                'created_date': '2024-01-01 00:00:00'
            })
            
            account_id += 1
            account_code += 100
            
            # Create category and subcategory accounts
            for category, subcategories in type_info['categories'].items():
                category_account_id = f"ACC_{account_id:06d}"
                accounts.append({
                    'account_id': category_account_id,
                    'account_code': str(account_code),
                    'account_name': category,
                    'account_type': account_type,
                    'account_category': category,
                    'account_subcategory': '',
                    'parent_account_id': parent_account_id,
                    'account_level': 2,
                    'is_leaf_account': False,
                    'normal_balance': type_info['normal_balance'],
                    'is_active': True,
                    'consolidation_account': account_type,
                    'created_date': '2024-01-01 00:00:00'
                })
                
                account_id += 1
                account_code += 10
                
                for subcategory, account_names in subcategories.items():
                    subcategory_account_id = f"ACC_{account_id:06d}"
                    accounts.append({
                        'account_id': subcategory_account_id,
                        'account_code': str(account_code),
                        'account_name': subcategory,
                        'account_type': account_type,
                        'account_category': category,
                        'account_subcategory': subcategory,
                        'parent_account_id': category_account_id,
                        'account_level': 3,
                        'is_leaf_account': False,
                        'normal_balance': type_info['normal_balance'],
                        'is_active': True,
                        'consolidation_account': account_type,
                        'created_date': '2024-01-01 00:00:00'
                    })
                    
                    account_id += 1
                    account_code += 1
                    
                    # Create leaf accounts
                    for account_name in account_names:
                        leaf_account_id = f"ACC_{account_id:06d}"
                        accounts.append({
                            'account_id': leaf_account_id,
                            'account_code': str(account_code),
                            'account_name': account_name,
                            'account_type': account_type,
                            'account_category': category,
                            'account_subcategory': subcategory,
                            'parent_account_id': subcategory_account_id,
                            'account_level': 4,
                            'is_leaf_account': True,
                            'normal_balance': type_info['normal_balance'],
                            'is_active': True,
                            'consolidation_account': account_type,
                            'created_date': '2024-01-01 00:00:00'
                        })
                        
                        account_id += 1
                        account_code += 1
        
        # Store for later reference
        self.accounts = {a['account_id']: a for a in accounts}
        
        print(f"Generated {len(accounts)} chart of accounts entries")
        return accounts
    
    def generate_currencies_and_rates(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate currencies and exchange rates."""
        print("💱 Generating currencies and exchange rates...")
        
        # Currencies
        currencies = [
            {'currency_code': 'EUR', 'currency_name': 'Euro', 'currency_symbol': '€', 'decimal_places': 2, 'is_active': True, 'created_date': '2024-01-01 00:00:00'},
            {'currency_code': 'USD', 'currency_name': 'US Dollar', 'currency_symbol': '$', 'decimal_places': 2, 'is_active': True, 'created_date': '2024-01-01 00:00:00'},
            {'currency_code': 'GBP', 'currency_name': 'British Pound', 'currency_symbol': '£', 'decimal_places': 2, 'is_active': True, 'created_date': '2024-01-01 00:00:00'},
            {'currency_code': 'CHF', 'currency_name': 'Swiss Franc', 'currency_symbol': 'CHF', 'decimal_places': 2, 'is_active': True, 'created_date': '2024-01-01 00:00:00'}
        ]
        
        # Exchange rates (daily for 2 years)
        exchange_rates = []
        base_rates = {
            ('EUR', 'USD'): 1.1000,
            ('EUR', 'GBP'): 0.8500,
            ('EUR', 'CHF'): 1.0800,
            ('USD', 'EUR'): 0.9091,
            ('GBP', 'EUR'): 1.1765,
            ('CHF', 'EUR'): 0.9259
        }
        
        start_date = date(self.base_year, 1, 1)
        end_date = date(self.base_year + self.num_years, 12, 31)
        current_date = start_date
        
        rate_id = 1
        
        while current_date <= end_date:
            for (from_curr, to_curr), base_rate in base_rates.items():
                # Add some realistic volatility (±2%)
                volatility = random.uniform(-0.02, 0.02)
                rate = base_rate * (1 + volatility)
                
                for rate_type in ['SPOT', 'CLOSING']:
                    exchange_rates.append({
                        'exchange_rate_id': f"EXR_{rate_id:08d}",  # Fixed: add missing exchange_rate_id
                        'effective_date': current_date.strftime('%Y-%m-%d'),
                        'base_currency': from_curr,  # Fixed: correct field name
                        'target_currency': to_curr,  # Fixed: correct field name
                        'exchange_rate': round(Decimal(str(rate)), 6),
                        'rate_type': rate_type,
                        'data_source': 'ECB',  # Fixed: correct field name
                        'created_date': '2024-01-01 00:00:00'
                    })
                    rate_id += 1
            
            current_date += timedelta(days=1)
        
        self.currencies = {c['currency_code']: c for c in currencies}
        
        print(f"Generated {len(currencies)} currencies and {len(exchange_rates):,} exchange rates")
        return currencies, exchange_rates
    
    def generate_reporting_periods(self) -> List[Dict]:
        """Generate reporting periods."""
        print("📅 Generating reporting periods...")
        
        periods = []
        
        for year in range(self.base_year, self.base_year + self.num_years + 1):
            for month in range(1, 13):
                period_id = f"{year}_{month:02d}"
                
                # Calculate period dates
                period_start = date(year, month, 1)
                if month == 12:
                    period_end = date(year, month, 31)
                else:
                    next_month = date(year, month + 1, 1) - timedelta(days=1)
                    period_end = next_month
                
                periods.append({
                    'period_id': period_id,
                    'period_year': year,
                    'period_month': month,
                    'period_name': f"{year}-{month:02d}",
                    'period_start_date': period_start.strftime('%Y-%m-%d'),
                    'period_end_date': period_end.strftime('%Y-%m-%d'),
                    'is_adjustment_period': False,
                    'period_status': 'CLOSED' if year < 2024 else 'OPEN',
                    'created_date': '2024-01-01 00:00:00'
                })
        
        # Add adjustment periods for year-end
        for year in range(self.base_year, self.base_year + self.num_years):
            periods.append({
                'period_id': f"{year}_ADJ",
                'period_year': year,
                'period_month': 13,
                'period_name': f"{year}-ADJ",
                'period_start_date': f"{year}-12-31",
                'period_end_date': f"{year}-12-31",
                'is_adjustment_period': True,
                'period_status': 'CLOSED',
                'created_date': '2024-01-01 00:00:00'
            })
        
        self.periods = {p['period_id']: p for p in periods}
        
        print(f"Generated {len(periods)} reporting periods")
        return periods
    
    def generate_cost_centers(self) -> List[Dict]:
        """Generate cost centers for each entity."""
        print("🏭 Generating cost centers...")
        
        cost_centers = []
        cost_center_types = {
            'SALES': ['Retail Stores', 'Online Sales', 'Wholesale'],
            'MARKETING': ['Digital Marketing', 'Traditional Advertising', 'Events'],
            'OPERATIONS': ['Warehousing', 'Logistics', 'Customer Service'],
            'ADMIN': ['Finance', 'HR', 'IT', 'Legal'],
            'MANAGEMENT': ['Executive', 'Strategy']
        }
        
        cc_id = 1
        
        for entity_id, entity in self.entities.items():
            entity_code = entity['entity_code']
            
            # Entity-level cost centers
            for cc_type, cc_names in cost_center_types.items():
                for cc_name in cc_names:
                    cost_centers.append({
                        'cost_center_id': f"CC_{cc_id:06d}",
                        'entity_id': entity_id,
                        'cost_center_code': f"{entity_code}_{cc_type}_{cc_id:03d}",
                        'cost_center_name': f"{cc_name} - {entity['country_code']}",
                        'cost_center_type': 'PROFIT' if cc_type == 'SALES' else 'COST',
                        'parent_cost_center_id': '',
                        'manager_name': f"Manager {cc_id}",
                        'is_active': True,
                        'created_date': '2024-01-01 00:00:00'
                    })
                    cc_id += 1
        
        self.cost_centers = {cc['cost_center_id']: cc for cc in cost_centers}
        
        print(f"Generated {len(cost_centers)} cost centers")
        return cost_centers
    
    def generate_gl_transactions(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate general ledger transactions."""
        print("📚 Generating GL transactions...")
        
        headers = []
        lines = []
        
        # Get revenue and expense accounts for realistic transactions
        revenue_accounts = [a for a in self.accounts.values() if a['account_type'] == 'REVENUE' and a['is_leaf_account']]
        expense_accounts = [a for a in self.accounts.values() if a['account_type'] == 'EXPENSES' and a['is_leaf_account']]
        asset_accounts = [a for a in self.accounts.values() if a['account_type'] == 'ASSETS' and a['is_leaf_account']]
        liability_accounts = [a for a in self.accounts.values() if a['account_type'] == 'LIABILITIES' and a['is_leaf_account']]
        
        journal_id = 1
        line_id = 1
        
        # Generate monthly transactions for each entity
        for entity_id, entity in self.entities.items():
            if entity['entity_type'] != 'BV':  # Skip holding company
                continue
                
            entity_currency = entity['functional_currency']
            
            for year in range(self.base_year, self.base_year + self.num_years):
                for month in range(1, 13):
                    period_id = f"{year}_{month:02d}"
                    
                    # Generate 50-100 journal entries per entity per month
                    num_journals = random.randint(50, 100)
                    
                    for _ in range(num_journals):
                        journal_date = date(year, month, random.randint(1, 28))
                        
                        # Journal header
                        current_journal_id = f"JE_{journal_id:08d}"
                        
                        # Random transaction types
                        transaction_types = [
                            ('SALES', 'Sales transaction'),
                            ('PURCHASE', 'Purchase transaction'),
                            ('PAYROLL', 'Payroll entry'),
                            ('DEPRECIATION', 'Depreciation entry'),
                            ('BANK', 'Bank transaction'),
                            ('ADJUSTMENT', 'Manual adjustment')
                        ]
                        
                        trans_type, description = random.choice(transaction_types)
                        
                        header = {
                            'journal_header_id': f"JH_{journal_id:08d}",  # Fixed: add missing journal_header_id
                            'journal_id': current_journal_id,
                            'entity_id': entity_id,
                            'period_id': period_id,  # Fixed: add missing period_id
                            'journal_number': f"{entity['entity_code']}-{year}-{journal_id:06d}",
                            'journal_date': journal_date.strftime('%Y-%m-%d'),
                            'posting_date': journal_date.strftime('%Y-%m-%d'),
                            'period_year': year,
                            'period_month': month,
                            'journal_type': 'STANDARD',
                            'journal_source': trans_type,
                            'description': description,
                            'reference_number': f"REF-{journal_id:06d}",  # Fixed: correct field name
                            'currency_code': entity_currency,  # Fixed: add missing currency_code
                            'total_debit': Decimal('0.00'),
                            'total_credit': Decimal('0.00'),
                            'functional_currency': entity_currency,
                            'journal_status': 'POSTED',
                            'created_by': 'SYSTEM',
                            'created_date': '2024-01-01 00:00:00',
                            'posted_by': 'SYSTEM',
                            'posted_date': '2024-01-01 00:00:00',
                            'approved_by': 'SYSTEM'  # Fixed: add missing approved_by
                        }
                        
                        # Generate journal lines (2-6 lines per journal)
                        num_lines = random.randint(2, 6)
                        journal_lines = []
                        total_debit = Decimal('0.00')
                        total_credit = Decimal('0.00')
                        
                        for line_num in range(1, num_lines + 1):
                            # Select accounts based on transaction type
                            if trans_type == 'SALES':
                                if line_num == 1:  # Debit cash/receivables
                                    account = random.choice([a for a in asset_accounts if 'cash' in a['account_name'].lower() or 'receivable' in a['account_name'].lower()])
                                    is_debit = True
                                else:  # Credit revenue
                                    account = random.choice(revenue_accounts)
                                    is_debit = False
                            elif trans_type == 'PURCHASE':
                                if line_num == 1:  # Debit expense/inventory
                                    account = random.choice(expense_accounts)
                                    is_debit = True
                                else:  # Credit cash/payables
                                    account = random.choice(liability_accounts)
                                    is_debit = False
                            else:
                                # Random account selection
                                account = random.choice(list(self.accounts.values()))
                                if account['is_leaf_account']:
                                    is_debit = random.choice([True, False])
                                else:
                                    continue
                            
                            # Generate realistic amounts
                            if trans_type == 'SALES':
                                amount = Decimal(str(random.uniform(50, 2000))).quantize(Decimal('0.01'))
                            elif trans_type == 'PURCHASE':
                                amount = Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01'))
                            elif trans_type == 'PAYROLL':
                                amount = Decimal(str(random.uniform(2000, 8000))).quantize(Decimal('0.01'))
                            else:
                                amount = Decimal(str(random.uniform(100, 3000))).quantize(Decimal('0.01'))
                            
                            debit_amount = amount if is_debit else Decimal('0.00')
                            credit_amount = amount if not is_debit else Decimal('0.00')
                            
                            # Get random cost center for this entity
                            entity_cost_centers = [cc for cc in self.cost_centers.values() if cc['entity_id'] == entity_id]
                            cost_center = random.choice(entity_cost_centers)['cost_center_code'] if entity_cost_centers else 'DEFAULT'
                            
                            journal_lines.append({
                                'journal_line_id': f"JL_{line_id:08d}",  # Fixed: add missing journal_line_id
                                'journal_header_id': f"JH_{journal_id:08d}",  # Fixed: add missing journal_header_id
                                'line_id': f"JL_{line_id:08d}",
                                'journal_id': current_journal_id,
                                'line_number': line_num,
                                'entity_id': entity_id,
                                'account_id': account['account_id'],
                                'cost_center_id': f"CC_{random.randint(1, 75):06d}",  # Fixed: add missing cost_center_id
                                'debit_amount': debit_amount,
                                'credit_amount': credit_amount,
                                'currency_code': entity_currency,  # Fixed: add missing currency_code
                                'functional_currency': entity_currency,
                                'transaction_currency': entity_currency,
                                'transaction_amount': amount,
                                'exchange_rate': Decimal('1.000000'),
                                'line_description': f"Line {line_num} - {description}",  # Fixed: correct field name
                                'reference_1': f"REF-{journal_id:06d}-{line_num}",  # Fixed: correct field name
                                'reference_2': '',  # Fixed: add missing reference_2
                                'cost_center': cost_center,
                                'project_id': '',
                                'customer_id': '',
                                'vendor_id': '',
                                'created_date': '2024-01-01 00:00:00'
                            })
                            
                            total_debit += debit_amount
                            total_credit += credit_amount
                            line_id += 1
                        
                        # Balance the journal entry if needed
                        if total_debit != total_credit:
                            balance_amount = abs(total_debit - total_credit)
                            if total_debit > total_credit:
                                # Add credit line
                                account = random.choice(liability_accounts)
                                journal_lines.append({
                                    'journal_line_id': f"JL_{line_id:08d}",  # Fixed: add missing journal_line_id
                                    'journal_header_id': f"JH_{journal_id:08d}",  # Fixed: add missing journal_header_id
                                    'line_id': f"JL_{line_id:08d}",
                                    'journal_id': current_journal_id,
                                    'line_number': len(journal_lines) + 1,
                                    'entity_id': entity_id,
                                    'account_id': account['account_id'],
                                    'cost_center_id': f"CC_{random.randint(1, 75):06d}",  # Fixed: add missing cost_center_id
                                    'debit_amount': Decimal('0.00'),
                                    'credit_amount': balance_amount,
                                    'currency_code': entity_currency,  # Fixed: add missing currency_code
                                    'functional_currency': entity_currency,
                                    'transaction_currency': entity_currency,
                                    'transaction_amount': balance_amount,
                                    'exchange_rate': Decimal('1.000000'),
                                    'line_description': f"Balancing entry",  # Fixed: correct field name
                                    'reference_1': f"REF-{journal_id:06d}-BAL",  # Fixed: correct field name
                                    'reference_2': '',  # Fixed: add missing reference_2
                                    'cost_center': cost_center,
                                    'project_id': '',
                                    'customer_id': '',
                                    'vendor_id': '',
                                    'created_date': '2024-01-01 00:00:00'
                                })
                                total_credit += balance_amount
                                line_id += 1
                            else:
                                # Add debit line
                                account = random.choice(asset_accounts)
                                journal_lines.append({
                                    'journal_line_id': f"JL_{line_id:08d}",  # Fixed: add missing journal_line_id
                                    'journal_header_id': f"JH_{journal_id:08d}",  # Fixed: add missing journal_header_id
                                    'line_id': f"JL_{line_id:08d}",
                                    'journal_id': current_journal_id,
                                    'line_number': len(journal_lines) + 1,
                                    'entity_id': entity_id,
                                    'account_id': account['account_id'],
                                    'cost_center_id': f"CC_{random.randint(1, 75):06d}",  # Fixed: add missing cost_center_id
                                    'debit_amount': balance_amount,
                                    'credit_amount': Decimal('0.00'),
                                    'currency_code': entity_currency,  # Fixed: add missing currency_code
                                    'functional_currency': entity_currency,
                                    'transaction_currency': entity_currency,
                                    'transaction_amount': balance_amount,
                                    'exchange_rate': Decimal('1.000000'),
                                    'line_description': f"Balancing entry",  # Fixed: correct field name
                                    'reference_1': f"REF-{journal_id:06d}-BAL",  # Fixed: correct field name
                                    'reference_2': '',  # Fixed: add missing reference_2
                                    'cost_center': cost_center,
                                    'project_id': '',
                                    'customer_id': '',
                                    'vendor_id': '',
                                    'created_date': '2024-01-01 00:00:00'
                                })
                                total_debit += balance_amount
                                line_id += 1
                        
                        # Update header totals
                        header['total_debit'] = total_debit
                        header['total_credit'] = total_credit
                        
                        headers.append(header)
                        lines.extend(journal_lines)
                        
                        journal_id += 1
        
        print(f"Generated {len(headers):,} journal headers and {len(lines):,} journal lines")
        return headers, lines
    
    def generate_budget_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate budget versions and data."""
        print("📊 Generating budget data...")
        
        budget_versions = []
        budget_data = []
        
        version_id = 1
        budget_id = 1
        
        # Generate budgets for each entity
        for entity_id, entity in self.entities.items():
            if entity['entity_type'] != 'BV':  # Skip holding company
                continue
            
            # Generate budgets for current year and next year
            for year in [2024, 2025]:
                # Original budget
                version = {
                    'budget_version_id': f"BV_{version_id:06d}",
                    'version_name': f"Original Budget {year}",
                    'fiscal_year': year,
                    'entity_id': entity_id,
                    'version_type': 'ORIGINAL',
                    'status': 'APPROVED',
                    'created_by': 'BUDGET_MANAGER',
                    'approved_by': 'CFO',
                    'approval_date': '2024-01-01',
                    'created_date': '2024-01-01 00:00:00'
                }
                budget_versions.append(version)
                
                # Generate budget amounts for each account and month
                revenue_accounts = [a for a in self.accounts.values() if a['account_type'] == 'REVENUE' and a['is_leaf_account']]
                expense_accounts = [a for a in self.accounts.values() if a['account_type'] == 'EXPENSES' and a['is_leaf_account']]
                
                entity_cost_centers = [cc for cc in self.cost_centers.values() if cc['entity_id'] == entity_id]
                
                for account in revenue_accounts + expense_accounts:
                    for month in range(1, 13):
                        for cost_center in entity_cost_centers[:3]:  # Limit to 3 cost centers per account
                            # Generate realistic budget amounts
                            if account['account_type'] == 'REVENUE':
                                base_amount = random.uniform(50000, 200000)
                                # Add seasonality (higher in Q4 for fashion retail)
                                if month in [10, 11, 12]:
                                    base_amount *= 1.5
                                elif month in [6, 7, 8]:
                                    base_amount *= 1.2
                            else:  # EXPENSES
                                base_amount = random.uniform(20000, 100000)
                            
                            budget_data.append({
                                'budget_line_id': f"BD_{budget_id:08d}",
                                'budget_version_id': version['budget_version_id'],
                                'entity_id': entity_id,
                                'account_id': account['account_id'],
                                'cost_center_id': cost_center['cost_center_id'],  # Fixed: add missing cost_center_id
                                'period_year': year,
                                'period_month': month,
                                'budget_amount': Decimal(str(base_amount)).quantize(Decimal('0.01')),
                                'currency_code': entity['functional_currency'],  # Fixed: add missing currency_code
                                'functional_currency': entity['functional_currency'],
                                'budget_type': 'OPERATING',  # Fixed: add missing budget_type
                                'scenario': 'BASE_CASE',  # Fixed: add missing scenario
                                'cost_center': cost_center['cost_center_code'],
                                'project_id': '',
                                'department_id': f"DEPT_{random.randint(1, 20):03d}",  # Fixed: add missing department_id
                                'comments': f"Budget for {account['account_name']}",
                                'created_by': 'BUDGET_MANAGER',  # Fixed: add missing created_by
                                'created_date': '2024-01-01 00:00:00'
                            })
                            budget_id += 1
                
                version_id += 1
        
        print(f"Generated {len(budget_versions)} budget versions and {len(budget_data):,} budget entries")
        return budget_versions, budget_data
    
    def generate_fixed_assets(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate fixed assets and depreciation schedules."""
        print("🏭 Generating fixed assets...")
        
        assets = []
        depreciation_schedule = []
        
        asset_categories = {
            'IT Equipment': {'useful_life': 3, 'min_cost': 500, 'max_cost': 5000},
            'Office Furniture': {'useful_life': 5, 'min_cost': 200, 'max_cost': 2000},
            'Store Equipment': {'useful_life': 7, 'min_cost': 1000, 'max_cost': 15000},
            'Vehicles': {'useful_life': 5, 'min_cost': 15000, 'max_cost': 50000},
            'Machinery': {'useful_life': 10, 'min_cost': 10000, 'max_cost': 100000}
        }
        
        asset_id = 1
        schedule_id = 1
        
        # Generate assets for each entity
        for entity_id, entity in self.entities.items():
            if entity['entity_type'] != 'BV':  # Skip holding company
                continue
            
            # Generate 20-50 assets per entity
            num_assets = random.randint(20, 50)
            
            for _ in range(num_assets):
                category = random.choice(list(asset_categories.keys()))
                category_info = asset_categories[category]
                
                # Random acquisition date in the past 5 years
                acquisition_date = date(
                    random.randint(2019, 2023),
                    random.randint(1, 12),
                    random.randint(1, 28)
                )
                
                acquisition_cost = Decimal(str(random.uniform(
                    category_info['min_cost'],
                    category_info['max_cost']
                ))).quantize(Decimal('0.01'))
                
                useful_life = category_info['useful_life']
                annual_depreciation = acquisition_cost / useful_life
                
                # Calculate accumulated depreciation
                months_owned = (date(2024, 1, 1) - acquisition_date).days // 30
                years_owned = months_owned / 12
                accumulated_depreciation = min(
                    annual_depreciation * Decimal(str(years_owned)),
                    acquisition_cost * Decimal('0.95')  # Max 95% depreciated
                ).quantize(Decimal('0.01'))
                
                net_book_value = acquisition_cost - accumulated_depreciation
                
                asset = {
                    'asset_id': f"FA_{entity['entity_code']}_{asset_id:06d}",  # Fixed: match schema pattern
                    'asset_code': f"{entity['entity_code']}-FA-{asset_id:06d}",  # Fixed: correct field name
                    'asset_name': f"{category} #{asset_id}",
                    'entity_id': entity_id,
                    'asset_category': category.upper().replace(' ', '_'),  # Fixed: standardize format
                    'cost_center_id': f"CC_{random.randint(1, 75):06d}",  # Fixed: add missing cost_center_id
                    'purchase_date': acquisition_date.strftime('%Y-%m-%d'),  # Fixed: correct field name
                    'purchase_cost': acquisition_cost,  # Fixed: correct field name
                    'currency_code': entity['functional_currency'],  # Fixed: add missing currency_code
                    'useful_life_years': useful_life,
                    'depreciation_method': 'STRAIGHT_LINE',
                    'salvage_value': acquisition_cost * Decimal('0.05'),  # 5% salvage
                    'accumulated_depreciation': accumulated_depreciation,
                    'book_value': net_book_value,  # Fixed: correct field name
                    'asset_location': f"{entity['country_code']} Office",
                    'serial_number': f"SN-{asset_id:08d}-{entity['entity_code']}",  # Fixed: add missing serial_number
                    'supplier_name': f"Supplier {random.randint(1, 20):02d}",  # Fixed: add missing supplier_name
                    'warranty_expiry': (acquisition_date + timedelta(days=365 * 2)).strftime('%Y-%m-%d'),  # Fixed: add missing warranty_expiry
                    'asset_status': 'ACTIVE' if net_book_value > 0 else 'RETIRED',  # Fixed: use correct status values
                    'disposal_date': None,  # Fixed: add missing disposal_date
                    'created_date': '2024-01-01 00:00:00'
                }
                assets.append(asset)
                
                # Generate depreciation schedule
                current_date = acquisition_date.replace(day=1)  # Start from first of month
                monthly_depreciation = annual_depreciation / 12
                running_accumulated = Decimal('0.00')
                
                while current_date < date(2026, 1, 1) and running_accumulated < acquisition_cost:
                    remaining_cost = acquisition_cost - running_accumulated
                    current_depreciation = min(monthly_depreciation, remaining_cost).quantize(Decimal('0.01'))
                    running_accumulated += current_depreciation
                    current_nbv = acquisition_cost - running_accumulated
                    
                    depreciation_schedule.append({
                        'depreciation_id': f"DEP_{current_date.year}_{schedule_id:06d}_{current_date.month:02d}",  # Fixed: correct field name and format
                        'asset_id': asset['asset_id'],
                        'period_id': f"P_{current_date.year}_{current_date.month:02d}",  # Fixed: add missing period_id
                        'depreciation_date': current_date.strftime('%Y-%m-%d'),  # Fixed: add missing depreciation_date
                        'depreciation_amount': current_depreciation,
                        'accumulated_depreciation': running_accumulated,
                        'book_value': current_nbv,  # Fixed: correct field name
                        'is_posted': current_date < date(2024, 1, 1),  # Fixed: correct field name
                        'journal_header_id': None,  # Fixed: add missing journal_header_id
                        'created_date': '2024-01-01 00:00:00'
                    })
                    schedule_id += 1
                    
                    # Move to next month
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                
                asset_id += 1
        
        print(f"Generated {len(assets)} fixed assets and {len(depreciation_schedule):,} depreciation entries")
        return assets, depreciation_schedule
    
    def write_csv_file(self, filename: str, data: List[Dict], fieldnames: List[str] = None):
        """Write data to CSV file with compression."""
        if not data:
            print(f"⚠️ No data to write for {filename}")
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        # Write uncompressed first
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        # Calculate original file size
        original_size = os.path.getsize(filepath)
        
        # Compress the file
        compressed_filepath = filepath + '.gz'
        import gzip
        
        with open(filepath, 'rb') as f_in:
            with gzip.open(compressed_filepath, 'wb', compresslevel=6) as f_out:
                f_out.write(f_in.read())
        
        # Calculate compressed file size
        compressed_size = os.path.getsize(compressed_filepath)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        # Remove uncompressed file to save space
        os.remove(filepath)
        
        # Format size display
        if compressed_size > 1024 * 1024:
            size_str = f"{compressed_size / (1024 * 1024):.1f} MB"
        elif compressed_size > 1024:
            size_str = f"{compressed_size / 1024:.1f} KB"
        else:
            size_str = f"{compressed_size} bytes"
        
        print(f"  📄 {filename}.gz ({len(data):,} records, {size_str}, {compression_ratio:.1f}% compression)")
        
        self.csv_files[filename + '.gz'] = {
            'records': len(data),
            'size': compressed_size,
            'path': compressed_filepath
        }
    
    def generate_all_finance_data(self):
        """Generate all finance system data."""
        print("\n🚀 Generating complete EuroStyle Finance system data...")
        
        # Load external data for referential integrity
        self.load_external_data()
        
        # 1. Corporate structure
        print("\n1. Corporate Structure")
        legal_entities = self.generate_legal_entities()
        self.write_csv_file('eurostyle_finance.legal_entities.csv', legal_entities)
        
        entity_relationships = self.generate_entity_relationships()
        self.write_csv_file('eurostyle_finance.entity_relationships.csv', entity_relationships)
        
        # 2. Chart of accounts
        print("\n2. Chart of Accounts")
        accounts = self.generate_chart_of_accounts()
        self.write_csv_file('eurostyle_finance.chart_of_accounts.csv', accounts)
        
        # Generate entity accounts mapping
        entity_accounts = []
        ea_id = 1
        for entity_id in self.entities.keys():
            for account_id in self.accounts.keys():
                entity_accounts.append({
                    'entity_account_id': f"EA_{ea_id:08d}",
                    'entity_id': entity_id,
                    'account_id': account_id,
                    'local_account_code': self.accounts[account_id]['account_code'],
                    'local_account_name': self.accounts[account_id]['account_name'],
                    'is_active': True,
                    'created_date': '2024-01-01 00:00:00'
                })
                ea_id += 1
        
        self.write_csv_file('eurostyle_finance.entity_accounts.csv', entity_accounts)
        
        # 3. Currencies and exchange rates
        print("\n3. Currencies and Exchange Rates")
        currencies, exchange_rates = self.generate_currencies_and_rates()
        self.write_csv_file('eurostyle_finance.currencies.csv', currencies)
        self.write_csv_file('eurostyle_finance.exchange_rates.csv', exchange_rates)
        
        # 4. Reporting periods
        print("\n4. Reporting Periods")
        periods = self.generate_reporting_periods()
        self.write_csv_file('eurostyle_finance.reporting_periods.csv', periods)
        
        # 5. Cost centers
        print("\n5. Cost Centers")
        cost_centers = self.generate_cost_centers()
        self.write_csv_file('eurostyle_finance.cost_centers.csv', cost_centers)
        
        # 6. General ledger transactions
        print("\n6. General Ledger Transactions")
        gl_headers, gl_lines = self.generate_gl_transactions()
        self.write_csv_file('eurostyle_finance.gl_journal_headers.csv', gl_headers)
        self.write_csv_file('eurostyle_finance.gl_journal_lines.csv', gl_lines)
        
        # 7. Budget data
        print("\n7. Budget Data")
        budget_versions, budget_data = self.generate_budget_data()
        self.write_csv_file('eurostyle_finance.budget_versions.csv', budget_versions)
        self.write_csv_file('eurostyle_finance.budget_data.csv', budget_data)
        
        # 8. Fixed assets
        print("\n8. Fixed Assets")
        fixed_assets, depreciation_schedule = self.generate_fixed_assets()
        self.write_csv_file('eurostyle_finance.fixed_assets.csv', fixed_assets)
        self.write_csv_file('eurostyle_finance.depreciation_schedule.csv', depreciation_schedule)
        
        # Summary
        print(f"\n✅ Complete finance data generation finished!")
        print(f"Generated files:")
        total_records = 0
        total_size = 0
        
        for filename, info in sorted(self.csv_files.items()):
            size_str = f"{info['size'] / (1024 * 1024):.1f} MB" if info['size'] > 1024 * 1024 else f"{info['size'] / 1024:.1f} KB"
            print(f"  📄 {filename} ({info['records']:,} records, {size_str})")
            total_records += info['records']
            total_size += info['size']
        
        total_size_str = f"{total_size / (1024 * 1024):.1f} MB" if total_size > 1024 * 1024 else f"{total_size / 1024:.1f} KB"
        print(f"\n📊 Total: {total_records:,} records, {total_size_str}")

def main():
    """Main function to generate EuroStyle Finance data."""
    print("🏦 EuroStyle Fashion - Finance Data Generator")
    print("============================================")
    
    try:
        generator = EuroStyleFinanceGenerator()
        generator.generate_all_finance_data()
        
        print("\n🎉 Finance data generation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during finance data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()