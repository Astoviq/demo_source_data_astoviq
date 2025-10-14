#!/usr/bin/env python3
"""
EuroStyle POS System Generator
=============================

Creates a Point of Sale system that links sales employees to in-store orders.
Includes commission tracking, shift management, and employee performance metrics.
"""

import csv
import gzip
import random
from datetime import datetime, date, timedelta, time
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

class POSSystemGenerator:
    """Generates POS system data linking employees to sales transactions."""
    
    def __init__(self):
        """Initialize the POS system generator."""
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.hr_data_path = Path("../generated_data")
        self.operational_data_path = Path("../data-generator/generated_data")
        self.output_path = Path("../generated_data")
        
        # Data containers
        self.employees = {}
        self.departments = {}
        self.stores = {}
        self.orders = {}
        self.customers = {}
        
        # Sales employees (will be populated)
        self.sales_employees = {}
        
        # Commission structure
        self.commission_structure = {
            'base_commission_rate': 0.03,     # 3% base commission
            'tier1_threshold': 10000,         # €10k monthly sales
            'tier1_rate': 0.035,              # 3.5% for tier 1
            'tier2_threshold': 20000,         # €20k monthly sales  
            'tier2_rate': 0.04,               # 4% for tier 2
            'team_bonus_threshold': 50000,    # €50k team monthly sales
            'team_bonus_rate': 0.005,         # 0.5% additional team bonus
        }
        
    def load_data(self) -> bool:
        """Load all required data."""
        self.logger.info("Loading data for POS system generation...")
        
        try:
            # Load HR employees
            employees_file = self.hr_data_path / "eurostyle_hr.employees.csv.gz"
            with gzip.open(employees_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.employees[row['employee_id']] = row
            
            self.logger.info(f"Loaded {len(self.employees)} employees")
            
            # Load HR departments
            departments_file = self.hr_data_path / "eurostyle_hr.departments.csv.gz"
            with gzip.open(departments_file, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.departments[row['department_id']] = row
            
            self.logger.info(f"Loaded {len(self.departments)} departments")
            
            # Load operational stores
            stores_file = self.operational_data_path / "stores.csv"
            with open(stores_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.stores[row['store_id']] = row
            
            self.logger.info(f"Loaded {len(self.stores)} stores")
            
            # Load operational orders (only in-store orders)
            orders_file = self.operational_data_path / "orders.csv"
            in_store_orders = {}
            with open(orders_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['order_channel'] == 'in_store' and row['store_id']:
                        order_id = row['order_id']
                        if order_id not in in_store_orders:  # Take first occurrence (header)
                            in_store_orders[order_id] = row
            
            self.orders = in_store_orders
            self.logger.info(f"Loaded {len(self.orders)} in-store orders")
            
            # Load operational customers
            customers_file = self.operational_data_path / "customers.csv"
            with open(customers_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.customers[row['customer_id']] = row
            
            self.logger.info(f"Loaded {len(self.customers)} customers")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def identify_sales_employees(self) -> bool:
        """Identify employees who work in sales departments."""
        self.logger.info("Identifying sales employees...")
        
        # Find sales departments
        sales_departments = []
        for dept_id, dept in self.departments.items():
            dept_name = dept.get('department_name', '').lower()
            if any(keyword in dept_name for keyword in ['sales', 'retail', 'store', 'customer']):
                sales_departments.append(dept_id)
        
        self.logger.info(f"Found {len(sales_departments)} sales departments")
        
        # Since employees don't have department assignments, we'll assign them
        # Get all active employees
        active_employees = []
        for emp_id, employee in self.employees.items():
            if employee.get('employee_status', '').upper() == 'ACTIVE':
                active_employees.append((emp_id, employee))
        
        self.logger.info(f"Found {len(active_employees)} active employees")
        
        # Take approximately 15% as sales employees (realistic for retail)
        import random
        num_sales_employees = max(50, int(len(active_employees) * 0.15))
        selected_employees = random.sample(active_employees, min(num_sales_employees, len(active_employees)))
        
        # Assign sales employees to sales departments
        for i, (emp_id, employee) in enumerate(selected_employees):
            # Rotate through sales departments
            selected_dept = sales_departments[i % len(sales_departments)] if sales_departments else 'DEPT_000012'
            
            self.sales_employees[emp_id] = {
                **employee,
                'assigned_department_id': selected_dept,
                'department_name': self.departments.get(selected_dept, {}).get('department_name', 'Retail'),
                'country': employee.get('entity_id', 'ENTITY_NL_BV').split('_')[1]  # Extract country from entity
            }
        
        self.logger.info(f"Identified {len(self.sales_employees)} sales employees")
        return len(self.sales_employees) > 0
    
    def assign_employees_to_stores(self) -> Dict[str, List[str]]:
        """Assign sales employees to stores based on geography."""
        self.logger.info("Assigning employees to stores...")
        
        store_assignments = {}
        
        # Group stores by country
        stores_by_country = {}
        for store_id, store in self.stores.items():
            country = store.get('country_code', 'NL')
            if country not in stores_by_country:
                stores_by_country[country] = []
            stores_by_country[country].append(store_id)
        
        # Group employees by country  
        employees_by_country = {}
        for emp_id, employee in self.sales_employees.items():
            country = employee['country']
            if country not in employees_by_country:
                employees_by_country[country] = []
            employees_by_country[country].append(emp_id)
        
        # Assign employees to stores within their country
        # First, use all available employees across all countries for distribution
        all_sales_employees = list(self.sales_employees.keys())
        
        for country, country_stores in stores_by_country.items():
            country_employees = employees_by_country.get(country, [])
            
            # If not enough employees in this country, supplement with employees from other countries
            if len(country_employees) < len(country_stores) * 2:  # Need at least 2 per store
                # Add employees from other countries, prioritizing nearby regions
                fallback_countries = ['NL', 'DE', 'BE', 'FR', 'LU']  # Priority order
                for fallback_country in fallback_countries:
                    if fallback_country != country and len(country_employees) < len(country_stores) * 3:
                        fallback_employees = employees_by_country.get(fallback_country, [])
                        # Add some employees from this fallback country
                        additional = min(len(fallback_employees) // 2, len(country_stores) * 2 - len(country_employees))
                        country_employees.extend(fallback_employees[:additional])
            
            # Distribute employees across stores in this country
            employees_pool = country_employees.copy()  # Create a pool to draw from
            
            for i, store_id in enumerate(country_stores):
                store_assignments[store_id] = []
                
                if not employees_pool:
                    # Refill pool if exhausted
                    employees_pool = country_employees.copy()
                
                # Assign employees to this store
                if len(employees_pool) == 0:
                    continue
                elif len(employees_pool) == 1:
                    assigned_employees = employees_pool[:1]
                    employees_pool = []  # Empty the pool
                else:
                    # Determine number of employees for this store (2-6 typically)
                    max_for_store = min(6, len(employees_pool))
                    if max_for_store >= 2:
                        num_employees = random.randint(2, max_for_store)
                    else:
                        num_employees = max_for_store
                    
                    # Assign employees (with replacement allowed across stores)
                    assigned_employees = random.sample(employees_pool, min(num_employees, len(employees_pool)))
                
                store_assignments[store_id] = assigned_employees
        
        # Log assignments
        total_assignments = sum(len(emps) for emps in store_assignments.values())
        self.logger.info(f"Created {total_assignments} store-employee assignments across {len(store_assignments)} stores")
        
        return store_assignments
    
    def generate_pos_shifts(self, store_assignments: Dict[str, List[str]]) -> List[Dict]:
        """Generate employee shift schedules."""
        self.logger.info("Generating POS shifts...")
        
        shifts = []
        shift_counter = 1
        
        # Generate shifts for each store
        for store_id, employee_ids in store_assignments.items():
            if not employee_ids:
                continue
                
            store = self.stores[store_id]
            store_country = store.get('country_code', 'NL')
            
            # Generate shifts from 2020-01-01 to 2025-10-10
            current_date = date(2020, 1, 1)
            end_date = date(2025, 10, 10)
            
            while current_date <= end_date:
                # Skip Sundays (most European stores closed on Sundays)
                if current_date.weekday() == 6:  # Sunday
                    current_date += timedelta(days=1)
                    continue
                
                # Determine number of shifts for this day
                # Weekdays: 2-3 shifts, Saturdays: 3-4 shifts
                if current_date.weekday() == 5:  # Saturday
                    num_shifts = random.randint(3, 4)
                else:  # Weekday
                    num_shifts = random.randint(2, 3)
                
                # Generate shifts for this day
                shift_times = [
                    (time(9, 0), time(14, 0)),   # Morning shift
                    (time(14, 0), time(19, 0)),  # Afternoon shift  
                    (time(19, 0), time(22, 0)),  # Evening shift
                    (time(10, 0), time(18, 0)),  # Full day shift
                ]
                
                for shift_num in range(min(num_shifts, len(shift_times))):
                    start_time, end_time = shift_times[shift_num]
                    
                    # Assign employee to this shift
                    assigned_employee = random.choice(employee_ids)
                    
                    # Calculate shift hours
                    shift_start = datetime.combine(current_date, start_time)
                    shift_end = datetime.combine(current_date, end_time)
                    shift_hours = (shift_end - shift_start).seconds / 3600
                    
                    # Generate sales targets (varies by shift and day)
                    if current_date.weekday() == 5:  # Saturday
                        daily_target = random.uniform(2000, 5000)
                    else:  # Weekday
                        daily_target = random.uniform(1000, 3000)
                    
                    shift_target = daily_target / num_shifts
                    
                    shifts.append({
                        'shift_id': f"SHIFT_{shift_counter:08d}",
                        'store_id': store_id,
                        'employee_id': assigned_employee,
                        'shift_date': current_date.strftime('%Y-%m-%d'),
                        'shift_start': shift_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'shift_end': shift_end.strftime('%Y-%m-%d %H:%M:%S'),
                        'shift_hours': shift_hours,
                        'sales_target_eur': round(shift_target, 2),
                        'actual_sales_eur': 0.0,  # Will be updated when linking to orders
                        'commission_earned_eur': 0.0,  # Will be calculated
                        'customers_served': 0,  # Will be updated
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    shift_counter += 1
                
                current_date += timedelta(days=1)
        
        self.logger.info(f"Generated {len(shifts)} POS shifts")
        return shifts
    
    def generate_pos_transactions(self, store_assignments: Dict[str, List[str]], shifts: List[Dict]) -> List[Dict]:
        """Generate POS transactions linking orders to employees."""
        self.logger.info("Generating POS transactions...")
        
        transactions = []
        
        # Create a lookup for shifts by store and date
        shifts_lookup = {}
        for shift in shifts:
            store_id = shift['store_id']
            shift_date = shift['shift_date']
            if store_id not in shifts_lookup:
                shifts_lookup[store_id] = {}
            if shift_date not in shifts_lookup[store_id]:
                shifts_lookup[store_id][shift_date] = []
            shifts_lookup[store_id][shift_date].append(shift)
        
        transaction_counter = 1
        
        # Link each in-store order to a sales employee
        for order_id, order in self.orders.items():
            store_id = order.get('store_id')
            order_date = order.get('order_date')
            order_amount = float(order.get('total_amount_eur', 0))
            
            if not store_id or not order_date:
                continue
            
            # Find shifts for this store and date
            store_shifts = shifts_lookup.get(store_id, {}).get(order_date, [])
            
            if not store_shifts:
                # No shifts found, assign to random employee in this store
                store_employees = store_assignments.get(store_id, [])
                if store_employees:
                    assigned_employee = random.choice(store_employees)
                else:
                    continue
            else:
                # Pick a random shift for this day
                selected_shift = random.choice(store_shifts)
                assigned_employee = selected_shift['employee_id']
            
            # Calculate commission
            base_commission = Decimal(str(order_amount)) * Decimal(str(self.commission_structure['base_commission_rate']))
            
            # Get customer info
            customer = self.customers.get(order.get('customer_id', ''), {})
            
            transactions.append({
                'transaction_id': f"POS_TXN_{transaction_counter:08d}",
                'order_id': order_id,
                'store_id': store_id,
                'employee_id': assigned_employee,
                'customer_id': order.get('customer_id', ''),
                'transaction_date': order_date,
                'transaction_time': order.get('order_datetime', f"{order_date} 12:00:00"),
                'sale_amount_eur': order_amount,
                'commission_rate': self.commission_structure['base_commission_rate'],
                'commission_amount_eur': float(base_commission),
                'payment_method': order.get('payment_method', 'card'),
                'customer_satisfaction_score': random.randint(7, 10),  # 7-10 satisfaction score
                'transaction_notes': '',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            transaction_counter += 1
        
        self.logger.info(f"Generated {len(transactions)} POS transactions")
        return transactions
    
    def calculate_employee_performance(self, transactions: List[Dict], shifts: List[Dict]) -> List[Dict]:
        """Calculate employee performance metrics."""
        self.logger.info("Calculating employee performance metrics...")
        
        performance_data = []
        
        # Group transactions by employee and month
        employee_monthly_data = {}
        
        for txn in transactions:
            emp_id = txn['employee_id']
            txn_date = datetime.strptime(txn['transaction_date'], '%Y-%m-%d')
            year_month = f"{txn_date.year}-{txn_date.month:02d}"
            
            key = f"{emp_id}_{year_month}"
            
            if key not in employee_monthly_data:
                employee_monthly_data[key] = {
                    'employee_id': emp_id,
                    'year_month': year_month,
                    'total_sales': 0,
                    'total_transactions': 0,
                    'total_commission': 0,
                    'avg_satisfaction': 0,
                    'satisfaction_scores': []
                }
            
            employee_monthly_data[key]['total_sales'] += txn['sale_amount_eur']
            employee_monthly_data[key]['total_transactions'] += 1
            employee_monthly_data[key]['total_commission'] += txn['commission_amount_eur']
            employee_monthly_data[key]['satisfaction_scores'].append(txn['customer_satisfaction_score'])
        
        # Generate performance records
        perf_counter = 1
        for key, data in employee_monthly_data.items():
            # Calculate average satisfaction
            if data['satisfaction_scores']:
                avg_satisfaction = sum(data['satisfaction_scores']) / len(data['satisfaction_scores'])
            else:
                avg_satisfaction = 0
            
            # Determine performance rating
            monthly_sales = data['total_sales']
            if monthly_sales >= 20000:
                performance_rating = 'EXCELLENT'
            elif monthly_sales >= 15000:
                performance_rating = 'GOOD'
            elif monthly_sales >= 10000:
                performance_rating = 'AVERAGE'
            else:
                performance_rating = 'NEEDS_IMPROVEMENT'
            
            performance_data.append({
                'performance_id': f"PERF_{perf_counter:08d}",
                'employee_id': data['employee_id'],
                'performance_month': data['year_month'],
                'total_sales_eur': data['total_sales'],
                'total_transactions': data['total_transactions'],
                'avg_transaction_value_eur': data['total_sales'] / data['total_transactions'] if data['total_transactions'] > 0 else 0,
                'total_commission_eur': data['total_commission'],
                'customer_satisfaction_avg': round(avg_satisfaction, 2),
                'performance_rating': performance_rating,
                'sales_target_eur': random.uniform(12000, 25000),  # Monthly target
                'target_achievement_pct': (data['total_sales'] / random.uniform(12000, 25000)) * 100,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            perf_counter += 1
        
        self.logger.info(f"Generated {len(performance_data)} performance records")
        return performance_data
    
    def save_pos_data(self, shifts: List[Dict], transactions: List[Dict], performance: List[Dict]) -> bool:
        """Save all POS system data."""
        self.logger.info("Saving POS system data...")
        
        try:
            # Save shifts (compressed)
            shifts_file = self.output_path / "eurostyle_pos.shifts.csv.gz"
            if shifts:
                with gzip.open(shifts_file, 'wt', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=shifts[0].keys())
                    writer.writeheader()
                    writer.writerows(shifts)
            
            # Save transactions (compressed)
            transactions_file = self.output_path / "eurostyle_pos.transactions.csv.gz"
            if transactions:
                with gzip.open(transactions_file, 'wt', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
                    writer.writeheader()
                    writer.writerows(transactions)
            
            # Save performance (compressed)
            performance_file = self.output_path / "eurostyle_pos.employee_performance.csv.gz"
            if performance:
                with gzip.open(performance_file, 'wt', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=performance[0].keys())
                    writer.writeheader()
                    writer.writerows(performance)
            
            # Calculate summary metrics
            total_sales = sum(txn['sale_amount_eur'] for txn in transactions)
            total_commission = sum(txn['commission_amount_eur'] for txn in transactions)
            avg_satisfaction = sum(txn['customer_satisfaction_score'] for txn in transactions) / len(transactions) if transactions else 0
            
            self.logger.info("✅ POS system data saved successfully:")
            self.logger.info(f"  - Shifts: {len(shifts):,}")
            self.logger.info(f"  - Transactions: {len(transactions):,}")
            self.logger.info(f"  - Performance records: {len(performance):,}")
            self.logger.info(f"  - Total sales: €{total_sales:,.2f}")
            self.logger.info(f"  - Total commission: €{total_commission:,.2f}")
            self.logger.info(f"  - Avg satisfaction: {avg_satisfaction:.1f}/10")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving POS data: {str(e)}")
            return False

def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🛍️ EuroStyle POS System Generator")
    logger.info("=" * 40)
    
    generator = POSSystemGenerator()
    
    try:
        # Load all required data
        if not generator.load_data():
            logger.error("❌ Failed to load required data")
            return False
        
        # Identify sales employees
        if not generator.identify_sales_employees():
            logger.error("❌ No sales employees found")
            return False
        
        # Assign employees to stores
        store_assignments = generator.assign_employees_to_stores()
        
        # Generate POS data
        shifts = generator.generate_pos_shifts(store_assignments)
        transactions = generator.generate_pos_transactions(store_assignments, shifts)
        performance = generator.calculate_employee_performance(transactions, shifts)
        
        # Save POS data
        if not generator.save_pos_data(shifts, transactions, performance):
            logger.error("❌ Failed to save POS data")
            return False
        
        logger.info("")
        logger.info("🎉 POS system generation completed successfully!")
        logger.info("✅ Sales employees linked to in-store transactions")
        logger.info("✅ Employee shift schedules generated")
        logger.info("✅ Commission tracking implemented")
        logger.info("✅ Performance metrics calculated")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ POS system generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)