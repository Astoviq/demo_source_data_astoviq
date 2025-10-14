#!/usr/bin/env python3
"""
EuroStyle Cross-System Data Registry
===================================

Central registry system that coordinates data generation across Operations, 
Webshop, and Finance systems to ensure referential integrity and consistency.

This registry:
- Manages shared customer, product, order, and session IDs
- Coordinates time periods across all systems
- Maintains cross-system reference mappings
- Ensures realistic conversion rates and revenue reconciliation

Usage:
    from data_registry import DataRegistry
    
    registry = DataRegistry()
    registry.load_operational_data()
    customer_ids = registry.get_customer_ids()
    order_mappings = registry.get_order_session_mappings()
"""

import json
import csv
import os
import random
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import logging

class DataRegistry:
    """Central registry for cross-system data coordination."""
    
    def __init__(self, base_path: str = "../generated_data"):
        """Initialize the data registry."""
        self.base_path = Path(base_path)
        self.registry_path = self.base_path / "registry"
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        # Registry data containers
        self.customers = {}
        self.products = {}
        self.orders = {}
        self.campaigns = {}
        self.stores = {}
        
        # Cross-system mappings
        self.session_order_mappings = {}
        self.customer_segments = {}
        self.channel_preferences = {}
        
        # Time configuration
        self.time_config = {
            "unified_start_date": "2020-01-01",
            "unified_end_date": "2025-10-10",
            "current_date": "2025-10-10"
        }
        
        # Target metrics
        self.target_metrics = {
            "total_orders": 50000,
            "total_revenue_eur": 9340000,  # €9.34M
            "online_conversion_rate": 0.025,  # 2.5%
            "online_order_percentage": 0.62,  # 62% of orders are online
            "total_webshop_sessions": 180000,  # Target sessions for realistic conversion
        }
        
        self.logger = logging.getLogger(__name__)
        
    def load_operational_data(self) -> bool:
        """Load operational data and build registry."""
        self.logger.info("Loading operational data into registry...")
        
        try:
            # Load customers
            customers_file = self.base_path / "customers.csv"
            if customers_file.exists():
                with open(customers_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.customers[row['customer_id']] = {
                            'customer_id': row['customer_id'],
                            'country_code': row['country_code'],
                            'channel_preference': row.get('preferred_channel', 'online'),
                            'registration_date': row.get('registration_date'),
                            'marketing_opt_in': row.get('marketing_opt_in', 'false').lower() == 'true'
                        }
                self.logger.info(f"Loaded {len(self.customers)} customers")
                
            # Load products
            products_file = self.base_path / "products.csv"
            if products_file.exists():
                with open(products_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.products[row['product_id']] = {
                            'product_id': row['product_id'],
                            'product_name': row['product_name'],
                            'category': row.get('category_l1', row.get('category', '')),
                            'price_eur': float(row.get('price_eur', 0)),
                            'is_active': row.get('is_active', 'true').lower() == 'true'
                        }
                self.logger.info(f"Loaded {len(self.products)} products")
                
            # Load orders
            orders_file = self.base_path / "orders.csv"
            if orders_file.exists():
                with open(orders_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.orders[row['order_id']] = {
                            'order_id': row['order_id'],
                            'customer_id': row['customer_id'],
                            'order_date': row['order_date'],
                            'order_total_eur': float(row.get('total_amount_eur', row.get('total_amount_local', row.get('total_amount', 0)))),
                            'channel': row.get('order_channel', row.get('channel', 'online')),
                            'store_id': row.get('store_id', ''),
                            'campaign_id': row.get('campaign_code', row.get('campaign_id', '')),
                            'country_code': row.get('country_code', '')
                        }
                self.logger.info(f"Loaded {len(self.orders)} orders")
                
            # Load campaigns  
            campaigns_file = self.base_path / "campaigns.csv"
            if campaigns_file.exists():
                with open(campaigns_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.campaigns[row['campaign_id']] = {
                            'campaign_id': row['campaign_id'],
                            'campaign_name': row['campaign_name'],
                            'start_date': row.get('start_date'),
                            'end_date': row.get('end_date'),
                            'channel': row.get('channel', 'digital')
                        }
                self.logger.info(f"Loaded {len(self.campaigns)} campaigns")
                
            # Load stores
            stores_file = self.base_path / "stores.csv" 
            if stores_file.exists():
                with open(stores_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.stores[row['store_id']] = {
                            'store_id': row['store_id'],
                            'store_name': row['store_name'],
                            'country_code': row['country_code'],
                            'city': row.get('city', ''),
                            'is_active': row.get('is_active', 'true').lower() == 'true'
                        }
                self.logger.info(f"Loaded {len(self.stores)} stores")
                
            # Build cross-system mappings
            self._build_cross_system_mappings()
            
            # Save registry files
            self._save_registry()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading operational data: {str(e)}")
            return False
    
    def _build_cross_system_mappings(self):
        """Build cross-system reference mappings."""
        self.logger.info("Building cross-system mappings...")
        
        # Calculate online orders - include all digital channels
        online_channels = ['online', 'mobile_app', 'social_commerce']
        online_orders = [order for order in self.orders.values() 
                        if order['channel'] in online_channels]
        
        target_online_orders = int(len(self.orders) * self.target_metrics['online_order_percentage'])
        
        if len(online_orders) < target_online_orders:
            self.logger.warning(f"Only {len(online_orders)} online orders found, need {target_online_orders}")
        
        # Create session-to-order mappings for online orders
        # Each online order gets exactly one converting session
        converting_sessions = []
        session_counter = 1
        
        for order in online_orders:
            session_id = f"SESS_{order['order_date'][:4]}_{session_counter:06d}"
            session_counter += 1
            
            # Get country code from customer data
            customer_country = self.customers.get(order['customer_id'], {}).get('country_code', 'NL')
            
            self.session_order_mappings[session_id] = {
                'session_id': session_id,
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'country_code': customer_country,
                'order_value_eur': order['order_total_eur'],
                'conversion_type': 'purchase',
                'session_date': order['order_date']
            }
            converting_sessions.append(session_id)
        
        # Calculate non-converting sessions needed for target conversion rate
        total_target_sessions = int(len(converting_sessions) / self.target_metrics['online_conversion_rate'])
        non_converting_sessions_needed = total_target_sessions - len(converting_sessions)
        
        self.logger.info(f"Creating {len(converting_sessions)} converting sessions")
        self.logger.info(f"Creating {non_converting_sessions_needed} non-converting sessions")
        self.logger.info(f"Target conversion rate: {self.target_metrics['online_conversion_rate']*100:.1f}%")
        
        # Create non-converting sessions
        countries = ['NL', 'DE', 'FR', 'BE', 'LU']
        country_weights = [0.20, 0.35, 0.25, 0.15, 0.05]
        
        for i in range(non_converting_sessions_needed):
            # Spread sessions across the time period
            days_span = (datetime.strptime(self.time_config['unified_end_date'], '%Y-%m-%d') - 
                        datetime.strptime(self.time_config['unified_start_date'], '%Y-%m-%d')).days
            
            session_date = datetime.strptime(self.time_config['unified_start_date'], '%Y-%m-%d') + \
                          timedelta(days=random.randint(0, days_span))
            
            session_id = f"SESS_{session_date.year}_{session_counter:06d}"
            session_counter += 1
            
            # Randomly assign customer (30% guest sessions)
            customer_id = random.choice(list(self.customers.keys())) if random.random() > 0.3 else ''
            country_code = random.choices(countries, weights=country_weights)[0]
            
            self.session_order_mappings[session_id] = {
                'session_id': session_id,
                'order_id': '',  # No order for non-converting session
                'customer_id': customer_id,
                'country_code': country_code,
                'order_value_eur': 0,
                'conversion_type': 'browse',
                'session_date': session_date.strftime('%Y-%m-%d')
            }
        
        self.logger.info(f"Built {len(self.session_order_mappings)} total session mappings")
    
    def _save_registry(self):
        """Save registry data to files."""
        self.logger.info("Saving registry files...")
        
        # Save shared IDs
        with open(self.registry_path / "customers.json", 'w') as f:
            json.dump(list(self.customers.keys()), f, indent=2)
            
        with open(self.registry_path / "products.json", 'w') as f:
            json.dump(list(self.products.keys()), f, indent=2)
            
        with open(self.registry_path / "orders.json", 'w') as f:
            json.dump(list(self.orders.keys()), f, indent=2)
            
        # Save session mappings
        with open(self.registry_path / "session_mappings.json", 'w') as f:
            json.dump(self.session_order_mappings, f, indent=2)
            
        # Save time configuration
        with open(self.registry_path / "time_config.json", 'w') as f:
            json.dump(self.time_config, f, indent=2)
            
        # Save cross-system references
        cross_refs = {
            'target_metrics': self.target_metrics,
            'online_orders': len([o for o in self.orders.values() if o['channel'] == 'online']),
            'total_orders': len(self.orders),
            'total_revenue_eur': sum(o['order_total_eur'] for o in self.orders.values()),
            'converting_sessions': len([s for s in self.session_order_mappings.values() if s['order_id'] != '']),
            'total_sessions': len(self.session_order_mappings)
        }
        
        with open(self.registry_path / "cross_refs.json", 'w') as f:
            json.dump(cross_refs, f, indent=2)
            
        self.logger.info(f"Registry saved to {self.registry_path}")
    
    def get_customer_ids(self) -> List[str]:
        """Get list of all customer IDs."""
        return list(self.customers.keys())
    
    def get_product_ids(self) -> List[str]:
        """Get list of all product IDs."""
        return list(self.products.keys())
    
    def get_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return list(self.orders.keys())
    
    def get_session_mappings(self) -> Dict:
        """Get session-to-order mappings."""
        return self.session_order_mappings
    
    def get_converting_sessions(self) -> Dict:
        """Get only converting sessions (those with orders)."""
        return {k: v for k, v in self.session_order_mappings.items() if v['order_id']}
    
    def get_non_converting_sessions(self) -> Dict:
        """Get only non-converting sessions."""
        return {k: v for k, v in self.session_order_mappings.items() if not v['order_id']}
    
    def get_time_config(self) -> Dict:
        """Get unified time configuration."""
        return self.time_config
    
    def get_target_metrics(self) -> Dict:
        """Get target metrics for validation."""
        return self.target_metrics
    
    def validate_registry(self) -> bool:
        """Validate registry consistency."""
        self.logger.info("Validating registry consistency...")
        
        errors = []
        
        # Check conversion rate
        converting = len(self.get_converting_sessions())
        total_sessions = len(self.session_order_mappings)
        actual_conversion_rate = converting / total_sessions if total_sessions > 0 else 0
        target_rate = self.target_metrics['online_conversion_rate']
        
        if abs(actual_conversion_rate - target_rate) > 0.005:  # 0.5% tolerance
            errors.append(f"Conversion rate mismatch: {actual_conversion_rate:.3f} vs target {target_rate:.3f}")
        
        # Check revenue consistency - compare only online order revenue vs session revenue
        online_channels = ['online', 'mobile_app', 'social_commerce']
        online_order_revenue = sum(o['order_total_eur'] for o in self.orders.values() 
                                 if o['channel'] in online_channels)
        session_revenue = sum(s['order_value_eur'] for s in self.session_order_mappings.values())
        
        if abs(online_order_revenue - session_revenue) > 1000:  # €1000 tolerance
            errors.append(f"Revenue mismatch: online orders {online_order_revenue:.2f} vs sessions {session_revenue:.2f}")
        
        # Check for orphaned references
        session_order_ids = {s['order_id'] for s in self.session_order_mappings.values() if s['order_id']}
        order_ids = set(self.orders.keys())
        orphaned_sessions = session_order_ids - order_ids
        
        if orphaned_sessions:
            errors.append(f"Orphaned session order references: {len(orphaned_sessions)}")
        
        if errors:
            for error in errors:
                self.logger.error(error)
            return False
        else:
            self.logger.info("Registry validation passed")
            return True

def main():
    """Example usage of the DataRegistry."""
    logging.basicConfig(level=logging.INFO)
    
    registry = DataRegistry()
    
    if registry.load_operational_data():
        print("✅ Registry loaded successfully")
        print(f"📊 Customers: {len(registry.get_customer_ids())}")
        print(f"📦 Products: {len(registry.get_product_ids())}")
        print(f"🛒 Orders: {len(registry.get_order_ids())}")
        print(f"🌐 Sessions: {len(registry.get_session_mappings())}")
        print(f"💰 Converting sessions: {len(registry.get_converting_sessions())}")
        
        if registry.validate_registry():
            print("✅ Registry validation passed")
        else:
            print("❌ Registry validation failed")
    else:
        print("❌ Failed to load registry")

if __name__ == "__main__":
    main()