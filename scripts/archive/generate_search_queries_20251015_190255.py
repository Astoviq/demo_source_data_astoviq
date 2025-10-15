#!/usr/bin/env python3
"""
EuroStyle Retail Demo - Search Queries Data Generator
Generates realistic search query data matching the database schema exactly.

Following WARP.md principles:
- Configuration-driven data generation
- Proper CSV schema alignment  
- Realistic European fashion search patterns
"""

import csv
import gzip
import random
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Fashion search terms for European market
SEARCH_TERMS = [
    # Basic categories
    "jeans", "shirt", "dress", "jacket", "sweater", "boots", "sneakers", 
    "coat", "blazer", "trousers", "skirt", "top", "blouse", "cardigan",
    
    # Seasonal items
    "winter coat", "summer dress", "spring jacket", "autumn sweater",
    "swimwear", "beachwear", "winter boots", "sandals",
    
    # Style keywords
    "casual", "formal", "business", "elegant", "sporty", "vintage",
    "bohemian", "minimalist", "trendy", "classic",
    
    # Specific items
    "little black dress", "white shirt", "leather jacket", "denim jacket",
    "cocktail dress", "evening gown", "polo shirt", "hoodie",
    
    # Brand-related
    "designer", "luxury", "premium", "sustainable", "eco-friendly",
    "cotton", "wool", "silk", "cashmere", "linen",
    
    # Size-related
    "plus size", "petite", "tall", "slim fit", "regular fit",
    
    # Color searches
    "black dress", "white shirt", "blue jeans", "red coat", "navy blazer",
    "grey sweater", "beige trousers", "brown boots", "green jacket"
]

# Filter options commonly used in fashion e-commerce
FILTER_OPTIONS = [
    "color", "size", "brand", "price", "material", "style", "category",
    "discount", "new_arrival", "bestseller", "sustainable", "season"
]

# Sort orders commonly used in search
SORT_OPTIONS = [
    "RELEVANCE", "PRICE_LOW_HIGH", "PRICE_HIGH_LOW", "NEWEST", 
    "BESTSELLER", "CUSTOMER_RATING", "DISCOUNT"
]

COUNTRIES = ["NL", "DE", "FR", "BE", "LU"]

def generate_search_query_id(index):
    """Generate search query ID following the pattern"""
    return f"SEARCH_EU_{index:08d}"

def generate_realistic_search_data():
    """Generate realistic search queries data matching database schema"""
    
    # Read existing session and customer data for referential integrity
    sessions = []
    customers = []
    products = []
    
    try:
        # Load existing sessions
        with gzip.open("data/csv/eurostyle_webshop.web_sessions.csv.gz", "rt") as f:
            session_reader = csv.DictReader(f)
            sessions = [row["session_id"] for row in session_reader][:5000]  # Sample
    except Exception as e:
        print(f"Warning: Could not load sessions: {e}")
        # Generate some sample session IDs
        sessions = [f"SESS_{i:08d}" for i in range(1, 1001)]
    
    try:
        # Load existing customers  
        with gzip.open("data/csv/eurostyle_operational.customers.csv.gz", "rt") as f:
            customer_reader = csv.DictReader(f)
            customers = [row["customer_id"] for row in customer_reader][:2000]  # Sample
    except Exception as e:
        print(f"Warning: Could not load customers: {e}")
        # Generate some sample customer IDs
        customers = [f"CUST_EU_{i:06d}" for i in range(1, 501)]
    
    try:
        # Load existing products
        with gzip.open("data/csv/eurostyle_operational.products.csv.gz", "rt") as f:
            product_reader = csv.DictReader(f)
            products = [row["product_id"] for row in product_reader][:1000]  # Sample
    except Exception as e:
        print(f"Warning: Could not load products: {e}")
        # Generate some sample product IDs
        products = [f"PROD_EU_{i:06d}" for i in range(1, 201)]

    search_queries = []
    
    # Generate search queries data
    for i in range(1, 1501):  # Generate 1500 search queries
        
        # Select random session and customer (30% anonymous searches)
        session_id = random.choice(sessions) if sessions else f"SESS_{random.randint(1000, 9999):08d}"
        customer_id = random.choice(customers) if customers and random.random() > 0.3 else ""
        
        # Select search term and generate realistic results
        search_term = random.choice(SEARCH_TERMS)
        results_count = random.randint(0, 500)  # Some searches return no results
        
        # Generate timestamp within last 90 days
        search_timestamp = datetime.now() - timedelta(
            days=random.randint(1, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Determine if user clicked on a result (60% click-through rate)
        clicked_result_position = None
        clicked_product_id = None
        if results_count > 0 and random.random() < 0.6:
            clicked_result_position = min(random.randint(1, 10), results_count)
            clicked_product_id = random.choice(products) if products else f"PROD_EU_{random.randint(1, 200):06d}"
        
        # Generate filters (30% of searches use filters)
        filters_applied = []
        if random.random() < 0.3:
            num_filters = random.randint(1, 3)
            filters_applied = random.sample(FILTER_OPTIONS, num_filters)
        
        # Sort order
        sort_order = random.choice(SORT_OPTIONS)
        
        # Search refinements (number of times user modified search)
        search_refinements = random.randint(0, 3) if random.random() < 0.4 else 0
        
        # No results flag
        no_results = results_count == 0
        
        # Country code
        country_code = random.choice(COUNTRIES)
        
        search_query = {
            "search_query_id": generate_search_query_id(i),
            "session_id": session_id,
            "customer_id": customer_id if customer_id else "",  # Empty string for NULL
            "country_code": country_code,
            "search_term": search_term,
            "search_timestamp": search_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "results_count": results_count,
            "clicked_result_position": clicked_result_position if clicked_result_position else "",  # Empty for NULL
            "clicked_product_id": clicked_product_id if clicked_product_id else "",  # Empty for NULL
            "filters_applied": str(filters_applied),  # Array as string representation
            "sort_order": sort_order,
            "search_refinements": search_refinements,
            "no_results": "true" if no_results else "false",  # Boolean as string
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        search_queries.append(search_query)
    
    return search_queries

def main():
    """Generate and save search queries CSV"""
    print("🔍 Generating EuroStyle Search Queries Data")
    print("=" * 50)
    
    # Ensure output directory exists
    output_dir = Path("data/csv")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate search queries data
    search_queries = generate_realistic_search_data()
    
    # Write to compressed CSV
    output_file = output_dir / "eurostyle_webshop.search_queries.csv.gz"
    
    with gzip.open(output_file, "wt", newline="", encoding="utf-8") as f:
        if search_queries:
            fieldnames = [
                "search_query_id", "session_id", "customer_id", "country_code",
                "search_term", "search_timestamp", "results_count", 
                "clicked_result_position", "clicked_product_id", "filters_applied",
                "sort_order", "search_refinements", "no_results", "created_at"
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(search_queries)
    
    print(f"✅ Generated {len(search_queries)} search query records")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Show sample data
    print("\n📋 Sample records:")
    for i, query in enumerate(search_queries[:3]):
        print(f"  {i+1}. {query['search_term']} → {query['results_count']} results")
        if query['clicked_product_id']:
            print(f"     Clicked: position {query['clicked_result_position']} → {query['clicked_product_id']}")

if __name__ == "__main__":
    main()