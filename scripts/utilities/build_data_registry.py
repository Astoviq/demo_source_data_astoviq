#!/usr/bin/env python3
"""
Build EuroStyle Data Registry
============================

This script builds the central data registry from existing operational data
and creates cross-system mappings for webshop and finance integration.

Usage:
    python3 build_data_registry.py
"""

import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from data_registry import DataRegistry

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to build the registry."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🏗️ Building EuroStyle Data Registry...")
    logger.info("=" * 50)
    
    # Create registry with proper path to data-generator output
    registry = DataRegistry("../data-generator/generated_data")
    
    try:
        # Load operational data and build mappings
        if registry.load_operational_data():
            logger.info("✅ Registry built successfully!")
            
            # Display registry statistics
            logger.info("")
            logger.info("📊 Registry Statistics:")
            logger.info("-" * 30)
            logger.info(f"Customers: {len(registry.get_customer_ids()):,}")
            logger.info(f"Products: {len(registry.get_product_ids()):,}")
            logger.info(f"Orders: {len(registry.get_order_ids()):,}")
            logger.info(f"Total Sessions: {len(registry.get_session_mappings()):,}")
            logger.info(f"Converting Sessions: {len(registry.get_converting_sessions()):,}")
            logger.info(f"Non-converting Sessions: {len(registry.get_non_converting_sessions()):,}")
            
            # Display key metrics
            converting_sessions = len(registry.get_converting_sessions())
            total_sessions = len(registry.get_session_mappings())
            conversion_rate = (converting_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            total_revenue = sum(session['order_value_eur'] 
                              for session in registry.get_session_mappings().values())
            
            logger.info("")
            logger.info("🎯 Target Metrics:")
            logger.info("-" * 20)
            logger.info(f"Conversion Rate: {conversion_rate:.2f}%")
            logger.info(f"Total Revenue: €{total_revenue:,.2f}")
            logger.info(f"Target Revenue: €{registry.get_target_metrics()['total_revenue_eur']:,.2f}")
            
            # Validate registry
            logger.info("")
            logger.info("🔍 Validating Registry...")
            logger.info("-" * 25)
            
            if registry.validate_registry():
                logger.info("✅ Registry validation PASSED!")
            else:
                logger.error("❌ Registry validation FAILED!")
                return False
                
            logger.info("")
            logger.info("🎉 Registry build completed successfully!")
            logger.info(f"Registry files saved to: {registry.registry_path}")
            
            # Show file locations
            logger.info("")
            logger.info("📁 Generated Registry Files:")
            logger.info("-" * 30)
            for file_path in registry.registry_path.glob("*.json"):
                logger.info(f"  {file_path.name}")
                
            return True
            
        else:
            logger.error("❌ Failed to load operational data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Registry build failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)