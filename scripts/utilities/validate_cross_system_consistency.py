#!/usr/bin/env python3
"""
EuroStyle Cross-System Consistency Validation
=============================================

Validates that the integrated data generation system produces consistent results
across Operations, Webshop, and Finance systems by running comprehensive checks.
"""

import csv
import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import sys
import logging

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class CrossSystemValidator:
    """Validates consistency across all EuroStyle systems."""
    
    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger(__name__)
        
        # Data paths
        self.operational_path = Path("../data-generator/generated_data")
        self.webshop_path = Path("../generated_data")
        self.finance_path = Path("../generated_data")
        self.registry_path = self.operational_path / "registry"
        
        # Data containers
        self.operational_data = {}
        self.webshop_data = {}
        self.finance_data = {}
        self.registry_data = {}
        
        # Validation results
        self.validation_results = []
        
    def load_all_data(self) -> bool:
        """Load data from all systems."""
        self.logger.info("Loading data from all systems...")
        
        try:
            # Load operational data
            self._load_operational_data()
            
            # Load webshop data (if generated)
            self._load_webshop_data()
            
            # Load finance data
            self._load_finance_data()
            
            # Load registry data
            self._load_registry_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _load_operational_data(self):
        """Load operational system data."""
        # Load customers
        with open(self.operational_path / "customers.csv", 'r') as f:
            reader = csv.DictReader(f)
            self.operational_data['customers'] = {row['customer_id']: row for row in reader}
            
        # Load orders (unique orders only)
        orders = {}
        with open(self.operational_path / "orders.csv", 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['order_id'] not in orders:
                    orders[row['order_id']] = row
        self.operational_data['orders'] = orders
        
        # Load products
        with open(self.operational_path / "products.csv", 'r') as f:
            reader = csv.DictReader(f)
            self.operational_data['products'] = {row['product_id']: row for row in reader}
            
        self.logger.info(f"Loaded operational data: {len(self.operational_data['customers'])} customers, "
                        f"{len(self.operational_data['orders'])} orders, {len(self.operational_data['products'])} products")
    
    def _load_webshop_data(self):
        """Load webshop system data."""
        # Check if webshop data exists
        webshop_sessions_file = self.webshop_path / "eurostyle_webshop.web_sessions.csv"
        if webshop_sessions_file.exists():
            with open(webshop_sessions_file, 'r') as f:
                reader = csv.DictReader(f)
                self.webshop_data['sessions'] = {row['session_id']: row for row in reader}
            self.logger.info(f"Loaded webshop data: {len(self.webshop_data['sessions'])} sessions")
        else:
            self.webshop_data['sessions'] = {}
            self.logger.warning("Webshop sessions data not found")
    
    def _load_finance_data(self):
        """Load finance system data."""
        # Load GL journal lines
        with open(self.finance_path / "eurostyle_finance.gl_journal_lines.csv", 'r') as f:
            reader = csv.DictReader(f)
            self.finance_data['gl_lines'] = list(reader)
            
        # Load GL journal headers
        with open(self.finance_path / "eurostyle_finance.gl_journal_headers.csv", 'r') as f:
            reader = csv.DictReader(f)
            self.finance_data['gl_headers'] = {row['journal_id']: row for row in reader}
            
        self.logger.info(f"Loaded finance data: {len(self.finance_data['gl_lines'])} GL lines, "
                        f"{len(self.finance_data['gl_headers'])} GL headers")
    
    def _load_registry_data(self):
        """Load registry data."""
        if self.registry_path.exists():
            # Load cross-references
            with open(self.registry_path / "cross_refs.json", 'r') as f:
                self.registry_data['cross_refs'] = json.load(f)
                
            # Load time configuration
            with open(self.registry_path / "time_config.json", 'r') as f:
                self.registry_data['time_config'] = json.load(f)
                
            self.logger.info("Loaded registry data")
        else:
            self.logger.warning("Registry data not found")
    
    def validate_revenue_reconciliation(self) -> bool:
        """Validate that operational revenue matches finance GL revenue."""
        self.logger.info("🔍 Validating revenue reconciliation...")
        
        # Calculate operational revenue
        operational_revenue = sum(
            float(order.get('total_amount_eur', order.get('total_amount_local', 0)))
            for order in self.operational_data['orders'].values()
        )
        
        # Calculate finance GL revenue (credit entries in revenue accounts)
        finance_revenue = sum(
            Decimal(line['credit_amount'])
            for line in self.finance_data['gl_lines']
            if line['account_id'] == 'ACC_4100'  # Revenue account
        )
        
        variance = abs(operational_revenue - float(finance_revenue))
        variance_percentage = (variance / operational_revenue * 100) if operational_revenue > 0 else 0
        
        self.logger.info(f"  Operational Revenue: €{operational_revenue:,.2f}")
        self.logger.info(f"  Finance GL Revenue:  €{finance_revenue:,.2f}")
        self.logger.info(f"  Variance:           €{variance:.2f} ({variance_percentage:.3f}%)")
        
        # Validation passes if variance is less than €10 or 0.001%
        is_valid = variance < 10.0 or variance_percentage < 0.001
        
        result = {
            'test': 'Revenue Reconciliation',
            'status': 'PASS' if is_valid else 'FAIL',
            'operational_revenue': operational_revenue,
            'finance_revenue': float(finance_revenue),
            'variance': variance,
            'variance_percentage': variance_percentage
        }
        
        self.validation_results.append(result)
        return is_valid
    
    def validate_customer_consistency(self) -> bool:
        """Validate customer ID consistency across systems."""
        self.logger.info("🔍 Validating customer consistency...")
        
        # Get customer IDs from each system
        operational_customers = set(self.operational_data['customers'].keys())
        
        # Check finance GL customer references
        finance_customers = set(
            line['customer_id'] 
            for line in self.finance_data['gl_lines'] 
            if line['customer_id']
        )
        
        # Check webshop customer references
        webshop_customers = set(
            session['customer_id']
            for session in self.webshop_data['sessions'].values()
            if session['customer_id']
        ) if self.webshop_data['sessions'] else set()
        
        # Find orphaned references
        orphaned_finance = finance_customers - operational_customers
        orphaned_webshop = webshop_customers - operational_customers
        
        self.logger.info(f"  Operational customers: {len(operational_customers):,}")
        self.logger.info(f"  Finance customer refs: {len(finance_customers):,}")
        self.logger.info(f"  Webshop customer refs: {len(webshop_customers):,}")
        self.logger.info(f"  Orphaned finance refs: {len(orphaned_finance)}")
        self.logger.info(f"  Orphaned webshop refs: {len(orphaned_webshop)}")
        
        is_valid = len(orphaned_finance) == 0 and len(orphaned_webshop) == 0
        
        result = {
            'test': 'Customer Consistency',
            'status': 'PASS' if is_valid else 'FAIL',
            'operational_customers': len(operational_customers),
            'finance_customer_refs': len(finance_customers),
            'webshop_customer_refs': len(webshop_customers),
            'orphaned_finance': len(orphaned_finance),
            'orphaned_webshop': len(orphaned_webshop)
        }
        
        self.validation_results.append(result)
        return is_valid
    
    def validate_order_references(self) -> bool:
        """Validate order references between operations and finance."""
        self.logger.info("🔍 Validating order references...")
        
        # Get order IDs from operational system
        operational_orders = set(self.operational_data['orders'].keys())
        
        # Get order references from finance GL
        finance_order_refs = set(
            line['reference_1']
            for line in self.finance_data['gl_lines']
            if line['reference_1'] and line['reference_1'].startswith('ORD_')
        )
        
        # Check for orphaned references
        orphaned_finance_orders = finance_order_refs - operational_orders
        missing_finance_refs = operational_orders - finance_order_refs
        
        self.logger.info(f"  Operational orders: {len(operational_orders):,}")
        self.logger.info(f"  Finance order refs: {len(finance_order_refs):,}")
        self.logger.info(f"  Orphaned finance refs: {len(orphaned_finance_orders)}")
        self.logger.info(f"  Missing finance refs: {len(missing_finance_refs)}")
        
        # Validation passes if all order references are valid and no orders are missing
        is_valid = len(orphaned_finance_orders) == 0 and len(missing_finance_refs) == 0
        
        result = {
            'test': 'Order References',
            'status': 'PASS' if is_valid else 'FAIL',
            'operational_orders': len(operational_orders),
            'finance_order_refs': len(finance_order_refs),
            'orphaned_finance_refs': len(orphaned_finance_orders),
            'missing_finance_refs': len(missing_finance_refs)
        }
        
        self.validation_results.append(result)
        return is_valid
    
    def validate_time_period_consistency(self) -> bool:
        """Validate time period consistency across systems."""
        self.logger.info("🔍 Validating time period consistency...")
        
        # Get date ranges from each system
        operational_dates = [order['order_date'] for order in self.operational_data['orders'].values()]
        op_min, op_max = min(operational_dates), max(operational_dates)
        
        finance_dates = [header['journal_date'] for header in self.finance_data['gl_headers'].values()]
        fin_min, fin_max = min(finance_dates), max(finance_dates)
        
        # Check webshop if available
        if self.webshop_data['sessions']:
            webshop_dates = [session['session_date'] for session in self.webshop_data['sessions'].values()]
            web_min, web_max = min(webshop_dates), max(webshop_dates)
        else:
            web_min, web_max = op_min, op_max  # Assume aligned
        
        self.logger.info(f"  Operations: {op_min} to {op_max}")
        self.logger.info(f"  Finance:    {fin_min} to {fin_max}")
        self.logger.info(f"  Webshop:    {web_min} to {web_max}")
        
        # Check if periods are aligned
        periods_aligned = (op_min == fin_min == web_min) and (op_max == fin_max == web_max)
        
        self.logger.info(f"  Periods aligned: {periods_aligned}")
        
        result = {
            'test': 'Time Period Consistency',
            'status': 'PASS' if periods_aligned else 'FAIL',
            'operations_range': f"{op_min} to {op_max}",
            'finance_range': f"{fin_min} to {fin_max}",
            'webshop_range': f"{web_min} to {web_max}",
            'periods_aligned': periods_aligned
        }
        
        self.validation_results.append(result)
        return periods_aligned
    
    def validate_conversion_rates(self) -> bool:
        """Validate realistic webshop conversion rates."""
        self.logger.info("🔍 Validating webshop conversion rates...")
        
        if not self.webshop_data['sessions']:
            self.logger.warning("Webshop data not available, skipping conversion rate validation")
            result = {
                'test': 'Conversion Rates',
                'status': 'SKIP',
                'reason': 'No webshop data available'
            }
            self.validation_results.append(result)
            return True
        
        # Count converting and total sessions
        converting_sessions = sum(
            1 for session in self.webshop_data['sessions'].values()
            if session.get('converted', 'False').lower() == 'true'
        )
        
        total_sessions = len(self.webshop_data['sessions'])
        conversion_rate = (converting_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Count online orders for comparison
        online_channels = ['online', 'mobile_app', 'social_commerce']
        online_orders = sum(
            1 for order in self.operational_data['orders'].values()
            if order.get('order_channel', order.get('channel', 'online')) in online_channels
        )
        
        self.logger.info(f"  Total sessions: {total_sessions:,}")
        self.logger.info(f"  Converting sessions: {converting_sessions:,}")
        self.logger.info(f"  Conversion rate: {conversion_rate:.2f}%")
        self.logger.info(f"  Online orders: {online_orders:,}")
        
        # Realistic fashion e-commerce conversion rate: 2-4%
        is_realistic = 2.0 <= conversion_rate <= 4.0
        
        result = {
            'test': 'Conversion Rates',
            'status': 'PASS' if is_realistic else 'FAIL',
            'total_sessions': total_sessions,
            'converting_sessions': converting_sessions,
            'conversion_rate': conversion_rate,
            'online_orders': online_orders,
            'is_realistic': is_realistic
        }
        
        self.validation_results.append(result)
        return is_realistic
    
    def generate_validation_report(self) -> str:
        """Generate a comprehensive validation report."""
        self.logger.info("📄 Generating validation report...")
        
        report = []
        report.append("# EuroStyle Cross-System Consistency Validation Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for r in self.validation_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.validation_results if r['status'] == 'FAIL')
        skipped_tests = sum(1 for r in self.validation_results if r['status'] == 'SKIP')
        
        report.append("## Summary")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Passed**: {passed_tests}")
        report.append(f"- **Failed**: {failed_tests}")
        report.append(f"- **Skipped**: {skipped_tests}")
        report.append(f"- **Success Rate**: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "- **Success Rate**: N/A")
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        report.append("")
        
        for result in self.validation_results:
            status_icon = "✅" if result['status'] == 'PASS' else ("❌" if result['status'] == 'FAIL' else "⏭️")
            report.append(f"### {status_icon} {result['test']} - {result['status']}")
            
            for key, value in result.items():
                if key not in ['test', 'status']:
                    if isinstance(value, float):
                        if 'percentage' in key:
                            report.append(f"- **{key.replace('_', ' ').title()}**: {value:.3f}%")
                        else:
                            report.append(f"- **{key.replace('_', ' ').title()}**: {value:,.2f}")
                    elif isinstance(value, int):
                        report.append(f"- **{key.replace('_', ' ').title()}**: {value:,}")
                    else:
                        report.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if failed_tests == 0:
            report.append("🎉 **All critical validations passed!** The cross-system integration is working correctly:")
            report.append("- Revenue reconciliation between Operations and Finance is perfect")
            report.append("- Customer and order references are consistent across systems")
            report.append("- Time periods are properly synchronized")
            report.append("- Conversion rates are realistic for fashion e-commerce")
        else:
            report.append("⚠️ **Issues detected:** Please address the following:")
            for result in self.validation_results:
                if result['status'] == 'FAIL':
                    report.append(f"- **{result['test']}**: Review and fix the reported inconsistencies")
        
        return "\n".join(report)
    
    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        self.logger.info("🚀 Starting cross-system consistency validation...")
        self.logger.info("=" * 60)
        
        if not self.load_all_data():
            return False
        
        # Run validation checks
        validations = [
            self.validate_revenue_reconciliation,
            self.validate_customer_consistency,
            self.validate_order_references,
            self.validate_time_period_consistency,
            self.validate_conversion_rates
        ]
        
        all_passed = True
        for validation in validations:
            try:
                passed = validation()
                if not passed:
                    all_passed = False
            except Exception as e:
                self.logger.error(f"Validation failed with error: {str(e)}")
                all_passed = False
            self.logger.info("")
        
        # Generate and save report
        report = self.generate_validation_report()
        
        report_path = Path("../generated_data/cross_system_validation_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        self.logger.info(f"📄 Validation report saved to: {report_path}")
        
        return all_passed

def main():
    """Main function."""
    logger = setup_logging()
    
    logger.info("🔍 EuroStyle Cross-System Consistency Validation")
    logger.info("=" * 55)
    
    validator = CrossSystemValidator()
    
    try:
        success = validator.run_all_validations()
        
        if success:
            logger.info("🎉 All validations passed! Cross-system consistency achieved.")
            return True
        else:
            logger.error("❌ Some validations failed. Check the report for details.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Validation process failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)