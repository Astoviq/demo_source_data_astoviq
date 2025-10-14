#!/usr/bin/env python3
"""
POS-Finance Integration Generator
=================================

Creates Finance GL entries for POS employee commissions and performance bonuses.
Integrates commission payments with the Finance system.
"""

import csv
import gzip
import os
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal
import logging
from typing import Dict, List

class POSFinanceIntegrationGenerator:
    """Generates Finance GL entries for POS employee commissions."""
    
    def __init__(self):
        """Initialize the POS-Finance integration generator."""
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.pos_data_path = Path("../generated_data")
        self.finance_data_path = Path("../generated_data")
        
        # Data containers
        self.pos_transactions = []
        self.pos_performance = []
        self.existing_gl_headers = []
        
        # GL accounts for commissions
        self.gl_accounts = {
            'commission_expense': '6100',      # Sales Commission Expense
            'commission_payable': '2300',      # Commission Payable (liability)
            'bonus_expense': '6110',           # Sales Bonus Expense
            'bonus_payable': '2310',           # Bonus Payable (liability)
            'cash': '1000'                     # Cash account (when paid)
        }
        
    def load_pos_data(self) -> bool:
        """Load POS transaction and performance data."""
        self.logger.info("Loading POS system data...")
        
        try:
            # Load POS transactions
            transactions_file = self.pos_data_path / "eurostyle_pos.transactions.csv"
            if transactions_file.exists():
                with open(transactions_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.pos_transactions = list(reader)
                
                self.logger.info(f"Loaded {len(self.pos_transactions)} POS transactions")
            else:
                self.logger.error("POS transactions file not found")
                return False
            
            # Load POS performance data
            performance_file = self.pos_data_path / "eurostyle_pos.employee_performance.csv"
            if performance_file.exists():
                with open(performance_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.pos_performance = list(reader)
                
                self.logger.info(f"Loaded {len(self.pos_performance)} performance records")
            else:
                self.logger.error("POS performance file not found")
                return False
            
            # Load existing GL headers to get next ID
            gl_headers_file = self.finance_data_path / "eurostyle_finance.gl_journal_headers.csv.gz"
            if gl_headers_file.exists():
                with gzip.open(gl_headers_file, 'rt', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.existing_gl_headers = list(reader)
                
                self.logger.info(f"Loaded {len(self.existing_gl_headers)} existing GL headers")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading POS data: {str(e)}")
            return False
    
    def generate_commission_gl_entries(self) -> List[Dict]:
        """Generate GL entries for monthly commission payments."""
        self.logger.info("Generating commission GL entries...")
        
        gl_headers = []
        gl_lines = []
        
        # Get starting GL header ID
        max_existing_id = 0
        if self.existing_gl_headers:
            for header in self.existing_gl_headers:
                header_id = header.get('journal_header_id', '')
                if header_id.startswith('GL_HEADER_'):
                    try:
                        id_num = int(header_id.replace('GL_HEADER_', ''))
                        max_existing_id = max(max_existing_id, id_num)
                    except ValueError:
                        continue
        
        header_counter = max_existing_id + 1
        line_counter = 1
        
        # Group performance data by month for commission payments
        monthly_commissions = {}
        
        for perf in self.pos_performance:
            year_month = perf.get('performance_month', '')
            employee_id = perf.get('employee_id', '')
            commission_eur = float(perf.get('total_commission_eur', 0))
            
            if not year_month or not employee_id or commission_eur == 0:
                continue
            
            if year_month not in monthly_commissions:
                monthly_commissions[year_month] = {}
            
            monthly_commissions[year_month][employee_id] = commission_eur
        
        # Generate GL entries for each month
        for year_month, employee_commissions in monthly_commissions.items():
            if not employee_commissions:
                continue
            
            # Calculate total commissions for this month
            total_commission = sum(employee_commissions.values())
            
            if total_commission == 0:
                continue
            
            # Create journal header for commission accrual
            accrual_header_id = f"GL_HEADER_{header_counter:08d}"
            accrual_date = f"{year_month}-28"  # End of month accrual
            
            gl_headers.append({
                'journal_header_id': accrual_header_id,
                'journal_date': accrual_date,
                'journal_period': year_month,
                'journal_source': 'POS_COMMISSION',
                'journal_category': 'ACCRUAL',
                'reference_number': f"COM_ACCR_{year_month.replace('-', '_')}",
                'description': f"Sales Commission Accrual - {year_month}",
                'total_debits_eur': total_commission,
                'total_credits_eur': total_commission,
                'status': 'POSTED',
                'created_by': 'POS_SYSTEM',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'approved_by': 'AUTO_SYSTEM',
                'approved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Create GL lines for commission accrual
            # Debit: Commission Expense
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': accrual_header_id,
                'line_number': 1,
                'account_code': self.gl_accounts['commission_expense'],
                'account_description': 'Sales Commission Expense',
                'debit_amount_eur': total_commission,
                'credit_amount_eur': 0.0,
                'description': f"Commission expense for {len(employee_commissions)} employees - {year_month}",
                'reference_id': '',
                'reference_type': 'COMMISSION_ACCRUAL',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            
            # Credit: Commission Payable
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': accrual_header_id,
                'line_number': 2,
                'account_code': self.gl_accounts['commission_payable'],
                'account_description': 'Commission Payable',
                'debit_amount_eur': 0.0,
                'credit_amount_eur': total_commission,
                'description': f"Commission payable to {len(employee_commissions)} employees - {year_month}",
                'reference_id': '',
                'reference_type': 'COMMISSION_ACCRUAL',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            header_counter += 1
            
            # Create journal header for commission payment (next month)
            payment_year, payment_month = year_month.split('-')
            payment_month_num = int(payment_month) + 1
            if payment_month_num > 12:
                payment_month_num = 1
                payment_year = str(int(payment_year) + 1)
            
            payment_date = f"{payment_year}-{payment_month_num:02d}-15"  # Mid-month payment
            payment_header_id = f"GL_HEADER_{header_counter:08d}"
            
            gl_headers.append({
                'journal_header_id': payment_header_id,
                'journal_date': payment_date,
                'journal_period': f"{payment_year}-{payment_month_num:02d}",
                'journal_source': 'POS_COMMISSION',
                'journal_category': 'PAYMENT',
                'reference_number': f"COM_PAY_{year_month.replace('-', '_')}",
                'description': f"Sales Commission Payment - {year_month}",
                'total_debits_eur': total_commission,
                'total_credits_eur': total_commission,
                'status': 'POSTED',
                'created_by': 'POS_SYSTEM',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'approved_by': 'AUTO_SYSTEM',
                'approved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Create GL lines for commission payment
            # Debit: Commission Payable (clear the liability)
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': payment_header_id,
                'line_number': 1,
                'account_code': self.gl_accounts['commission_payable'],
                'account_description': 'Commission Payable',
                'debit_amount_eur': total_commission,
                'credit_amount_eur': 0.0,
                'description': f"Commission payment to {len(employee_commissions)} employees - {year_month}",
                'reference_id': '',
                'reference_type': 'COMMISSION_PAYMENT',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            
            # Credit: Cash (payment)
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': payment_header_id,
                'line_number': 2,
                'account_code': self.gl_accounts['cash'],
                'account_description': 'Cash',
                'debit_amount_eur': 0.0,
                'credit_amount_eur': total_commission,
                'description': f"Cash payment for commissions - {year_month}",
                'reference_id': '',
                'reference_type': 'COMMISSION_PAYMENT',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            header_counter += 1
        
        self.logger.info(f"Generated {len(gl_headers)} GL headers and {len(gl_lines)} GL lines for commissions")
        return gl_headers, gl_lines
    
    def generate_performance_bonus_entries(self) -> List[Dict]:
        """Generate GL entries for performance bonuses."""
        self.logger.info("Generating performance bonus GL entries...")
        
        gl_headers = []
        gl_lines = []
        
        # Performance bonuses for top performers (quarterly)
        quarterly_bonuses = {}
        
        for perf in self.pos_performance:
            year_month = perf.get('performance_month', '')
            employee_id = perf.get('employee_id', '')
            performance_rating = perf.get('performance_rating', '')
            total_sales = float(perf.get('total_sales_eur', 0))
            
            if not year_month or not employee_id:
                continue
            
            # Calculate quarter
            year, month = year_month.split('-')
            quarter = f"{year}-Q{((int(month) - 1) // 3) + 1}"
            
            # Bonus criteria: EXCELLENT performance with >€20k sales
            if performance_rating == 'EXCELLENT' and total_sales >= 20000:
                bonus_amount = min(total_sales * 0.01, 500)  # 1% of sales, max €500
                
                if quarter not in quarterly_bonuses:
                    quarterly_bonuses[quarter] = {}
                
                if employee_id not in quarterly_bonuses[quarter]:
                    quarterly_bonuses[quarter][employee_id] = 0
                
                quarterly_bonuses[quarter][employee_id] += bonus_amount
        
        # Generate GL entries for quarterly bonuses
        header_counter = 50000  # Start with high number to avoid conflicts
        line_counter = 100000
        
        for quarter, employee_bonuses in quarterly_bonuses.items():
            if not employee_bonuses:
                continue
            
            total_bonus = sum(employee_bonuses.values())
            
            if total_bonus == 0:
                continue
            
            # Determine bonus payment date (end of quarter)
            year, q = quarter.split('-Q')
            if q == '1':
                bonus_date = f"{year}-03-31"
            elif q == '2':
                bonus_date = f"{year}-06-30"
            elif q == '3':
                bonus_date = f"{year}-09-30"
            else:  # Q4
                bonus_date = f"{year}-12-31"
            
            # Create journal header
            header_id = f"GL_HEADER_{header_counter:08d}"
            
            gl_headers.append({
                'journal_header_id': header_id,
                'journal_date': bonus_date,
                'journal_period': bonus_date[:7],
                'journal_source': 'POS_BONUS',
                'journal_category': 'BONUS',
                'reference_number': f"BONUS_{quarter.replace('-', '_')}",
                'description': f"Performance Bonus Payment - {quarter}",
                'total_debits_eur': total_bonus,
                'total_credits_eur': total_bonus,
                'status': 'POSTED',
                'created_by': 'POS_SYSTEM',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'approved_by': 'AUTO_SYSTEM',
                'approved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Create GL lines
            # Debit: Bonus Expense
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': header_id,
                'line_number': 1,
                'account_code': self.gl_accounts['bonus_expense'],
                'account_description': 'Sales Bonus Expense',
                'debit_amount_eur': total_bonus,
                'credit_amount_eur': 0.0,
                'description': f"Performance bonus for {len(employee_bonuses)} top performers - {quarter}",
                'reference_id': '',
                'reference_type': 'PERFORMANCE_BONUS',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            
            # Credit: Cash
            gl_lines.append({
                'journal_line_id': f"GL_LINE_{line_counter:08d}",
                'journal_header_id': header_id,
                'line_number': 2,
                'account_code': self.gl_accounts['cash'],
                'account_description': 'Cash',
                'debit_amount_eur': 0.0,
                'credit_amount_eur': total_bonus,
                'description': f"Cash payment for performance bonuses - {quarter}",
                'reference_id': '',
                'reference_type': 'PERFORMANCE_BONUS',
                'entity_id': 'ENTITY_NL_BV',
                'cost_center': 'SALES',
                'project_code': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            line_counter += 1
            header_counter += 1
        
        self.logger.info(f"Generated {len(gl_headers)} GL headers and {len(gl_lines)} GL lines for bonuses")
        return gl_headers, gl_lines
    
    def append_to_finance_data(self, commission_headers: List[Dict], commission_lines: List[Dict], 
                              bonus_headers: List[Dict], bonus_lines: List[Dict]) -> bool:
        """Append new GL entries to existing finance data files."""
        self.logger.info("Appending POS commission/bonus entries to finance data...")
        
        try:
            all_headers = commission_headers + bonus_headers
            all_lines = commission_lines + bonus_lines
            
            if not all_headers and not all_lines:
                self.logger.info("No data to append")
                return True
            
            # Append to GL headers
            gl_headers_file = self.finance_data_path / "eurostyle_finance.gl_journal_headers.csv.gz"
            
            # Read existing data carefully, handle field mismatches
            existing_headers = []
            existing_fieldnames = None
            
            if gl_headers_file.exists():
                try:
                    with gzip.open(gl_headers_file, 'rt', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        existing_fieldnames = reader.fieldnames
                        existing_headers = list(reader)
                except Exception as e:
                    self.logger.warning(f"Could not read existing GL headers: {e}")
                    existing_headers = []
            
            # Write combined data, prioritizing new structure
            if all_headers:
                new_fieldnames = list(all_headers[0].keys())
                
                # Filter existing headers to match new structure (in case of field mismatches)
                filtered_existing = []
                if existing_headers and existing_fieldnames:
                    for row in existing_headers:
                        filtered_row = {}
                        for field in new_fieldnames:
                            filtered_row[field] = row.get(field, '')  # Use empty string as default
                        filtered_existing.append(filtered_row)
                
                with gzip.open(gl_headers_file, 'wt', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=new_fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_existing)
                    writer.writerows(all_headers)
            
            # Similar approach for GL lines
            gl_lines_file = self.finance_data_path / "eurostyle_finance.gl_journal_lines.csv.gz"
            
            existing_lines = []
            existing_line_fieldnames = None
            
            if gl_lines_file.exists():
                try:
                    with gzip.open(gl_lines_file, 'rt', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        existing_line_fieldnames = reader.fieldnames
                        existing_lines = list(reader)
                except Exception as e:
                    self.logger.warning(f"Could not read existing GL lines: {e}")
                    existing_lines = []
            
            # Write combined line data
            if all_lines:
                new_line_fieldnames = list(all_lines[0].keys())
                
                # Filter existing lines to match new structure
                filtered_existing_lines = []
                if existing_lines and existing_line_fieldnames:
                    for row in existing_lines:
                        filtered_row = {}
                        for field in new_line_fieldnames:
                            filtered_row[field] = row.get(field, '')
                        filtered_existing_lines.append(filtered_row)
                
                with gzip.open(gl_lines_file, 'wt', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=new_line_fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_existing_lines)
                    writer.writerows(all_lines)
            
            # Calculate totals
            total_commission = sum(float(h.get('total_debits_eur', 0)) for h in commission_headers)
            total_bonus = sum(float(h.get('total_debits_eur', 0)) for h in bonus_headers)
            
            self.logger.info("✅ POS-Finance integration completed successfully:")
            self.logger.info(f"  - Commission GL entries: {len(commission_headers)} headers, {len(commission_lines)} lines")
            self.logger.info(f"  - Bonus GL entries: {len(bonus_headers)} headers, {len(bonus_lines)} lines")
            self.logger.info(f"  - Total commission expense: €{total_commission:,.2f}")
            self.logger.info(f"  - Total bonus expense: €{total_bonus:,.2f}")
            self.logger.info(f"  - Existing headers preserved: {len(existing_headers)}")
            self.logger.info(f"  - Existing lines preserved: {len(existing_lines)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error appending to finance data: {str(e)}")
            return False

def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("💰 POS-Finance Integration Generator")
    logger.info("=" * 40)
    
    generator = POSFinanceIntegrationGenerator()
    
    try:
        # Load POS data
        if not generator.load_pos_data():
            logger.error("❌ Failed to load POS data")
            return False
        
        # Generate commission GL entries
        commission_headers, commission_lines = generator.generate_commission_gl_entries()
        
        # Generate performance bonus entries
        bonus_headers, bonus_lines = generator.generate_performance_bonus_entries()
        
        # Append to finance data
        if not generator.append_to_finance_data(commission_headers, commission_lines, 
                                               bonus_headers, bonus_lines):
            logger.error("❌ Failed to append to finance data")
            return False
        
        logger.info("")
        logger.info("🎉 POS-Finance integration completed successfully!")
        logger.info("✅ Commission accruals and payments recorded in GL")
        logger.info("✅ Performance bonuses calculated and recorded")
        logger.info("✅ Complete audit trail from sales to finance")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ POS-Finance integration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)