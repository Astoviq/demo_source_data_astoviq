#!/usr/bin/env python3
"""
POS to Operations Orders Transformer
====================================

Transforms POS transactions into Operations orders to implement 
"Operations as Master" architecture where all sales flow through
the operations database.

Usage:
    python3 scripts/data-transformation/pos_to_operations_orders.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import logging
from datetime import datetime
import random
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PosToOperations')

def load_pos_transactions():
    """Load POS transactions from CSV."""
    try:
        pos_file = 'data/csv/eurostyle_pos.transactions.csv.gz'
        logger.info(f"Loading POS transactions from {pos_file}")
        df = pd.read_csv(pos_file, compression='gzip')
        logger.info(f"Loaded {len(df)} POS transactions")
        return df
    except Exception as e:
        logger.error(f"Failed to load POS transactions: {e}")
        return None

def load_customers():
    """Load customers for mapping."""
    try:
        customers_file = 'data/csv/eurostyle_operational.customers.csv.gz'
        logger.info(f"Loading customers from {customers_file}")
        df = pd.read_csv(customers_file, compression='gzip')
        logger.info(f"Loaded {len(df)} customers")
        return df
    except Exception as e:
        logger.error(f"Failed to load customers: {e}")
        return None

def transform_pos_to_orders(pos_df, customers_df):
    """Transform POS transactions to Operations orders."""
    logger.info("Transforming POS transactions to Operations orders...")
    
    # Get existing online orders to determine next order ID
    try:
        online_orders = pd.read_csv('data/csv/eurostyle_operational.orders.csv.gz', compression='gzip')
        last_order_num = max([int(oid.split('_')[-1]) for oid in online_orders['order_id']])
        logger.info(f"Last online order number: {last_order_num}")
    except:
        last_order_num = 0
        logger.warning("Could not determine last order ID, starting from 0")
    
    orders = []
    order_lines = []
    
    for idx, pos_txn in pos_df.iterrows():
        # Generate new order ID
        order_num = last_order_num + idx + 1
        order_id = f"ORD_EU_2024_{order_num:06d}"
        
        # Map to customer (random assignment for demo)
        customer = customers_df.sample(1).iloc[0]
        customer_id = customer['customer_id']
        
        # Create order from POS transaction
        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'store_id': pos_txn['store_id'],
            'order_date': pos_txn['transaction_date'],
            'order_datetime': pos_txn['transaction_datetime'],
            'delivery_date': None,  # In-store pickup
            'promised_delivery_date': None,
            'subtotal_eur': float(pos_txn['total_amount_eur']),  # Using total as subtotal for simplicity
            'tax_amount_eur': float(pos_txn.get('tax_amount_eur', 0)),
            'shipping_cost_eur': 0.0,  # No shipping for in-store
            'discount_amount_eur': float(pos_txn.get('discount_amount_eur', 0)),
            'total_amount_eur': float(pos_txn['total_amount_eur']),
            'currency_code': 'EUR',
            'exchange_rate': 1.0000,
            'total_amount_local': float(pos_txn['total_amount_eur']),
            'order_status': 'completed',
            'fulfillment_center': pos_txn['store_id'],
            'shipping_method': 'in_store_pickup',
            'tracking_number': None,
            'order_channel': 'in-store',
            'traffic_source': 'walk_in',
            'campaign_code': None,
            'payment_method': pos_txn.get('payment_method', 'card'),
            'payment_status': 'paid',
            'customer_service_notes': f"Converted from POS transaction {pos_txn['transaction_id']}",
            'return_reason': None,
            'return_date': None,
            'created_at': pos_txn['transaction_datetime'],
            'updated_at': pos_txn['transaction_datetime']
        }
        
        orders.append(order)
        
        # Create basic order line (simplified for demo)
        order_line = {
            'order_line_id': f"OL_{order_num:06d}_001",
            'order_id': order_id,
            'product_id': 'PROD_MIXED_RETAIL',  # Placeholder - POS items would need detailed mapping
            'quantity': int(pos_txn.get('item_count', 1)),
            'unit_price_eur': float(pos_txn['total_amount_eur']) / max(int(pos_txn.get('item_count', 1)), 1),
            'line_total_eur': float(pos_txn['total_amount_eur']),
            'discount_amount_eur': float(pos_txn.get('discount_amount_eur', 0)),
            'tax_amount_eur': float(pos_txn.get('tax_amount_eur', 0)),
            'fulfillment_status': 'delivered',
            'shipped_quantity': int(pos_txn.get('item_count', 1)),
            'return_quantity': 0,
            'created_at': pos_txn['transaction_datetime'],
            'updated_at': pos_txn['transaction_datetime']
        }
        
        order_lines.append(order_line)
    
    logger.info(f"Transformed {len(orders)} POS transactions to Operations orders")
    return pd.DataFrame(orders), pd.DataFrame(order_lines)

def save_to_csv(orders_df, order_lines_df):
    """Save transformed data to CSV files."""
    # Load existing online orders and append
    try:
        existing_orders = pd.read_csv('data/csv/eurostyle_operational.orders.csv.gz', compression='gzip')
        combined_orders = pd.concat([existing_orders, orders_df], ignore_index=True)
        logger.info(f"Combined {len(existing_orders)} existing + {len(orders_df)} new orders = {len(combined_orders)} total")
    except:
        combined_orders = orders_df
        logger.info(f"No existing orders found, creating new file with {len(orders_df)} orders")
    
    # Save combined orders
    orders_file = 'data/csv/eurostyle_operational.orders.csv.gz'
    combined_orders.to_csv(orders_file, compression='gzip', index=False)
    logger.info(f"Saved {len(combined_orders)} orders to {orders_file}")
    
    # Load existing order lines and append
    try:
        existing_lines = pd.read_csv('data/csv/eurostyle_operational.order_lines.csv.gz', compression='gzip')
        combined_lines = pd.concat([existing_lines, order_lines_df], ignore_index=True)
        logger.info(f"Combined {len(existing_lines)} existing + {len(order_lines_df)} new lines = {len(combined_lines)} total")
    except:
        combined_lines = order_lines_df
        logger.info(f"No existing order lines found, creating new file with {len(order_lines_df)} lines")
    
    # Save combined order lines
    lines_file = 'data/csv/eurostyle_operational.order_lines.csv.gz'
    combined_lines.to_csv(lines_file, compression='gzip', index=False)
    logger.info(f"Saved {len(combined_lines)} order lines to {lines_file}")

def main():
    """Main transformation process."""
    logger.info("🔄 Starting POS to Operations transformation...")
    
    # Load data
    pos_df = load_pos_transactions()
    customers_df = load_customers()
    
    if pos_df is None or customers_df is None:
        logger.error("Failed to load required data")
        return False
    
    # Transform data
    orders_df, order_lines_df = transform_pos_to_orders(pos_df, customers_df)
    
    # Save transformed data
    save_to_csv(orders_df, order_lines_df)
    
    logger.info("✅ POS to Operations transformation completed!")
    logger.info(f"📊 Created {len(orders_df)} in-store orders from POS transactions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)