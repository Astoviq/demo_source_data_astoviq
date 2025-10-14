#!/usr/bin/env python3

"""
EuroStyle Fashion - HR Data Generator
====================================
Generates comprehensive HR data for a European fashion retail company
with multi-country employment law compliance and advanced HR features.

Features:
- Multi-country employee data (Netherlands, Germany, France, Italy, Spain)
- European employment law compliance
- Sick leave tracking with statutory requirements
- Performance management system
- Training and development records
- Compensation and benefits management
- Time and attendance tracking
- Recruitment and onboarding processes

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
import gzip
from typing import Dict, List, Tuple, Optional
import json
from faker import Faker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EuroStyleHRGenerator:
    """Generates comprehensive HR data for EuroStyle Fashion multi-country structure."""
    
    def __init__(self):
        """Initialize the HR data generator."""
        print("👥 Initializing EuroStyle Fashion HR Data Generator...")
        
        # Configuration
        self.base_year = 2023
        self.num_years = 2  # 2023-2024
        
        # File paths  
        self.output_dir = "data/csv"  # Output to data/csv directory
        self.csv_files = {}
        
        # Data containers
        self.entities = {}
        self.departments = {}
        self.positions = {}
        self.employees = {}
        self.contracts = {}
        
        # External data references (loaded from other systems)
        self.finance_entities = []
        self.stores = []
        self.cost_centers = []
        
        # European country configurations - EuroStyle countries: NL, DE, FR, BE, LU
        self.countries = {
            'NL': {
                'name': 'Netherlands',
                'currency': 'EUR',
                'annual_leave': 25,  # Minimum statutory days
                'sick_leave': 730,   # Up to 2 years
                'maternity_leave': 16,  # Weeks
                'paternity_leave': 6,   # Weeks (as of 2024)
                'working_hours': 40,    # Standard per week
                'min_salary': 24000,    # Minimum annual salary
                'avg_salary': 45000,
                'locales': ['nl_NL']
            },
            'DE': {
                'name': 'Germany',
                'currency': 'EUR',
                'annual_leave': 24,
                'sick_leave': 1460,  # Up to 4 years with continuation
                'maternity_leave': 14,
                'paternity_leave': 2,
                'working_hours': 40,
                'min_salary': 22000,
                'avg_salary': 48000,
                'locales': ['de_DE']
            },
            'FR': {
                'name': 'France',
                'currency': 'EUR',
                'annual_leave': 25,
                'sick_leave': 360,   # Initial period
                'maternity_leave': 16,
                'paternity_leave': 4,
                'working_hours': 35,  # 35-hour work week
                'min_salary': 21000,
                'avg_salary': 42000,
                'locales': ['fr_FR']
            },
            'BE': {
                'name': 'Belgium',
                'currency': 'EUR',
                'annual_leave': 20,  # Minimum statutory days
                'sick_leave': 365,   # Up to 1 year
                'maternity_leave': 15,  # Weeks
                'paternity_leave': 2,   # Weeks (as of 2023)
                'working_hours': 38,    # Standard per week
                'min_salary': 20000,    # Minimum annual salary
                'avg_salary': 41000,
                'locales': ['nl_NL']  # Use Dutch locale for Belgium
            },
            'LU': {
                'name': 'Luxembourg',
                'currency': 'EUR',
                'annual_leave': 25,
                'sick_leave': 365,
                'maternity_leave': 20,  # 20 weeks
                'paternity_leave': 2,
                'working_hours': 40,
                'min_salary': 25000,    # Higher due to Luxembourg wages
                'avg_salary': 55000,    # Highest in Europe
                'locales': ['fr_FR']  # Use French locale for Luxembourg
            }
        }
        
        # Initialize Faker instances for each locale
        self.fakers = {}
        for country, config in self.countries.items():
            # Use primary locale for each country
            locale = config['locales'][0]
            self.fakers[country] = Faker(locale)
        
        # Job families and their typical salaries (multipliers of base salary)
        self.job_families = {
            'Executive': {'multiplier': 3.0, 'levels': ['EXECUTIVE']},
            'Management': {'multiplier': 2.2, 'levels': ['DIRECTOR', 'MANAGER']},
            'Sales': {'multiplier': 1.1, 'levels': ['ENTRY', 'JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'Marketing': {'multiplier': 1.3, 'levels': ['JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'Finance': {'multiplier': 1.4, 'levels': ['JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'IT': {'multiplier': 1.5, 'levels': ['JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'Operations': {'multiplier': 1.0, 'levels': ['ENTRY', 'JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'HR': {'multiplier': 1.2, 'levels': ['JUNIOR', 'SENIOR', 'LEAD', 'MANAGER']},
            'Legal': {'multiplier': 1.6, 'levels': ['JUNIOR', 'SENIOR', 'LEAD']},
            'Retail': {'multiplier': 0.8, 'levels': ['ENTRY', 'JUNIOR', 'SENIOR', 'LEAD']}
        }
        
        print("✅ HR generator initialized with European employment law compliance")
    
    def load_external_data(self):
        """Load existing data from other systems for referential integrity."""
        print("\n📊 Loading external data for referential integrity...")
        
        try:
            # Load finance legal entities from unified data directory
            finance_entities_path = "data/csv/eurostyle_finance.legal_entities.csv.gz"
            if os.path.exists(finance_entities_path):
                import gzip
                with gzip.open(finance_entities_path, 'rt', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.finance_entities = list(reader)
                print(f"Loaded {len(self.finance_entities)} legal entities")
            
            # Load cost centers
            cost_centers_path = "data/csv/eurostyle_finance.cost_centers.csv.gz"
            if os.path.exists(cost_centers_path):
                import gzip
                with gzip.open(cost_centers_path, 'rt', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.cost_centers = list(reader)
                print(f"Loaded {len(self.cost_centers)} cost centers")
            
            # Load stores (fallback to operational data if available)
            stores_path = "data/csv/stores.csv.gz"
            if os.path.exists(stores_path):
                import gzip
                with gzip.open(stores_path, 'rt', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.stores = list(reader)
                print(f"Loaded {len(self.stores)} stores")
                
        except Exception as e:
            print(f"⚠️ Could not load all external data: {e}")
            print("Will generate HR data with mock references...")
    
    def generate_departments(self) -> List[Dict]:
        """Generate department hierarchy for each entity."""
        print("\n🏢 Generating department structure...")
        
        departments = []
        dept_id = 1
        
        # Standard department structure for each entity
        dept_structure = {
            'Corporate': {
                'parent': None,
                'level': 1,
                'type': 'CORPORATE',
                'children': {
                    'Executive': {'type': 'CORPORATE'},
                    'Finance': {'type': 'CORPORATE'},
                    'HR': {'type': 'SUPPORT'},
                    'IT': {'type': 'SUPPORT'},
                    'Legal': {'type': 'SUPPORT'},
                    'Marketing': {'type': 'SUPPORT'}
                }
            },
            'Operations': {
                'parent': None,
                'level': 1,
                'type': 'WAREHOUSE',
                'children': {
                    'Logistics': {'type': 'WAREHOUSE'},
                    'Supply Chain': {'type': 'WAREHOUSE'},
                    'Quality Control': {'type': 'WAREHOUSE'}
                }
            },
            'Retail': {
                'parent': None,
                'level': 1,
                'type': 'RETAIL',
                'children': {
                    'Store Operations': {'type': 'RETAIL'},
                    'Visual Merchandising': {'type': 'RETAIL'},
                    'Customer Service': {'type': 'RETAIL'}
                }
            }
        }
        
        # Generate departments for each entity
        for entity in self.finance_entities:
            entity_id = entity['entity_id']
            if entity['entity_type'] == 'HOLDING':
                continue  # Skip holding company for HR departments
            
            entity_depts = {}
            
            # Create top-level departments
            for dept_name, dept_config in dept_structure.items():
                dept_id_str = f"DEPT_{dept_id:06d}"
                department = {
                    'department_id': dept_id_str,
                    'department_code': f"{entity['entity_code']}_{dept_name.upper().replace(' ', '_')}",
                    'department_name': dept_name,
                    'entity_id': entity_id,  # Match schema order
                    'parent_department_id': '',
                    'manager_employee_id': '',  # Match schema field name
                    'cost_center_id': self._get_random_cost_center(entity_id),
                    'department_type': dept_config['type'],  # Match schema order
                    'location': '',  # Add missing field
                    'is_active': True,
                    'created_date': '2023-01-01 00:00:00'
                }
                departments.append(department)
                entity_depts[dept_name] = dept_id_str
                dept_id += 1
                
                # Create child departments
                for child_name, child_config in dept_config['children'].items():
                    child_dept_id = f"DEPT_{dept_id:06d}"
                    child_department = {
                        'department_id': child_dept_id,
                        'department_code': f"{entity['entity_code']}_{child_name.upper().replace(' ', '_')}",
                        'department_name': child_name,
                        'entity_id': entity_id,  # Match schema order
                        'parent_department_id': dept_id_str,
                        'manager_employee_id': '',  # Match schema field name
                        'cost_center_id': self._get_random_cost_center(entity_id),
                        'department_type': child_config['type'],  # Match schema order
                        'location': '',  # Add missing field
                        'is_active': True,
                        'created_date': '2023-01-01 00:00:00'
                    }
                    departments.append(child_department)
                    entity_depts[child_name] = child_dept_id
                    dept_id += 1
        
        self.departments = {d['department_id']: d for d in departments}
        
        print(f"Generated {len(departments)} departments across {len(self.finance_entities)} entities")
        return departments
    
    def generate_job_positions(self) -> List[Dict]:
        """Generate job positions for each department."""
        print("📋 Generating job positions...")
        
        positions = []
        pos_id = 1
        
        # Position templates by department type and job family
        position_templates = {
            'Executive': [
                {'title': 'Chief Executive Officer', 'level': 'EXECUTIVE', 'family': 'Executive', 'min_exp': 15, 'max_exp': 25},
                {'title': 'Chief Financial Officer', 'level': 'EXECUTIVE', 'family': 'Finance', 'min_exp': 12, 'max_exp': 20},
                {'title': 'Chief Technology Officer', 'level': 'EXECUTIVE', 'family': 'IT', 'min_exp': 12, 'max_exp': 18}
            ],
            'Finance': [
                {'title': 'Finance Director', 'level': 'DIRECTOR', 'family': 'Finance', 'min_exp': 8, 'max_exp': 15},
                {'title': 'Finance Manager', 'level': 'MANAGER', 'family': 'Finance', 'min_exp': 5, 'max_exp': 10},
                {'title': 'Senior Financial Analyst', 'level': 'SENIOR', 'family': 'Finance', 'min_exp': 3, 'max_exp': 7},
                {'title': 'Financial Analyst', 'level': 'JUNIOR', 'family': 'Finance', 'min_exp': 1, 'max_exp': 4}
            ],
            'HR': [
                {'title': 'HR Director', 'level': 'DIRECTOR', 'family': 'HR', 'min_exp': 8, 'max_exp': 15},
                {'title': 'HR Business Partner', 'level': 'SENIOR', 'family': 'HR', 'min_exp': 4, 'max_exp': 8},
                {'title': 'HR Coordinator', 'level': 'JUNIOR', 'family': 'HR', 'min_exp': 1, 'max_exp': 4}
            ],
            'IT': [
                {'title': 'IT Director', 'level': 'DIRECTOR', 'family': 'IT', 'min_exp': 8, 'max_exp': 15},
                {'title': 'Senior Software Engineer', 'level': 'SENIOR', 'family': 'IT', 'min_exp': 4, 'max_exp': 8},
                {'title': 'Software Engineer', 'level': 'JUNIOR', 'family': 'IT', 'min_exp': 1, 'max_exp': 4},
                {'title': 'IT Support Specialist', 'level': 'JUNIOR', 'family': 'IT', 'min_exp': 1, 'max_exp': 3}
            ],
            'Marketing': [
                {'title': 'Marketing Director', 'level': 'DIRECTOR', 'family': 'Marketing', 'min_exp': 6, 'max_exp': 12},
                {'title': 'Marketing Manager', 'level': 'MANAGER', 'family': 'Marketing', 'min_exp': 3, 'max_exp': 8},
                {'title': 'Digital Marketing Specialist', 'level': 'JUNIOR', 'family': 'Marketing', 'min_exp': 1, 'max_exp': 4}
            ],
            'Store Operations': [
                {'title': 'Store Manager', 'level': 'MANAGER', 'family': 'Retail', 'min_exp': 3, 'max_exp': 8},
                {'title': 'Assistant Store Manager', 'level': 'LEAD', 'family': 'Retail', 'min_exp': 2, 'max_exp': 5},
                {'title': 'Sales Associate', 'level': 'ENTRY', 'family': 'Retail', 'min_exp': 0, 'max_exp': 3}
            ],
            'Logistics': [
                {'title': 'Logistics Manager', 'level': 'MANAGER', 'family': 'Operations', 'min_exp': 4, 'max_exp': 8},
                {'title': 'Warehouse Supervisor', 'level': 'LEAD', 'family': 'Operations', 'min_exp': 2, 'max_exp': 6},
                {'title': 'Warehouse Worker', 'level': 'ENTRY', 'family': 'Operations', 'min_exp': 0, 'max_exp': 2}
            ]
        }
        
        # Generate positions for each department
        for dept_id, dept in self.departments.items():
            dept_name = dept['department_name']
            entity_id = dept['entity_id']
            country_code = self._get_country_from_entity(entity_id)
            country_config = self.countries.get(country_code, self.countries['NL'])
            
            # Get position templates for this department
            templates = position_templates.get(dept_name, [
                {'title': f"{dept_name} Manager", 'level': 'MANAGER', 'family': 'Management', 'min_exp': 3, 'max_exp': 8},
                {'title': f"Senior {dept_name} Specialist", 'level': 'SENIOR', 'family': 'Operations', 'min_exp': 2, 'max_exp': 5},
                {'title': f"{dept_name} Specialist", 'level': 'JUNIOR', 'family': 'Operations', 'min_exp': 0, 'max_exp': 3}
            ])
            
            for template in templates:
                pos_id_str = f"POS_{pos_id:06d}"
                
                # Calculate salary range based on job family and country
                family_config = self.job_families.get(template['family'], self.job_families['Operations'])
                base_salary = country_config['avg_salary']
                min_salary = base_salary * family_config['multiplier'] * 0.8
                max_salary = base_salary * family_config['multiplier'] * 1.4
                
                # Adjust by level
                level_multipliers = {
                    'ENTRY': 0.7, 'JUNIOR': 0.85, 'SENIOR': 1.0, 
                    'LEAD': 1.2, 'MANAGER': 1.5, 'DIRECTOR': 2.0, 'EXECUTIVE': 3.0
                }
                multiplier = level_multipliers.get(template['level'], 1.0)
                min_salary *= multiplier
                max_salary *= multiplier
                
                # Determine reporting position (higher level position in same department or parent department)
                reporting_position_id = None
                if template['level'] != 'EXECUTIVE':
                    # Find a higher-level position in the same department or parent
                    hierarchy = ['EXECUTIVE', 'DIRECTOR', 'MANAGER', 'LEAD', 'SENIOR', 'JUNIOR', 'ENTRY']
                    current_level_idx = hierarchy.index(template['level']) if template['level'] in hierarchy else len(hierarchy)
                    
                    # Look for positions with higher level (lower index in hierarchy)
                    for existing_pos in positions:
                        if (existing_pos['department_id'] == dept_id and 
                            existing_pos['position_level'] in hierarchy and
                            hierarchy.index(existing_pos['position_level']) < current_level_idx):
                            reporting_position_id = existing_pos['position_id']
                            break
                
                # Employment type and salary grade
                employment_type = 'PERMANENT'  # Most positions are permanent
                if template['level'] in ['ENTRY', 'JUNIOR'] and random.random() < 0.2:
                    employment_type = 'TEMPORARY'  # 20% of junior positions are temporary
                
                salary_grade = f"GRADE_{template['level'][:2]}{random.randint(1, 3)}"
                
                # Skills for the position
                skills = self._get_skills_for_family(template['family'])
                
                # Remote work eligibility
                remote_eligible = template['family'] in ['IT', 'Finance', 'HR', 'Marketing'] and random.random() < 0.7
                
                # Travel requirements
                travel_percentage = 0
                if template['level'] in ['DIRECTOR', 'EXECUTIVE']:
                    travel_percentage = random.randint(10, 30)
                elif template['family'] == 'Sales':
                    travel_percentage = random.randint(5, 20)
                
                position = {
                    'position_id': pos_id_str,
                    'position_code': f"{dept['department_code']}_{template['title'].upper().replace(' ', '_')}",
                    'position_title': template['title'],
                    'department_id': dept_id,
                    'reporting_position_id': reporting_position_id,  # Fixed: correct field name
                    'position_level': template['level'],
                    'employment_type': employment_type,  # Fixed: add missing field
                    'salary_grade': salary_grade,  # Fixed: add missing field
                    'min_salary_eur': Decimal(str(min_salary)).quantize(Decimal('0.01')),  # Fixed: correct field name
                    'max_salary_eur': Decimal(str(max_salary)).quantize(Decimal('0.01')),  # Fixed: correct field name
                    'country_code': country_code,  # Fixed: add missing field
                    'required_skills': skills,
                    'education_requirements': self._get_education_requirements(template['level']),
                    'experience_years': template['max_exp'],  # Fixed: single field, not min/max
                    'is_remote_eligible': remote_eligible,  # Fixed: add missing field
                    'travel_percentage': travel_percentage,  # Fixed: add missing field
                    'is_active': True,
                    'created_date': '2023-01-01 00:00:00'
                }
                positions.append(position)
                pos_id += 1
        
        self.positions = {p['position_id']: p for p in positions}
        
        print(f"Generated {len(positions)} job positions")
        return positions
    
    def generate_employees(self) -> List[Dict]:
        """Generate employee master data."""
        print("👥 Generating employees...")
        
        employees = []
        emp_id = 1
        
        # Generate employees for each entity
        for entity in self.finance_entities:
            if entity['entity_type'] == 'HOLDING':
                num_employees = random.randint(15, 25)  # Small holding company
            else:
                num_employees = random.randint(80, 150)  # Operating companies
            
            entity_id = entity['entity_id']
            country_code = self._get_country_from_entity(entity_id)
            faker = self.fakers[country_code]
            country_config = self.countries[country_code]
            
            for _ in range(num_employees):
                emp_id_str = f"EMP_{emp_id:06d}"
                
                # Generate realistic personal data
                gender = random.choice(['MALE', 'FEMALE', 'NON_BINARY', 'PREFER_NOT_TO_SAY'])
                if gender == 'MALE':
                    first_name = faker.first_name_male()
                    title = 'MR'
                elif gender == 'FEMALE':
                    first_name = faker.first_name_female()
                    title = random.choice(['MS', 'MRS'])
                else:
                    first_name = faker.first_name()
                    title = random.choice(['MR', 'MS'])
                
                last_name = faker.last_name()
                birth_date = faker.date_of_birth(minimum_age=18, maximum_age=65)
                hire_date = faker.date_between(start_date=date(2018, 1, 1), end_date=date(2024, 6, 30))
                
                # Employment status based on hire date and random factors
                if hire_date > date(2024, 1, 1):
                    status = 'ACTIVE'
                    termination_date = None
                    termination_reason = None
                else:
                    # 5% chance of termination for older employees
                    if random.random() < 0.05:
                        status = 'TERMINATED'
                        termination_date = faker.date_between(start_date=hire_date + timedelta(days=90), end_date=date.today())
                        termination_reason = random.choice(['RESIGNATION', 'TERMINATION', 'REDUNDANCY', 'RETIREMENT'])
                    elif random.random() < 0.02:
                        status = 'ON_LEAVE'
                        termination_date = None
                        termination_reason = None
                    else:
                        status = 'ACTIVE'
                        termination_date = None
                        termination_reason = None
                
                # Generate work and personal contact information
                work_email = f"{first_name.lower()}.{last_name.lower()}@eurostyle{country_code.lower()}.com"
                personal_email = faker.email()
                
                employee = {
                    'employee_id': emp_id_str,
                    'employee_number': f"{entity['entity_code']}{emp_id:06d}",
                    'entity_id': entity_id,
                    'personal_email': personal_email,
                    'work_email': work_email,
                    'title': title,
                    'first_name': first_name,
                    'middle_name': faker.first_name() if random.random() < 0.3 else '',
                    'last_name': last_name,
                    'preferred_name': first_name if random.random() < 0.9 else faker.first_name(),
                    'date_of_birth': birth_date.strftime('%Y-%m-%d'),
                    'gender': gender,
                    'nationality': country_code,
                    'country_of_birth': country_code if random.random() < 0.8 else random.choice(list(self.countries.keys())),
                    'marital_status': random.choice(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', 'DOMESTIC_PARTNERSHIP']),
                    'number_of_dependents': random.choices([0, 1, 2, 3, 4], weights=[30, 25, 25, 15, 5])[0],
                    
                    # Contact information
                    'phone_mobile': faker.phone_number(),
                    'phone_home': faker.phone_number() if random.random() < 0.7 else '',
                    'emergency_contact_name': faker.name(),
                    'emergency_contact_phone': faker.phone_number(),
                    'emergency_contact_relationship': random.choice(['SPOUSE', 'PARENT', 'SIBLING', 'CHILD', 'FRIEND']),
                    
                    # Address information
                    'address_street': faker.street_address(),
                    'address_city': faker.city(),
                    'address_state': faker.state() if country_code in ['DE', 'US'] else '',
                    'address_postal_code': faker.postcode(),
                    'address_country': country_code,
                    
                    # Legal and compliance (simplified for demo)
                    'social_security_number': f"***-**-{random.randint(1000, 9999)}",  # Masked
                    'tax_id': f"{country_code}{random.randint(100000, 999999)}",
                    'passport_number': f"{country_code}{random.randint(1000000, 9999999)}",
                    'passport_expiry_date': (date.today() + timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d'),
                    'visa_status': 'EU_CITIZEN' if random.random() < 0.9 else random.choice(['WORK_PERMIT', 'OTHER']),
                    'visa_expiry_date': (date.today() + timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d') if random.random() < 0.1 else '',
                    'work_permit_required': random.random() < 0.1,
                    'work_permit_expiry_date': (date.today() + timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d') if random.random() < 0.1 else '',
                    
                    # Employment status
                    'employee_status': status,
                    'hire_date': hire_date.strftime('%Y-%m-%d'),
                    'termination_date': termination_date.strftime('%Y-%m-%d') if termination_date else '',
                    'termination_reason': termination_reason or '',
                    'rehire_eligible': random.random() < 0.8,
                    'created_date': '2023-01-01 00:00:00',
                    'updated_date': '2024-01-01 00:00:00'
                }
                employees.append(employee)
                emp_id += 1
        
        self.employees = {e['employee_id']: e for e in employees}
        
        print(f"Generated {len(employees)} employees across {len(self.finance_entities)} entities")
        return employees
    
    def generate_employment_contracts(self) -> List[Dict]:
        """Generate employment contracts for employees."""
        print("📄 Generating employment contracts...")
        
        contracts = []
        contract_id = 1
        
        for emp_id, employee in self.employees.items():
            entity_id = employee['entity_id']
            country_code = self._get_country_from_entity(entity_id)
            country_config = self.countries[country_code]
            
            # Get suitable positions for this entity
            entity_positions = [p for p in self.positions.values() 
                              if p['department_id'] in [d['department_id'] for d in self.departments.values() if d['entity_id'] == entity_id]]
            
            if not entity_positions:
                continue
            
            position = random.choice(entity_positions)
            department = self.departments[position['department_id']]
            
            # Contract details
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            contract_type = random.choices(
                ['PERMANENT', 'TEMPORARY', 'INTERNSHIP', 'CONTRACTOR'],
                weights=[75, 15, 7, 3]
            )[0]
            
            # Contract terms based on country regulations
            if contract_type == 'PERMANENT':
                # Some permanent contracts have theoretical end dates for compliance/review
                if random.random() < 0.05:  # 5% have formal review dates
                    end_date = hire_date + timedelta(days=random.randint(1095, 1825))  # 3-5 years
                else:
                    end_date = None
                probation_months = random.choice([3, 6])  # Standard probation
                notice_weeks = random.choice([4, 8, 12])  # Based on tenure
            elif contract_type == 'TEMPORARY':
                end_date = hire_date + timedelta(days=random.randint(180, 730))
                probation_months = 1
                notice_weeks = 2
            else:  # INTERNSHIP, CONTRACTOR
                end_date = hire_date + timedelta(days=random.randint(90, 365))
                probation_months = 0 if contract_type == 'CONTRACTOR' else 1
                notice_weeks = 1
            
            # Working arrangements
            working_hours = country_config['working_hours'] + random.uniform(-5, 5)
            work_schedule = random.choices(
                ['FULL_TIME', 'PART_TIME', 'FLEXIBLE', 'SHIFT_WORK'],
                weights=[70, 20, 8, 2]
            )[0]
            
            if work_schedule == 'PART_TIME':
                working_hours *= random.uniform(0.5, 0.8)
            
            remote_allowed = random.random() < 0.4  # 40% can work remotely
            remote_days = random.randint(1, 3) if remote_allowed else 0
            
            # Get store assignment if retail
            store_id = ''
            if department['department_type'] == 'RETAIL' and self.stores:
                # Try to match store to entity country
                entity_stores = [s for s in self.stores if s.get('country', 'NL') == country_code]
                if entity_stores:
                    store_id = random.choice(entity_stores)['store_id']
                else:
                    store_id = random.choice(self.stores)['store_id']
            
            contract = {
                'contract_id': f"CONT_{contract_id:08d}",
                'employee_id': emp_id,
                'contract_type': contract_type,
                'contract_status': 'ACTIVE' if employee['employee_status'] == 'ACTIVE' else 'TERMINATED',
                'position_id': position['position_id'],
                'department_id': department['department_id'],
                'manager_id': '',  # Will be populated later
                
                # Contract terms
                'start_date': hire_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
                'probation_period_months': probation_months,
                'notice_period_weeks': notice_weeks,
                'working_hours_per_week': Decimal(str(working_hours)).quantize(Decimal('0.1')),
                'work_schedule': work_schedule,
                'remote_work_allowed': remote_allowed,
                'remote_work_days_per_week': remote_days,
                
                # Location and reporting
                'primary_work_location': f"{country_config['name']} Office",
                'store_id': store_id,
                'reports_to_employee_id': '',  # Will be set later
                
                # Legal compliance
                'collective_bargaining_agreement': f"{country_code}_RETAIL_CBA" if department['department_type'] == 'RETAIL' else '',
                'union_membership': random.random() < 0.3,  # 30% union membership
                
                'created_date': '2023-01-01 00:00:00',
                'signed_date': hire_date.strftime('%Y-%m-%d'),
                'terminated_date': employee['termination_date'] if employee['termination_date'] else ''
            }
            contracts.append(contract)
            contract_id += 1
        
        self.contracts = {c['contract_id']: c for c in contracts}
        
        print(f"Generated {len(contracts)} employment contracts")
        return contracts
    
    def generate_compensation_history(self) -> List[Dict]:
        """Generate compensation history with salary changes matching database schema."""
        print("💰 Generating compensation history...")
        
        compensation_records = []
        comp_id = 1
        
        # Generate realistic compensation changes for each employee
        for contract in self.contracts.values():
            employee = self.employees[contract['employee_id']]
            position = self.positions[contract['position_id']]
            country_code = self._get_country_from_entity(employee['entity_id'])
            hire_date = datetime.strptime(contract['start_date'], '%Y-%m-%d').date()
            
            # Calculate base salary from position range
            min_salary = float(position['min_salary_eur'])  # Fixed: correct field name
            max_salary = float(position['max_salary_eur'])  # Fixed: correct field name
            initial_salary = random.uniform(min_salary, max_salary * 0.8)  # Start lower for growth
            
            # Adjust for part-time
            if contract['work_schedule'] == 'PART_TIME':
                initial_salary *= random.uniform(0.6, 0.8)
            
            current_salary = initial_salary
            
            # Generate multiple compensation changes over employment period
            change_dates = []
            
            # Initial hire record
            change_dates.append((hire_date, 'HIRE'))
            
            # Add periodic reviews/promotions
            review_date = hire_date + timedelta(days=365)  # Annual reviews
            while review_date < date(2024, 8, 31):
                if random.random() < 0.7:  # 70% chance of salary change each year
                    change_type = random.choices(
                        ['ANNUAL_REVIEW', 'PROMOTION', 'MARKET_ADJUSTMENT', 'MERIT_INCREASE'],
                        weights=[50, 15, 20, 15]
                    )[0]
                    change_dates.append((review_date, change_type))
                
                review_date += timedelta(days=365)
            
            # Generate compensation records for each change
            for i, (change_date, change_reason) in enumerate(change_dates):
                previous_salary = current_salary if i > 0 else None
                
                # Calculate new salary based on change type
                if change_reason == 'HIRE':
                    new_salary = initial_salary
                    change_percentage = 0.0
                elif change_reason == 'PROMOTION':
                    increase = random.uniform(0.15, 0.30)  # 15-30% for promotion
                    new_salary = current_salary * (1 + increase)
                    change_percentage = increase * 100
                elif change_reason == 'MARKET_ADJUSTMENT':
                    increase = random.uniform(0.08, 0.15)  # 8-15% for market
                    new_salary = current_salary * (1 + increase)
                    change_percentage = increase * 100
                else:  # ANNUAL_REVIEW or MERIT_INCREASE
                    increase = random.uniform(0.02, 0.08)  # 2-8% for regular increases
                    new_salary = current_salary * (1 + increase)
                    change_percentage = increase * 100
                
                # Ensure salary doesn't exceed position max
                new_salary = min(new_salary, max_salary)
                current_salary = new_salary
                
                # Calculate benefits and bonuses
                bonus_amount = None
                equity_grant = None
                health_contribution = None
                other_benefits = None
                
                # Generate bonuses for certain change types and levels
                if change_reason in ['PROMOTION', 'ANNUAL_REVIEW'] and position['position_level'] in ['SENIOR', 'LEAD', 'MANAGER', 'DIRECTOR', 'EXECUTIVE']:
                    bonus_amount = Decimal(str(new_salary * random.uniform(0.05, 0.25))).quantize(Decimal('0.01'))
                
                # Equity grants for senior levels
                if change_reason == 'PROMOTION' and position['position_level'] in ['DIRECTOR', 'EXECUTIVE']:
                    equity_grant = Decimal(str(random.uniform(5000, 50000))).quantize(Decimal('0.01'))
                
                # Health insurance contribution (company portion)
                if random.random() < 0.8:  # 80% of employees get health contribution
                    health_contribution = Decimal(str(random.uniform(150, 400))).quantize(Decimal('0.01'))  # Monthly
                
                # Other benefits (meal vouchers, transport, etc.)
                if random.random() < 0.6:  # 60% get additional benefits
                    other_benefits = Decimal(str(random.uniform(50, 200))).quantize(Decimal('0.01'))  # Monthly
                
                # Commission rate for sales positions (detect from position title)
                commission_rate = None
                if any(word in position['position_title'].lower() for word in ['sales', 'account', 'business development']):
                    commission_rate = Decimal(str(random.uniform(0.02, 0.08))).quantize(Decimal('0.01'))
                
                # Pension contribution
                pension_percentage = Decimal(str(random.uniform(3.0, 8.0))).quantize(Decimal('0.01'))
                
                compensation = {
                    'compensation_id': f"COMP_{comp_id:08d}",
                    'employee_id': contract['employee_id'],
                    'effective_date': change_date.strftime('%Y-%m-%d'),
                    'change_reason': change_reason,
                    
                    # Salary change tracking (matching database schema)
                    'previous_base_salary_eur': Decimal(str(previous_salary)).quantize(Decimal('0.01')) if previous_salary else None,
                    'new_base_salary_eur': Decimal(str(new_salary)).quantize(Decimal('0.01')),
                    'salary_change_percentage': Decimal(str(change_percentage)).quantize(Decimal('0.01')),
                    'currency': 'EUR',
                    
                    # Variable compensation
                    'bonus_amount_eur': bonus_amount,
                    'commission_rate': commission_rate,
                    'equity_grant_value_eur': equity_grant,
                    
                    # Benefits
                    'health_insurance_contribution_eur': health_contribution,
                    'pension_contribution_percentage': pension_percentage,
                    'other_benefits_eur': other_benefits,
                    
                    # Approval tracking
                    'approved_by': f"MGR_{random.randint(1, 50)}",
                    'hr_approved_by': f"HR_{random.randint(1, 10)}",
                    'created_date': change_date.strftime('%Y-%m-%d') + ' 00:00:00'
                }
                compensation_records.append(compensation)
                comp_id += 1
        
        print(f"Generated {len(compensation_records)} compensation change records")
        return compensation_records
    
    def generate_leave_requests(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate leave requests and balances with European compliance."""
        print("🏖️ Generating leave requests and balances...")
        
        leave_requests = []
        leave_balances = []
        request_id = 1
        balance_id = 1
        
        for emp_id, employee in self.employees.items():
            if employee['employee_status'] != 'ACTIVE':
                continue
            
            country_code = self._get_country_from_entity(employee['entity_id'])
            country_config = self.countries[country_code]
            
            # Generate leave balances for 2023 and 2024
            for year in [2023, 2024]:
                for leave_type in ['ANNUAL', 'SICK', 'PERSONAL']:
                    if leave_type == 'ANNUAL':
                        entitlement = country_config['annual_leave']
                    elif leave_type == 'SICK':
                        entitlement = 365  # Simplified
                    else:
                        entitlement = 5  # Personal leave
                    
                    used = random.uniform(0, entitlement * 0.8)
                    carried_forward = random.uniform(0, min(5, entitlement - used)) if leave_type == 'ANNUAL' else 0
                    current_balance = entitlement + carried_forward - used
                    
                    balance = {
                        'balance_id': f"BAL_{balance_id:08d}",
                        'employee_id': emp_id,
                        'leave_type': leave_type,
                        'balance_year': year,
                        'opening_balance': Decimal(str(carried_forward)).quantize(Decimal('0.1')),
                        'accrued_days': Decimal(str(entitlement)).quantize(Decimal('0.1')),
                        'used_days': Decimal(str(used)).quantize(Decimal('0.1')),
                        'expired_days': Decimal('0.0'),
                        'current_balance': Decimal(str(current_balance)).quantize(Decimal('0.1')),
                        'statutory_minimum': Decimal(str(country_config['annual_leave'])).quantize(Decimal('0.1')) if leave_type == 'ANNUAL' else Decimal('0.0'),
                        'company_entitlement': Decimal(str(entitlement)).quantize(Decimal('0.1')),
                        'max_carryover': Decimal('5.0') if leave_type == 'ANNUAL' else Decimal('0.0'),
                        'expiry_date': f"{year + 1}-03-31" if leave_type == 'ANNUAL' else '',
                        'sick_leave_unlimited': leave_type == 'SICK',
                        'long_term_illness_days': Decimal('0.0') if leave_type == 'SICK' else None,
                        'last_updated': '2024-01-01',
                        'created_date': '2024-01-01 00:00:00'
                    }
                    leave_balances.append(balance)
                    balance_id += 1
            
            # Generate some leave requests
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            
            # Generate 2-8 leave requests per active employee
            num_requests = random.randint(2, 8)
            
            for _ in range(num_requests):
                # Random leave type weighted by common usage
                leave_type = random.choices(
                    ['ANNUAL', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY'],
                    weights=[70, 20, 5, 3, 2]
                )[0]
                
                # Generate reasonable leave dates
                leave_start = self.fakers['NL'].date_between(
                    start_date=max(hire_date, date(2023, 1, 1)),
                    end_date=date(2024, 8, 31)
                )
                
                if leave_type == 'SICK':
                    duration = random.choices([1, 2, 3, 5, 10, 30], weights=[40, 25, 15, 10, 7, 3])[0]
                elif leave_type in ['MATERNITY', 'PATERNITY']:
                    duration = random.randint(10, 80)
                else:
                    duration = random.randint(1, 15)
                
                leave_end = leave_start + timedelta(days=duration - 1)
                
                # Determine request status and workflow
                status = random.choices(['APPROVED', 'PENDING', 'REJECTED'], weights=[85, 10, 5])[0]
                request_date = leave_start - timedelta(days=random.randint(1, 30))
                
                # Generate appropriate sub-types for demo purposes (simplified)
                sick_leave_type = None
                parental_leave_type = None
                special_leave_type = None
                
                if leave_type == 'SICK':
                    sick_leave_type = random.choice(['SHORT_TERM', 'CHRONIC', 'INJURY']) if duration > 5 else 'SHORT_TERM'
                elif leave_type in ['MATERNITY', 'PATERNITY']:
                    parental_leave_type = leave_type.lower()
                elif leave_type == 'PERSONAL':
                    special_leave_type = random.choice(['BEREAVEMENT', 'EMERGENCY', 'PERSONAL'])
                
                # Approval workflow
                approval_date = None
                rejection_reason = None
                if status == 'APPROVED':
                    approval_date = (request_date + timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d')
                elif status == 'REJECTED':
                    rejection_reason = random.choice([
                        'Insufficient leave balance',
                        'Business needs - peak period',
                        'Short notice - less than 48 hours',
                        'Documentation incomplete'
                    ])
                
                # Sick leave compliance tracking
                requires_medical = duration > 3 if leave_type == 'SICK' else False
                medical_provided = random.random() < 0.8 if requires_medical else False
                
                request = {
                    'leave_request_id': f"LR_{request_id:08d}",
                    'employee_id': emp_id,
                    'leave_type': leave_type,
                    'start_date': leave_start.strftime('%Y-%m-%d'),
                    'end_date': leave_end.strftime('%Y-%m-%d'),
                    'total_days': Decimal(str(duration)).quantize(Decimal('0.1')),
                    'request_date': request_date.strftime('%Y-%m-%d'),
                    
                    # Sub-types (optional fields for demo)
                    'sick_leave_type': sick_leave_type,
                    'parental_leave_type': parental_leave_type,
                    'special_leave_type': special_leave_type,
                    
                    # Workflow fields
                    'status': status,  # Fixed: correct field name
                    'requested_by': emp_id,  # Fixed: populate requested_by
                    'approved_by': f"MGR_{random.randint(1, 100)}",
                    'approval_date': approval_date,  # Fixed: populate approval_date
                    'rejection_reason': rejection_reason,  # Fixed: populate rejection_reason
                    
                    # Medical compliance
                    'medical_certificate_required': requires_medical,
                    'medical_certificate_provided': medical_provided,
                    'doctor_name': f"Dr. {self.fakers['NL'].last_name()}" if medical_provided else None,
                    
                    # Leave details
                    'statutory_entitlement': leave_type in ['ANNUAL', 'MATERNITY', 'PATERNITY'],
                    'paid_leave': leave_type != 'PERSONAL',
                    'pay_percentage': Decimal('100.00') if leave_type != 'SICK' else Decimal('70.00'),
                    'comments': self._get_leave_reason(leave_type),
                    
                    'created_date': request_date.strftime('%Y-%m-%d') + ' 00:00:00'
                }
                leave_requests.append(request)
                request_id += 1
        
        print(f"Generated {len(leave_requests)} leave requests and {len(leave_balances)} leave balances")
        return leave_requests, leave_balances
    
    def generate_performance_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate performance cycles and reviews."""
        print("📈 Generating performance management data...")
        
        cycles = []
        reviews = []
        
        # Create annual performance cycles
        for year in [2023, 2024]:
            cycle = {
                'cycle_id': f"CYCLE_{year}_ANNUAL",
                'cycle_name': f"Annual Performance Review {year}",
                'cycle_year': year,
                'cycle_type': 'ANNUAL',
                'planning_start_date': f"{year}-01-01",
                'planning_end_date': f"{year}-02-28",
                'review_start_date': f"{year}-11-01",
                'review_end_date': f"{year}-12-31",
                'calibration_date': f"{year + 1}-01-15",
                'entity_ids': [e['entity_id'] for e in self.finance_entities],
                'is_active': year == 2024,
                'created_by': 'HR_SYSTEM',
                'created_date': f"{year}-01-01 00:00:00"
            }
            cycles.append(cycle)
        
        # Generate performance reviews
        review_id = 1
        
        for cycle in cycles:
            cycle_year = cycle['cycle_year']
            
            # Only generate reviews for employees who were active during the cycle
            eligible_employees = [
                emp for emp in self.employees.values()
                if (datetime.strptime(emp['hire_date'], '%Y-%m-%d').date() <= date(cycle_year, 6, 30) and
                    (not emp['termination_date'] or 
                     datetime.strptime(emp['termination_date'], '%Y-%m-%d').date() >= date(cycle_year, 6, 30)))
            ]
            
            for employee in eligible_employees:
                # Skip executives and very new employees
                if random.random() < 0.1:  # 10% skip rate
                    continue
                
                # Generate realistic performance data
                goals_score = random.uniform(2.0, 5.0)
                competency_score = random.uniform(2.5, 4.8)
                overall_score = (goals_score + competency_score) / 2
                
                # Map score to rating
                if overall_score >= 4.5:
                    rating = 'EXCEEDS_EXPECTATIONS'
                elif overall_score >= 3.5:
                    rating = 'MEETS_EXPECTATIONS'
                elif overall_score >= 2.5:
                    rating = 'PARTIALLY_MEETS'
                elif overall_score >= 1.5:
                    rating = 'BELOW_EXPECTATIONS'
                else:
                    rating = 'UNSATISFACTORY'
                
                # Generate realistic goals and competencies (as JSON)
                goals_json = json.dumps([
                    {"goal": "Achieve sales target", "target": "100%", "achievement": f"{random.randint(80, 120)}%"},
                    {"goal": "Customer satisfaction", "target": "4.5/5", "achievement": f"{random.uniform(4.0, 5.0):.1f}/5"},
                    {"goal": "Team collaboration", "target": "Effective", "achievement": "Achieved"}
                ])
                
                competencies_json = json.dumps({
                    "leadership": random.uniform(3.0, 5.0),
                    "communication": random.uniform(3.0, 5.0),
                    "problem_solving": random.uniform(3.0, 5.0),
                    "adaptability": random.uniform(3.0, 5.0)
                })
                
                review = {
                    'review_id': f"REV_{review_id:08d}",
                    'cycle_id': cycle['cycle_id'],
                    'employee_id': employee['employee_id'],
                    'reviewer_id': f"MGR_{random.randint(1, 50)}",  # Mock manager ID
                    'review_period_start': f"{cycle_year}-01-01",
                    'review_period_end': f"{cycle_year}-12-31",
                    
                    # Goals and competencies
                    'goals_json': goals_json,
                    'overall_goals_score': Decimal(str(goals_score)).quantize(Decimal('0.1')),
                    'competencies_json': competencies_json,
                    'overall_competency_score': Decimal(str(competency_score)).quantize(Decimal('0.1')),
                    
                    # Overall assessment
                    'overall_rating': rating,
                    'overall_score': Decimal(str(overall_score)).quantize(Decimal('0.1')),
                    
                    # Comments
                    'manager_comments': self._get_performance_comment(rating, True),
                    'employee_comments': self._get_performance_comment(rating, False),
                    'development_areas': self._get_development_areas(),
                    'development_plan': self._get_development_plan(),
                    
                    # Calibration
                    'calibrated_rating': rating if random.random() < 0.9 else None,
                    'calibrated_by': 'HR_DIRECTOR' if random.random() < 0.9 else None,
                    'calibrated_date': f"{cycle_year + 1}-01-15" if random.random() < 0.9 else None,
                    
                    'review_status': 'FINAL' if cycle_year == 2023 else random.choice(['DRAFT', 'FINAL']),
                    'created_date': f"{cycle_year}-11-01 00:00:00",
                    'completed_date': f"{cycle_year}-12-15 00:00:00" if cycle_year == 2023 else None
                }
                reviews.append(review)
                review_id += 1
        
        print(f"Generated {len(cycles)} performance cycles and {len(reviews)} performance reviews")
        return cycles, reviews
    
    def generate_training_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate training programs and employee training records."""
        print("🎓 Generating training and development data...")
        
        programs = []
        training_records = []
        
        # Standard training programs
        program_templates = [
            {
                'code': 'MANDATORY_001', 'name': 'Data Protection & GDPR Compliance', 'type': 'MANDATORY',
                'duration': 2.0, 'method': 'ONLINE', 'provider': 'EuroStyle Academy',
                'cost': 0, 'families': ['ALL'], 'levels': ['ALL'], 'certification': 12, 'recert': True
            },
            {
                'code': 'MANDATORY_002', 'name': 'Health & Safety Training', 'type': 'MANDATORY',
                'duration': 4.0, 'method': 'BLENDED', 'provider': 'Safety First Ltd',
                'cost': 150, 'families': ['ALL'], 'levels': ['ALL'], 'certification': 24, 'recert': True
            },
            {
                'code': 'LEADERSHIP_001', 'name': 'Leadership Fundamentals', 'type': 'LEADERSHIP',
                'duration': 16.0, 'method': 'CLASSROOM', 'provider': 'Leadership Institute',
                'cost': 1200, 'families': ['Management'], 'levels': ['MANAGER', 'DIRECTOR'], 'certification': 0, 'recert': False
            },
            {
                'code': 'TECHNICAL_001', 'name': 'Advanced Excel for Finance', 'type': 'TECHNICAL',
                'duration': 8.0, 'method': 'ONLINE', 'provider': 'TechSkills Online',
                'cost': 300, 'families': ['Finance'], 'levels': ['JUNIOR', 'SENIOR'], 'certification': 0, 'recert': False
            },
            {
                'code': 'SALES_001', 'name': 'Customer Service Excellence', 'type': 'OPTIONAL',
                'duration': 6.0, 'method': 'WORKSHOP', 'provider': 'Service Academy',
                'cost': 450, 'families': ['Sales', 'Retail'], 'levels': ['ALL'], 'certification': 12, 'recert': False
            },
            {
                'code': 'COMPLIANCE_001', 'name': 'Anti-Money Laundering Training', 'type': 'COMPLIANCE',
                'duration': 1.5, 'method': 'ONLINE', 'provider': 'Compliance Corp',
                'cost': 0, 'families': ['Finance'], 'levels': ['ALL'], 'certification': 12, 'recert': True
            }
        ]
        
        # Generate training programs
        for i, template in enumerate(program_templates, 1):
            program = {
                'program_id': f"PROG_{i:06d}",
                'program_code': template['code'],
                'program_name': template['name'],
                'program_type': template['type'],
                'description': f"Comprehensive {template['name'].lower()} program for EuroStyle employees.",
                'duration_hours': int(template['duration']),  # Convert to integer for UInt16 compatibility
                'delivery_method': template['method'],
                'provider': template['provider'],
                'cost_per_participant': Decimal(str(template['cost'])),
                'currency': 'EUR',
                'target_job_families': json.dumps(template['families']),  # Convert to JSON string
                'target_levels': json.dumps(template['levels']),  # Convert to JSON string
                'prerequisites': 'None' if template['type'] == 'MANDATORY' else 'Manager approval',
                'compliance_category': template['type'] if template['type'] == 'COMPLIANCE' else '',
                'certification_valid_months': template['certification'],
                'recertification_required': template['recert'],
                'is_active': True,
                'created_date': '2023-01-01 00:00:00'
            }
            programs.append(program)
        
        # Generate employee training records
        training_id = 1
        
        for emp_id, employee in self.employees.items():
            if employee['employee_status'] != 'ACTIVE':
                continue
            
            # Get employee's contract and position
            emp_contracts = [c for c in self.contracts.values() if c['employee_id'] == emp_id]
            if not emp_contracts:
                continue
            
            contract = emp_contracts[0]
            position = self.positions.get(contract['position_id'])
            if not position:
                continue
            
            hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
            
            # Assign relevant training programs
            for program in programs:
                # Check if program is relevant for this employee (use position title to infer job family)
                families = program['target_job_families']
                levels = program['target_levels']
                
                # Infer job family from position title since job_family field doesn't exist in schema
                position_title_lower = position['position_title'].lower()
                inferred_family = 'Operations'  # default
                if any(word in position_title_lower for word in ['finance', 'financial', 'accounting']):
                    inferred_family = 'Finance'
                elif any(word in position_title_lower for word in ['sales', 'account', 'business']):
                    inferred_family = 'Sales'
                elif any(word in position_title_lower for word in ['marketing', 'digital']):
                    inferred_family = 'Marketing'
                elif any(word in position_title_lower for word in ['hr', 'human']):
                    inferred_family = 'HR'
                elif any(word in position_title_lower for word in ['it', 'software', 'engineer', 'technical']):
                    inferred_family = 'IT'
                elif any(word in position_title_lower for word in ['manager', 'director', 'executive', 'ceo', 'cfo']):
                    inferred_family = 'Management'
                elif any(word in position_title_lower for word in ['store', 'retail', 'sales associate']):
                    inferred_family = 'Retail'
                
                if (families != ['ALL'] and inferred_family not in families):
                    continue
                if (levels != ['ALL'] and position['position_level'] not in levels):
                    continue
                
                # Mandatory programs - high enrollment rate
                if program['program_type'] == 'MANDATORY':
                    enrollment_rate = 0.95
                # Leadership programs - only for managers
                elif program['program_type'] == 'LEADERSHIP':
                    enrollment_rate = 0.7 if position['position_level'] in ['MANAGER', 'DIRECTOR'] else 0.1
                # Optional programs - variable rate
                else:
                    enrollment_rate = 0.4
                
                if random.random() > enrollment_rate:
                    continue
                
                # Generate training dates
                enrollment_date = self.fakers['NL'].date_between(
                    start_date=max(hire_date, date(2023, 1, 1)),
                    end_date=date(2024, 6, 30)
                )
                start_date = enrollment_date + timedelta(days=random.randint(1, 30))
                
                # Completion based on program type and employee factors
                if program['program_type'] == 'MANDATORY':
                    completion_rate = 0.98
                else:
                    completion_rate = 0.85
                
                if random.random() < completion_rate:
                    completion_date = start_date + timedelta(days=random.randint(1, 90))
                    status = 'COMPLETED'
                    score = random.uniform(70, 100) if program['program_type'] in ['CERTIFICATION', 'COMPLIANCE'] else None
                else:
                    completion_date = None
                    status = random.choice(['IN_PROGRESS', 'FAILED', 'CANCELLED'])
                    score = random.uniform(40, 69) if status == 'FAILED' else None
                
                # Calculate expiry date if certification
                expiry_date = None
                if program['certification_valid_months'] > 0 and completion_date:
                    expiry_date = completion_date + timedelta(days=program['certification_valid_months'] * 30)
                
                # Generate certification details
                certification_earned = False
                certification_number = None
                certification_expiry_date = None
                
                if status == 'COMPLETED' and program['certification_valid_months'] > 0:
                    if random.random() < 0.9:  # 90% earn certification if they complete
                        certification_earned = True
                        certification_number = f"CERT-{program['program_code']}-{training_id:06d}-{completion_date.year}"
                        certification_expiry_date = expiry_date
                
                # Generate instructor details
                instructor_names = [
                    "Dr. Sarah Johnson", "Prof. Michael Chen", "Maria Rodriguez", "James Wilson",
                    "Dr. Emma Thompson", "Carlos Mendez", "Lisa Anderson", "Ahmed Hassan",
                    "Sophie Martin", "David Brown", "Anna Kowalski", "Roberto Silva"
                ]
                instructor_name = random.choice(instructor_names)
                
                # Training location based on delivery method and country
                country_code = self._get_country_from_entity(employee['entity_id'])
                if program['delivery_method'] == 'ONLINE':
                    training_location = 'Online/Virtual'
                elif program['delivery_method'] == 'CLASSROOM':
                    training_location = f"EuroStyle {self.countries[country_code]['name']} Training Center"
                else:  # BLENDED, WORKSHOP
                    training_location = f"EuroStyle {self.countries[country_code]['name']} Office"
                
                # Employee feedback and rating (for completed trainings)
                employee_feedback = None
                employee_rating = None
                if status == 'COMPLETED':
                    if random.random() < 0.7:  # 70% provide feedback
                        feedback_templates = [
                            "Very informative and well-structured course.",
                            "Excellent instructor, learned a lot of practical skills.",
                            "Good content but could use more interactive elements.",
                            "Highly recommend this training to colleagues.",
                            "Clear explanations and relevant examples.",
                            "Training met my expectations and professional needs.",
                            "Could benefit from more hands-on exercises."
                        ]
                        employee_feedback = random.choice(feedback_templates)
                        employee_rating = random.randint(3, 5)  # 3-5 star rating
                
                training_record = {
                    'training_record_id': f"TR_{training_id:08d}",
                    'employee_id': emp_id,
                    'program_id': program['program_id'],
                    'enrollment_date': enrollment_date.strftime('%Y-%m-%d'),
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'completion_date': completion_date.strftime('%Y-%m-%d') if completion_date else None,
                    'status': status,
                    
                    # Fixed: Add missing fields matching database schema
                    'score': Decimal(str(score)).quantize(Decimal('0.1')) if score else None,
                    'certification_earned': certification_earned,
                    'certification_number': certification_number,
                    'certification_expiry_date': certification_expiry_date.strftime('%Y-%m-%d') if certification_expiry_date else None,
                    'instructor_name': instructor_name,
                    'training_location': training_location,
                    'cost_eur': program['cost_per_participant'],
                    'approved_by': f"MGR_{random.randint(1, 50)}",
                    'employee_feedback': employee_feedback,
                    'employee_rating': employee_rating,
                    
                    'created_date': enrollment_date.strftime('%Y-%m-%d') + ' 00:00:00'
                }
                training_records.append(training_record)
                training_id += 1
        
        print(f"Generated {len(programs)} training programs and {len(training_records)} training records")
        return programs, training_records
    
    def generate_surveys_and_responses(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate employee surveys and responses."""
        print("📋 Generating employee surveys and responses...")
        
        surveys = []
        responses = []
        
        # Survey templates
        survey_templates = [
            {
                'name': 'Annual Employee Engagement Survey 2023',
                'type': 'ENGAGEMENT',
                'launch': '2023-03-01',
                'close': '2023-03-31',
                'anonymous': True,
                'questions': [
                    {"id": 1, "text": "How satisfied are you with your current role?", "type": "scale_5"},
                    {"id": 2, "text": "Do you feel valued by your manager?", "type": "scale_5"},
                    {"id": 3, "text": "Would you recommend EuroStyle as a great place to work?", "type": "scale_5"},
                    {"id": 4, "text": "What could we improve?", "type": "text"}
                ]
            },
            {
                'name': 'Quarterly Pulse Survey Q2 2024',
                'type': 'PULSE',
                'launch': '2024-04-01',
                'close': '2024-04-15',
                'anonymous': True,
                'questions': [
                    {"id": 1, "text": "How are you feeling about your workload?", "type": "scale_5"},
                    {"id": 2, "text": "Rate your work-life balance", "type": "scale_5"},
                    {"id": 3, "text": "Any concerns or suggestions?", "type": "text"}
                ]
            }
        ]
        
        # Generate surveys
        for i, template in enumerate(survey_templates, 1):
            survey = {
                'survey_id': f"SURVEY_{i:06d}",
                'survey_name': template['name'],
                'survey_type': template['type'],
                'description': f"EuroStyle {template['type'].lower()} survey to measure employee satisfaction and engagement.",
                'questions_json': json.dumps(template['questions']),
                'launch_date': template['launch'],
                'close_date': template['close'],
                'target_entities': [e['entity_id'] for e in self.finance_entities],
                'target_departments': [],
                'target_job_levels': [],
                'is_anonymous': template['anonymous'],
                'survey_status': 'CLOSED',
                'created_by': 'HR_SYSTEM',
                'created_date': template['launch'] + ' 00:00:00'
            }
            surveys.append(survey)
        
        # Generate survey responses
        response_id = 1
        
        for survey in surveys:
            survey_date = datetime.strptime(survey['launch_date'], '%Y-%m-%d').date()
            questions = json.loads(survey['questions_json'])
            
            # Get eligible employees (active at time of survey)
            eligible_employees = [
                emp for emp in self.employees.values()
                if (datetime.strptime(emp['hire_date'], '%Y-%m-%d').date() <= survey_date and
                    (not emp['termination_date'] or 
                     datetime.strptime(emp['termination_date'], '%Y-%m-%d').date() >= survey_date))
            ]
            
            # Response rate varies by survey type
            response_rate = 0.75 if survey['survey_type'] == 'ENGAGEMENT' else 0.85
            
            for employee in eligible_employees:
                if random.random() > response_rate:
                    continue
                
                # Generate responses
                responses_data = {}
                for question in questions:
                    if question['type'] == 'scale_5':
                        # Weighted towards positive responses
                        responses_data[str(question['id'])] = random.choices(
                            [1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30]
                        )[0]
                    elif question['type'] == 'text':
                        responses_data[str(question['id'])] = random.choice([
                            "Overall very satisfied with the company culture.",
                            "Would like more flexible working arrangements.",
                            "Great team collaboration and support.",
                            "Career development opportunities could be improved.",
                            "Excellent management and clear communication.",
                            ""  # Some skip text questions
                        ])
                
                completion_percentage = 100.0 if len(responses_data) == len(questions) else random.uniform(60, 95)
                
                # Get department and job level for demographics
                emp_contracts = [c for c in self.contracts.values() if c['employee_id'] == employee['employee_id']]
                department_id = emp_contracts[0]['department_id'] if emp_contracts else None
                position = self.positions.get(emp_contracts[0]['position_id']) if emp_contracts else None
                job_level = position['position_level'] if position else 'UNKNOWN'
                
                # Calculate tenure at survey time
                hire_date = datetime.strptime(employee['hire_date'], '%Y-%m-%d').date()
                tenure_months = (survey_date.year - hire_date.year) * 12 + (survey_date.month - hire_date.month)
                
                # Generate demographic groupings
                department_group = None
                if department_id:
                    dept = self.departments.get(department_id)
                    if dept:
                        dept_type = dept.get('department_type', 'OTHER')
                        department_group = {
                            'CORPORATE': 'Corporate Functions',
                            'SUPPORT': 'Support Services', 
                            'RETAIL': 'Retail Operations',
                            'OPERATIONS': 'Operations'
                        }.get(dept_type, 'Other')
                
                # Tenure groupings
                if tenure_months < 12:
                    tenure_group = '0-1 years'
                elif tenure_months < 36:
                    tenure_group = '1-3 years'
                elif tenure_months < 60:
                    tenure_group = '3-5 years'
                else:
                    tenure_group = '5+ years'
                
                # Age groupings (based on birth date in employee record)
                birth_date = datetime.strptime(employee.get('birth_date', '1980-01-01'), '%Y-%m-%d').date()
                age_years = (survey_date - birth_date).days // 365
                if age_years < 25:
                    age_group = 'Under 25'
                elif age_years < 35:
                    age_group = '25-34'
                elif age_years < 45:
                    age_group = '35-44'
                elif age_years < 55:
                    age_group = '45-54'
                else:
                    age_group = '55+'
                
                # Role level grouping
                role_level = {
                    'ENTRY': 'Individual Contributor',
                    'JUNIOR': 'Individual Contributor', 
                    'SENIOR': 'Senior Individual Contributor',
                    'LEAD': 'Team Lead',
                    'MANAGER': 'Management',
                    'DIRECTOR': 'Senior Management',
                    'EXECUTIVE': 'Executive'
                }.get(job_level, 'Other')
                
                # Generate realistic satisfaction ratings (1-5 scale, weighted towards positive)
                rating_weights = [2, 5, 15, 40, 38]  # Weighted towards 4-5
                overall_satisfaction = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
                work_life_balance = random.choices([1, 2, 3, 4, 5], weights=[3, 8, 20, 42, 27])[0]
                compensation_satisfaction = random.choices([1, 2, 3, 4, 5], weights=[5, 12, 25, 35, 23])[0]
                career_development = random.choices([1, 2, 3, 4, 5], weights=[4, 10, 22, 38, 26])[0]
                management_effectiveness = random.choices([1, 2, 3, 4, 5], weights=[3, 7, 18, 42, 30])[0]
                company_culture = random.choices([1, 2, 3, 4, 5], weights=[2, 6, 17, 43, 32])[0]
                
                # Generate text responses
                likes_most_options = [
                    "Great team collaboration and supportive colleagues",
                    "Flexible working arrangements and work-life balance",
                    "Opportunities for professional development and growth",
                    "Company culture and values alignment",
                    "Challenging and meaningful work projects",
                    "Competitive compensation and benefits package",
                    "Strong leadership and clear direction",
                    "Innovation and forward-thinking approach"
                ]
                
                improvement_suggestions_options = [
                    "More opportunities for career advancement",
                    "Better communication between departments",
                    "Enhanced training and development programs",
                    "Improved work-life balance initiatives",
                    "More competitive compensation packages",
                    "Better recognition and rewards programs",
                    "Upgraded office facilities and technology",
                    "More flexible working arrangements",
                    "",  # Some don't provide suggestions
                    ""   # Some don't provide suggestions
                ]
                
                additional_comments_options = [
                    "Overall very satisfied with my role and the company",
                    "Looking forward to continued growth and development",
                    "Appreciate the supportive management team",
                    "Happy with the company direction and vision",
                    "",  # Many skip additional comments
                    "",
                    "",
                    ""
                ]
                
                response = {
                    'response_id': f"RESP_{response_id:08d}",
                    'survey_id': survey['survey_id'],
                    'employee_id': None if survey['is_anonymous'] else employee['employee_id'],  # Fixed: populate employee_id
                    'response_date': (survey_date + timedelta(days=random.randint(0, 15))).strftime('%Y-%m-%d %H:%M:%S'),
                    
                    # Fixed: Add all missing satisfaction rating fields
                    'overall_satisfaction': overall_satisfaction,
                    'work_life_balance_rating': work_life_balance,
                    'compensation_satisfaction': compensation_satisfaction,
                    'career_development_rating': career_development,
                    'management_effectiveness': management_effectiveness,
                    'company_culture_rating': company_culture,
                    
                    # Fixed: Add missing text response fields
                    'likes_most': random.choice(likes_most_options),
                    'improvement_suggestions': random.choice(improvement_suggestions_options),
                    'additional_comments': random.choice(additional_comments_options),
                    
                    # Fixed: Add missing demographic grouping fields
                    'department_group': department_group,
                    'tenure_group': tenure_group,
                    'age_group': age_group,
                    'role_level': role_level,
                    
                    # Privacy and consent fields
                    'consent_given': True,
                    'anonymization_level': 'FULL' if survey['is_anonymous'] else 'PARTIAL',
                    
                    'created_date': survey['launch_date'] + ' 00:00:00'
                }
                responses.append(response)
                response_id += 1
        
        print(f"Generated {len(surveys)} surveys and {len(responses)} survey responses")
        return surveys, responses
    
    def _get_random_cost_center(self, entity_id: str) -> str:
        """Get a random cost center for the given entity."""
        entity_cost_centers = [cc for cc in self.cost_centers if cc.get('entity_id') == entity_id]
        return random.choice(entity_cost_centers)['cost_center_id'] if entity_cost_centers else ''
    
    def _get_country_from_entity(self, entity_id: str) -> str:
        """Extract country code from entity ID."""
        for entity in self.finance_entities:
            if entity['entity_id'] == entity_id:
                return entity['country_code']
        return 'NL'  # Default
    
    def _get_skills_for_family(self, job_family: str) -> List[str]:
        """Get relevant skills for job family."""
        skills_map = {
            'Executive': ['Strategic Planning', 'Leadership', 'P&L Management'],
            'Finance': ['Financial Analysis', 'Excel', 'SAP', 'IFRS'],
            'IT': ['Python', 'SQL', 'Cloud Computing', 'Agile'],
            'Marketing': ['Digital Marketing', 'Social Media', 'Analytics'],
            'Sales': ['Customer Relations', 'Negotiation', 'CRM'],
            'HR': ['Employee Relations', 'Recruitment', 'HRIS'],
            'Operations': ['Process Improvement', 'Logistics', 'Quality Control'],
            'Retail': ['Customer Service', 'Visual Merchandising', 'POS Systems']
        }
        return skills_map.get(job_family, ['Communication', 'Teamwork', 'Problem Solving'])
    
    def _get_education_requirements(self, level: str) -> str:
        """Get education requirements by level."""
        requirements = {
            'ENTRY': 'High School Diploma or equivalent',
            'JUNIOR': "Bachelor's degree preferred",
            'SENIOR': "Bachelor's degree required",
            'LEAD': "Bachelor's degree, relevant certifications preferred",
            'MANAGER': "Bachelor's degree required, MBA preferred",
            'DIRECTOR': "Advanced degree (MBA/Masters) required",
            'EXECUTIVE': "Advanced degree required, extensive experience"
        }
        return requirements.get(level, "Bachelor's degree preferred")
    
    def _get_leave_reason(self, leave_type: str) -> str:
        """Generate appropriate leave reason."""
        reasons = {
            'ANNUAL': ['Family vacation', 'Personal time off', 'Rest and relaxation', 'Wedding anniversary'],
            'SICK': ['Flu symptoms', 'Medical appointment', 'Back pain', 'Dental procedure'],
            'PERSONAL': ['Family emergency', 'Moving house', 'Personal matters', 'Bereavement'],
            'MATERNITY': ['Maternity leave', 'Childbirth recovery'],
            'PATERNITY': ['Paternity leave', 'Newborn care']
        }
        return random.choice(reasons.get(leave_type, ['Personal reasons']))
    
    def _get_performance_comment(self, rating: str, is_manager: bool) -> str:
        """Generate performance review comments."""
        if is_manager:
            comments = {
                'EXCEEDS_EXPECTATIONS': [
                    "Consistently delivers exceptional results and goes above and beyond expectations.",
                    "Outstanding performer who serves as a role model for the team.",
                    "Demonstrates exceptional leadership qualities and drives team success."
                ],
                'MEETS_EXPECTATIONS': [
                    "Solid performer who consistently meets objectives and contributes positively to the team.",
                    "Reliable employee who delivers quality work and collaborates well with others.",
                    "Good performance with room for continued growth and development."
                ],
                'PARTIALLY_MEETS': [
                    "Shows potential but needs to focus on meeting core objectives more consistently.",
                    "Performance is acceptable but there are areas that require improvement.",
                    "With additional support and development, can achieve higher performance levels."
                ]
            }
        else:
            comments = {
                'EXCEEDS_EXPECTATIONS': [
                    "I'm proud of my achievements this year and enjoy the challenging work.",
                    "Feel well-supported by management and excited about future opportunities.",
                    "Grateful for the recognition and looking forward to taking on more responsibility."
                ],
                'MEETS_EXPECTATIONS': [
                    "Satisfied with my performance and appreciate the feedback for improvement.",
                    "Feel I've grown in my role and am ready for new challenges.",
                    "Happy with my contribution to the team and company success."
                ],
                'PARTIALLY_MEETS': [
                    "Understand the areas for improvement and committed to developing these skills.",
                    "Appreciate the constructive feedback and support for my development.",
                    "Ready to work on the identified areas and improve my performance."
                ]
            }
        
        return random.choice(comments.get(rating, ["Good overall performance with room for growth."]))
    
    def _get_development_areas(self) -> str:
        """Generate development areas."""
        areas = [
            "Leadership and team management skills",
            "Strategic thinking and planning",
            "Technical skills advancement",
            "Communication and presentation skills",
            "Customer relationship management",
            "Cross-functional collaboration",
            "Digital transformation and technology adoption"
        ]
        return random.choice(areas)
    
    def _get_development_plan(self) -> str:
        """Generate development plan."""
        plans = [
            "Enroll in leadership development program and seek mentoring opportunities.",
            "Attend relevant conferences and pursue additional certifications.",
            "Take on stretch assignments and cross-functional projects.",
            "Participate in public speaking workshops and presentation training.",
            "Shadow senior leaders and attend strategic planning sessions.",
            "Complete advanced technical training and gain new certifications."
        ]
        return random.choice(plans)
    
    def write_csv_file(self, filename: str, data: List[Dict], fieldnames: List[str] = None):
        """Write data to compressed CSV file."""
        if not data:
            print(f"⚠️ No data to write for {filename}")
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        # Ensure filename has .gz extension
        if not filename.endswith('.gz'):
            filename = filename.replace('.csv', '.csv.gz')
        
        filepath = os.path.join(self.output_dir, filename)
        
        with gzip.open(filepath, 'wt', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        # Calculate file size
        file_size = os.path.getsize(filepath)
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size} bytes"
        
        print(f"  📄 {filename} ({len(data):,} records, {size_str})")
        
        self.csv_files[filename] = {
            'records': len(data),
            'size': file_size,
            'path': filepath
        }
    
    def generate_all_hr_data(self):
        """Generate all HR system data."""
        print("\n🚀 Generating complete EuroStyle HR system data...")
        
        # Load external data for referential integrity
        self.load_external_data()
        
        # 1. Organizational structure
        print("\n1. Organizational Structure")
        departments = self.generate_departments()
        self.write_csv_file('eurostyle_hr.departments.csv', departments)
        
        positions = self.generate_job_positions()
        self.write_csv_file('eurostyle_hr.job_positions.csv', positions)
        
        # 2. Employee master data
        print("\n2. Employee Master Data")
        employees = self.generate_employees()
        self.write_csv_file('eurostyle_hr.employees.csv', employees)
        
        # 3. Employment contracts and compensation
        print("\n3. Employment Contracts & Compensation")
        contracts = self.generate_employment_contracts()
        self.write_csv_file('eurostyle_hr.employment_contracts.csv', contracts)
        
        compensation = self.generate_compensation_history()
        self.write_csv_file('eurostyle_hr.compensation_history.csv', compensation)
        
        # 4. Leave management
        print("\n4. Leave Management")
        leave_requests, leave_balances = self.generate_leave_requests()
        self.write_csv_file('eurostyle_hr.leave_requests.csv', leave_requests)
        self.write_csv_file('eurostyle_hr.leave_balances.csv', leave_balances)
        
        # 5. Performance management
        print("\n5. Performance Management")
        performance_cycles, performance_reviews = self.generate_performance_data()
        self.write_csv_file('eurostyle_hr.performance_cycles.csv', performance_cycles)
        self.write_csv_file('eurostyle_hr.performance_reviews.csv', performance_reviews)
        
        # 6. Training and development
        print("\n6. Training & Development")
        training_programs, employee_training = self.generate_training_data()
        self.write_csv_file('eurostyle_hr.training_programs.csv', training_programs)
        self.write_csv_file('eurostyle_hr.employee_training.csv', employee_training)
        
        # 7. Employee surveys
        print("\n7. Employee Surveys")
        surveys, survey_responses = self.generate_surveys_and_responses()
        self.write_csv_file('eurostyle_hr.employee_surveys.csv', surveys)
        self.write_csv_file('eurostyle_hr.survey_responses.csv', survey_responses)
        
        # Summary
        print(f"\n✅ Complete HR data generation finished!")
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
    """Main function to generate EuroStyle HR data."""
    print("👥 EuroStyle Fashion - HR Data Generator")
    print("========================================")
    
    try:
        generator = EuroStyleHRGenerator()
        generator.generate_all_hr_data()
        
        print("\n🎉 HR data generation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during HR data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Initialize faker instance for the main function
    faker = Faker()
    main()