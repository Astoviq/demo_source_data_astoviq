#!/usr/bin/env python3
"""
EuroStyle HR-Finance Integration Generator
=========================================

Generates Finance GL entries for payroll costs based on HR employee data.
Creates monthly payroll journals with salaries, benefits, and department allocations.
"""

import csv
import gzip
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple
import logging

class HRFinanceIntegrator:
    """Integrates HR payroll data with Finance GL."""
    
    def __init__(self):
        """Initialize the HR-Finance integrator."""
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.hr_data_path = Path("../generated_data")
        self.finance_data_path = Path("../generated_data")
        
        # Data containers
        self.employees = {}
        self.departments = {}
        self.compensation_history = {}
        self.existing_gl_lines = []
        
        # HR cost structure (European fashion retail)
        self.cost_structure = {
            'employer_social_security': 0.25,    # 25% employer SS contributions
            'pension_contribution': 0.08,        # 8% pension contributions  
            'health_insurance': 0.04,            # 4% health insurance
            'vacation_accrual': 0.08,            # 8% vacation accrual
            'training_budget': 0.02,             # 2% training budget per employee
            'other_benefits': 0.03,              # 3% other benefits
        }
        
        # Time period for payroll generation
        self.payroll_start_date = date(2020, 1, 1)
        self.payroll_end_date = date(2025, 10, 31)
        
    def load_hr_data(self) -> bool:
        """Load HR data from compressed files."""
        self.logger.info("Loading HR data...")
        
        try:
            # Load employees
            employees_file = self.hr_data_path / "eurostyle_hr.employees.csv.gz"
            with gzip.open(employees_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.employees[row['employee_id']] = row
            
            self.logger.info(f"Loaded {len(self.employees)} employees")
            
            # Load departments
            departments_file = self.hr_data_path / "eurostyle_hr.departments.csv.gz"
            with gzip.open(departments_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.departments[row['department_id']] = row
            
            self.logger.info(f"Loaded {len(self.departments)} departments")
            
            # Load compensation history
            comp_file = self.hr_data_path / "eurostyle_hr.compensation_history.csv.gz"
            with gzip.open(comp_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    emp_id = row['employee_id']
                    if emp_id not in self.compensation_history:
                        self.compensation_history[emp_id] = []
                    self.compensation_history[emp_id].append(row)
            
            self.logger.info(f"Loaded compensation history for {len(self.compensation_history)} employees")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading HR data: {str(e)}")
            return False
    
    def load_existing_finance_data(self) -> bool:
        """Load existing finance GL data to append payroll entries."""
        self.logger.info("Loading existing Finance GL data...")
        
        try:
            gl_lines_file = self.finance_data_path / "eurostyle_finance.gl_journal_lines.csv"
            if gl_lines_file.exists():
                with open(gl_lines_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.existing_gl_lines = list(reader)
                
                self.logger.info(f"Loaded {len(self.existing_gl_lines)} existing GL lines")
            else:
                self.logger.warning("No existing GL lines found - will create new file")
                self.existing_gl_lines = []
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading existing finance data: {str(e)}")
            return False
    
    def get_employee_monthly_salary(self, employee_id: str, target_date: date) -> Decimal:
        """Get employee monthly salary for a specific date."""
        if employee_id not in self.compensation_history:
            # Default salary if no compensation history
            return Decimal('3500.00')  # €3,500 default monthly salary
        
        # Find the most recent compensation entry before or on the target date
        valid_entries = []
        for comp in self.compensation_history[employee_id]:
            effective_date = datetime.strptime(comp['effective_date'], '%Y-%m-%d').date()
            if effective_date <= target_date:
                valid_entries.append((effective_date, comp))
        
        if not valid_entries:
            return Decimal('3500.00')  # Default if no valid entries
        
        # Get the most recent entry
        valid_entries.sort(key=lambda x: x[0], reverse=True)
        latest_comp = valid_entries[0][1]
        
        # Use monthly base salary
        return Decimal(str(latest_comp.get('monthly_base_salary_eur', '3500.00')))
    
    def map_department_to_cost_center(self, department_name: str) -> str:
        """Map HR department to Finance cost center."""
        department_mapping = {
            'sales': 'SALES_001',
            'marketing': 'MARKETING_001', 
            'operations': 'OPERATIONS_001',
            'finance': 'ADMIN_001',
            'human resources': 'ADMIN_002',
            'it': 'ADMIN_003',
            'legal': 'ADMIN_004',
            'management': 'MANAGEMENT_001',
            'customer service': 'OPERATIONS_002',
            'logistics': 'OPERATIONS_003',
            'procurement': 'OPERATIONS_004',
        }
        
        dept_lower = department_name.lower()
        for key, cost_center in department_mapping.items():
            if key in dept_lower:
                return cost_center
        
        return 'ADMIN_999'  # Default cost center
    
    def generate_monthly_payroll_journals(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate monthly payroll journal entries."""
        self.logger.info("Generating monthly payroll journals...")
        
        headers = []
        lines = []
        
        # Get next journal ID (continue from existing)
        next_journal_id = len(self.existing_gl_lines) // 2 + 50000  # Start payroll journals at 50000
        next_line_id = len(self.existing_gl_lines) + 1
        
        # Generate payroll for each month in the period
        current_date = self.payroll_start_date
        while current_date <= self.payroll_end_date:
            # Generate payroll journal for this month
            month_headers, month_lines, next_journal_id, next_line_id = self._generate_monthly_payroll(
                current_date, next_journal_id, next_line_id
            )
            
            headers.extend(month_headers)
            lines.extend(month_lines)
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        self.logger.info(f"Generated {len(headers)} payroll journal headers")
        self.logger.info(f"Generated {len(lines)} payroll journal lines")
        
        return headers, lines
    
    def _generate_monthly_payroll(self, payroll_date: date, journal_id: int, line_id: int) -> Tuple[List[Dict], List[Dict], int, int]:
        """Generate payroll entries for a specific month."""
        headers = []
        lines = []
        
        # Group employees by entity for separate payroll journals
        employees_by_entity = {}
        for emp_id, employee in self.employees.items():
            entity_id = employee.get('entity_id', 'ENTITY_NL_BV')
            if entity_id not in employees_by_entity:
                employees_by_entity[entity_id] = []
            
            # Only include active employees
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            termination_date = None
            if employee.get('termination_date'):
                termination_date = datetime.strptime(employee['termination_date'], '%Y-%m-%d').date()
            
            # Check if employee was active during this payroll period
            if hire_date <= payroll_date and (termination_date is None or termination_date >= payroll_date):
                employees_by_entity[entity_id].append(employee)
        
        # Generate payroll journal for each entity
        for entity_id, entity_employees in employees_by_entity.items():
            if not entity_employees:
                continue
            
            # Calculate total payroll costs for this entity
            total_base_salary = Decimal('0.00')
            total_benefits = Decimal('0.00')
            employee_payroll_lines = []
            
            for employee in entity_employees:
                emp_id = employee['employee_id']
                monthly_salary = self.get_employee_monthly_salary(emp_id, payroll_date)
                
                # Calculate benefit costs
                social_security = monthly_salary * Decimal(str(self.cost_structure['employer_social_security']))
                pension = monthly_salary * Decimal(str(self.cost_structure['pension_contribution']))
                health_insurance = monthly_salary * Decimal(str(self.cost_structure['health_insurance']))
                vacation_accrual = monthly_salary * Decimal(str(self.cost_structure['vacation_accrual']))
                training_budget = monthly_salary * Decimal(str(self.cost_structure['training_budget']))
                other_benefits = monthly_salary * Decimal(str(self.cost_structure['other_benefits']))
                
                total_benefits_per_emp = social_security + pension + health_insurance + vacation_accrual + training_budget + other_benefits
                
                total_base_salary += monthly_salary
                total_benefits += total_benefits_per_emp
                
                # Get department for cost center mapping
                dept_name = 'general'  # Default
                if hasattr(employee, 'department_id') and employee.get('department_id'):
                    dept = self.departments.get(employee['department_id'], {})
                    dept_name = dept.get('department_name', 'general')
                
                cost_center = self.map_department_to_cost_center(dept_name)
                
                employee_payroll_lines.append({
                    'employee_id': emp_id,
                    'monthly_salary': monthly_salary,
                    'total_benefits': total_benefits_per_emp,
                    'cost_center': cost_center,
                    'department': dept_name
                })
            
            # Create payroll journal header
            current_journal_id = f"JE_{journal_id:08d}"
            # Set payroll journal date to last day of the month
            if payroll_date.month == 12:
                next_month = date(payroll_date.year + 1, 1, 1)
            else:
                next_month = date(payroll_date.year, payroll_date.month + 1, 1)
            
            payroll_journal_date = next_month - timedelta(days=1)
            
            header = {
                'journal_header_id': f"JH_{journal_id:08d}",
                'journal_id': current_journal_id,
                'entity_id': entity_id,
                'period_id': f"{payroll_date.year}_{payroll_date.month:02d}",
                'journal_number': f"PAYROLL-{payroll_date.year}-{payroll_date.month:02d}-{entity_id}",
                'journal_date': payroll_journal_date.strftime('%Y-%m-%d'),
                'posting_date': payroll_journal_date.strftime('%Y-%m-%d'),
                'period_year': payroll_date.year,
                'period_month': payroll_date.month,
                'journal_type': 'PAYROLL',
                'journal_source': 'HR_SYSTEM',
                'description': f'Monthly payroll for {payroll_date.strftime("%B %Y")}',
                'reference_number': f"PAYROLL-{payroll_date.year}{payroll_date.month:02d}",
                'currency_code': 'EUR',
                'total_debit': total_base_salary + total_benefits,
                'total_credit': total_base_salary + total_benefits,
                'functional_currency': 'EUR',
                'journal_status': 'POSTED',
                'created_by': 'HR_SYSTEM',
                'created_date': '2024-01-01 00:00:00',
                'posted_by': 'HR_SYSTEM',
                'posted_date': '2024-01-01 00:00:00',
                'approved_by': 'HR_SYSTEM'
            }
            headers.append(header)
            journal_id += 1
            
            # Create payroll journal lines
            # 1. Debit: Personnel Expenses (by cost center)
            cost_center_totals = {}
            for emp_payroll in employee_payroll_lines:
                cost_center = emp_payroll['cost_center']
                total_emp_cost = emp_payroll['monthly_salary'] + emp_payroll['total_benefits']
                
                if cost_center not in cost_center_totals:
                    cost_center_totals[cost_center] = Decimal('0.00')
                cost_center_totals[cost_center] += total_emp_cost
            
            # Create debit entries for each cost center
            line_number = 1
            for cost_center, total_amount in cost_center_totals.items():
                lines.append({
                    'journal_line_id': f"JL_{line_id:08d}",
                    'journal_header_id': f"JH_{journal_id-1:08d}",
                    'line_id': f"JL_{line_id:08d}",
                    'journal_id': current_journal_id,
                    'line_number': line_number,
                    'entity_id': entity_id,
                    'account_id': 'ACC_6200',  # Personnel Expenses
                    'cost_center_id': f"CC_{random.randint(1, 10):06d}",
                    'debit_amount': total_amount,
                    'credit_amount': Decimal('0.00'),
                    'currency_code': 'EUR',
                    'functional_currency': 'EUR',
                    'transaction_currency': 'EUR',
                    'transaction_amount': total_amount,
                    'exchange_rate': Decimal('1.000000'),
                    'line_description': f'Personnel expenses - {cost_center}',
                    'reference_1': f"PAYROLL-{payroll_date.year}{payroll_date.month:02d}",
                    'reference_2': cost_center,
                    'cost_center': cost_center,
                    'project_id': '',
                    'customer_id': '',
                    'vendor_id': '',
                    'created_date': '2024-01-01 00:00:00'
                })
                line_id += 1
                line_number += 1
            
            # 2. Credit: Accrued Payroll (liability)
            lines.append({
                'journal_line_id': f"JL_{line_id:08d}",
                'journal_header_id': f"JH_{journal_id-1:08d}",
                'line_id': f"JL_{line_id:08d}",
                'journal_id': current_journal_id,
                'line_number': line_number,
                'entity_id': entity_id,
                'account_id': 'ACC_2120',  # Accrued Expenses (payroll liability)
                'cost_center_id': f"CC_{random.randint(1, 10):06d}",
                'debit_amount': Decimal('0.00'),
                'credit_amount': total_base_salary + total_benefits,
                'currency_code': 'EUR',
                'functional_currency': 'EUR',
                'transaction_currency': 'EUR',
                'transaction_amount': total_base_salary + total_benefits,
                'exchange_rate': Decimal('1.000000'),
                'line_description': f'Accrued payroll liability for {payroll_date.strftime("%B %Y")}',
                'reference_1': f"PAYROLL-{payroll_date.year}{payroll_date.month:02d}",
                'reference_2': entity_id,
                'cost_center': 'ADMIN_001',
                'project_id': '',
                'customer_id': '',
                'vendor_id': '',
                'created_date': '2024-01-01 00:00:00'
            })
            line_id += 1
        
        return headers, lines, journal_id, line_id
    
    def save_integrated_finance_data(self, payroll_headers: List[Dict], payroll_lines: List[Dict]) -> bool:
        """Save the integrated finance data (existing + payroll)."""
        self.logger.info("Saving integrated finance data...")
        
        try:
            # Combine existing GL lines with new payroll lines
            all_gl_lines = self.existing_gl_lines + payroll_lines
            
            # Load existing GL headers
            existing_headers = []
            headers_file = self.finance_data_path / "eurostyle_finance.gl_journal_headers.csv"
            if headers_file.exists():
                with open(headers_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_headers = list(reader)
            
            all_headers = existing_headers + payroll_headers
            
            # Save combined GL headers
            if all_headers:
                with open(headers_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=all_headers[0].keys())
                    writer.writeheader()
                    writer.writerows(all_headers)
            
            # Save combined GL lines
            lines_file = self.finance_data_path / "eurostyle_finance.gl_journal_lines.csv"
            if all_gl_lines:
                with open(lines_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=all_gl_lines[0].keys())
                    writer.writeheader()
                    writer.writerows(all_gl_lines)
            
            # Calculate payroll summary
            total_payroll_expense = sum(
                Decimal(line['debit_amount']) for line in payroll_lines
                if line['account_id'] == 'ACC_6200'  # Personnel expenses
            )
            
            self.logger.info(f"✅ Saved integrated finance data:")
            self.logger.info(f"  - Total GL headers: {len(all_headers):,}")
            self.logger.info(f"  - Total GL lines: {len(all_gl_lines):,}")
            self.logger.info(f"  - Payroll GL entries: {len(payroll_lines):,}")
            self.logger.info(f"  - Total payroll expense: €{total_payroll_expense:,.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving integrated finance data: {str(e)}")
            return False

def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🤝 EuroStyle HR-Finance Integration Generator")
    logger.info("=" * 50)
    
    integrator = HRFinanceIntegrator()
    
    try:
        # Load HR and existing finance data
        if not integrator.load_hr_data():
            logger.error("❌ Failed to load HR data")
            return False
        
        if not integrator.load_existing_finance_data():
            logger.error("❌ Failed to load existing finance data") 
            return False
        
        # Generate payroll GL entries
        payroll_headers, payroll_lines = integrator.generate_monthly_payroll_journals()
        
        # Save integrated data
        if not integrator.save_integrated_finance_data(payroll_headers, payroll_lines):
            logger.error("❌ Failed to save integrated finance data")
            return False
        
        logger.info("")
        logger.info("🎉 HR-Finance integration completed successfully!")
        logger.info("✅ Payroll costs now integrated with Finance GL")
        logger.info("✅ Department cost center mapping implemented")  
        logger.info("✅ Monthly payroll journals generated for all entities")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ HR-Finance integration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)