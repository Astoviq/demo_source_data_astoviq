# Entity Creation Guide - WARP.md Compliant

**Following WARP.md Rule**: "dont hard code, always use guidelines and framework principles"

This guide provides the step-by-step process for adding new entities (tables) to the EuroStyle Retail Demo system following configuration-driven principles.

---

## 📋 Overview

The EuroStyle system follows a **5-step configuration-driven approach**:

1. **Database Schema Definition** (YAML)
2. **Data Generation Patterns** (YAML) 
3. **Column Mappings** (YAML)
4. **Generation Method Implementation** (Python)
5. **Integration & Testing**

---

## 🎯 Step 1: Database Schema Definition

### Location: `config/schemas/{domain}_schema.yaml`

Add your table definition to the appropriate domain schema file:

```yaml
# Example: config/schemas/webshop_schema.yaml
database: eurostyle_webshop

tables:
  product_reviews:
    engine: "MergeTree()"
    primary_key: "review_id"
    order_by: "review_id"
    columns:
      review_id:
        type: "String"
        nullable: false
        description: "Unique review identifier"
      product_id:
        type: "String"
        nullable: false
        description: "Referenced product ID"
      customer_id:
        type: "Nullable(String)"
        nullable: true
        description: "Customer who wrote the review (null for guest reviews)"
      rating:
        type: "UInt8"
        nullable: false
        description: "Star rating 1-5"
      review_text:
        type: "String"
        nullable: false
        description: "Review content"
      is_verified_purchase:
        type: "Bool"
        nullable: false
        default: false
        description: "Whether reviewer purchased the product"
      created_date:
        type: "DateTime"
        nullable: false
        description: "Review creation timestamp"
```

---

## 🎲 Step 2: Data Generation Patterns

### Location: `config/data_patterns/{domain}_patterns.yaml`

Define how data should be generated:

```yaml
# Example: config/data_patterns/webshop_patterns.yaml
database: eurostyle_webshop

product_reviews:
  generation_rules:
    total_records_by_mode:
      demo: 100
      fast: 500  
      full: 2500
    dependency_tables: ["customers", "products", "orders"]
    review_rate: 0.05  # 5% of orders result in reviews
    
  data_patterns:
    rating_distribution:
      5_STAR: 0.45  # 45%
      4_STAR: 0.25  # 25%
      3_STAR: 0.15  # 15%
      2_STAR: 0.10  # 10%
      1_STAR: 0.05  # 5%
      
    reviewer_types:
      VERIFIED_BUYER: 0.85    # 85%
      GUEST_REVIEWER: 0.15    # 15%
      
    content_templates:
      positive:
        - "Great product, exactly as described!"
        - "Fast delivery and excellent quality"
        - "Would recommend to others"
      neutral:
        - "Good product, meets expectations"
        - "As advertised, nothing special"
      negative:
        - "Not as described, disappointed"
        - "Poor quality materials"

business_logic:
  seasonal_patterns: true
  customer_behavior_modeling: true
  product_category_preferences: true
```

---

## 🗂️ Step 3: Column Mappings

### Location: `config/mappings/{domain}_column_mappings.yaml`

Define CSV-to-database column mappings:

```yaml
# Example: config/mappings/webshop_column_mappings.yaml
database: eurostyle_webshop

tables:
  product_reviews:
    csv_columns:
      - review_id
      - product_id
      - customer_id
      - order_id
      - rating
      - review_title
      - review_text
      - is_verified_purchase
      - helpful_votes
      - review_date
      - created_date
      - updated_date
      
    database_columns:
      - review_id
      - product_id
      - customer_id
      - order_id
      - rating
      - review_title
      - review_text
      - is_verified_purchase
      - helpful_votes
      - review_date
      - created_date
      - updated_date
      
    defaults:
      created_date: "now()"
      updated_date: "now()"
      
    transformations:
      rating: "CAST(rating AS UInt8)"
      is_verified_purchase: "CAST(is_verified_purchase AS Bool)"
```

---

## 🐍 Step 4: Generation Method Implementation

### Location: `scripts/data-generation/generators/{domain}_generators.py`

Create a dedicated generator class:

```python
# Example: scripts/data-generation/generators/webshop_generators.py

import random
import yaml
from faker import Faker
from typing import List, Dict, Any
from pathlib import Path

class WebshopEntityGenerator:
    """WARP.md compliant generator for webshop entities."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.faker = Faker()
        self._load_configurations()
        
    def _load_configurations(self):
        """Load all configuration files following WARP.md principles."""
        # Load schema
        with open(self.config_path / 'schemas' / 'webshop_schema.yaml') as f:
            self.schema = yaml.safe_load(f)
            
        # Load patterns  
        with open(self.config_path / 'data_patterns' / 'webshop_patterns.yaml') as f:
            self.patterns = yaml.safe_load(f)
            
        # Load mappings
        with open(self.config_path / 'mappings' / 'webshop_column_mappings.yaml') as f:
            self.mappings = yaml.safe_load(f)
    
    def generate_product_reviews(self, mode: str, dependencies: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate product reviews following configuration patterns."""
        
        # Get configuration for this entity
        config = self.patterns['product_reviews']
        generation_rules = config['generation_rules']
        data_patterns = config['data_patterns']
        
        # Determine record count based on mode
        total_records = generation_rules['total_records_by_mode'][mode]
        
        # Check dependencies
        customers = dependencies.get('customers', [])
        products = dependencies.get('products', [])
        orders = dependencies.get('orders', [])
        
        if not customers or not products:
            raise ValueError("Missing required dependencies: customers and products")
            
        reviews = []
        
        # Generate reviews based on configuration patterns
        verified_count = int(total_records * data_patterns['reviewer_types']['VERIFIED_BUYER'])
        guest_count = total_records - verified_count
        
        # Generate verified buyer reviews
        for i in range(verified_count):
            review = self._create_review_record(
                i + 1, 
                customers, 
                products, 
                orders,
                is_verified=True,
                data_patterns=data_patterns
            )
            reviews.append(review)
            
        # Generate guest reviews
        for i in range(guest_count):
            review = self._create_review_record(
                verified_count + i + 1,
                customers,
                products, 
                orders,
                is_verified=False,
                data_patterns=data_patterns
            )
            reviews.append(review)
            
        return reviews
    
    def _create_review_record(self, index: int, customers: List, products: List, 
                            orders: List, is_verified: bool, data_patterns: Dict) -> Dict:
        """Create a single review record following patterns."""
        
        product = random.choice(products)
        
        # Select rating based on distribution
        rating_key = random.choices(
            list(data_patterns['rating_distribution'].keys()),
            weights=list(data_patterns['rating_distribution'].values())
        )[0]
        rating_value = int(rating_key.split('_')[0])
        
        # Select content template based on rating
        if rating_value >= 4:
            content_key = 'positive'
        elif rating_value == 3:
            content_key = 'neutral'
        else:
            content_key = 'negative'
            
        review_text = random.choice(data_patterns['content_templates'][content_key])
        
        # Create review record
        review = {
            'review_id': f"REV_{index:08d}",
            'product_id': product['product_id'],
            'customer_id': random.choice(customers)['customer_id'] if is_verified else None,
            'order_id': random.choice(orders)['order_id'] if is_verified and orders else None,
            'rating': rating_value,
            'review_title': f"{rating_value} star review",
            'review_text': review_text,
            'is_verified_purchase': is_verified,
            'helpful_votes': random.randint(0, 25 if is_verified else 10),
            'review_date': self.faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
            'created_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
            'updated_date': self.faker.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return review
```

---

## 🔧 Step 5: Integration with Main Generator

### Update: `scripts/data-generation/universal_data_generator_v2.py`

Add integration points:

```python
# Import the new generator
from generators.webshop_generators import WebshopEntityGenerator

class UniversalDataGeneratorV2:
    
    def __init__(self, config_path: str):
        # ... existing code ...
        self.webshop_generator = WebshopEntityGenerator(config_path)
    
    def generate_webshop_entities(self, mode: str) -> Dict[str, List[Dict]]:
        """Generate webshop entities using dedicated generator."""
        
        # Prepare dependencies
        dependencies = {
            'customers': self.generated_data.get('customers', []),
            'products': self.generated_data.get('products', []),
            'orders': self.generated_data.get('orders', []),
            'web_sessions': self.generated_data.get('web_sessions', [])
        }
        
        results = {}
        
        # Generate product reviews
        try:
            product_reviews = self.webshop_generator.generate_product_reviews(mode, dependencies)
            results['product_reviews'] = product_reviews
            self.generated_data['product_reviews'] = product_reviews
            self.logger.info(f"✅ Generated {len(product_reviews)} product reviews")
        except Exception as e:
            self.logger.error(f"❌ Failed to generate product reviews: {e}")
            results['product_reviews'] = []
            
        return results
```

---

## 📊 Step 6: CSV Generation and Loading

The system automatically:

1. **Saves CSV files** using `_save_csv_data()` method
2. **Compresses files** as `.csv.gz` 
3. **Loads into ClickHouse** via loading scripts
4. **Validates data** using consistency checks

### CSV File Naming Convention:
```
data/csv/{database}.{table}.csv.gz
```

Example: `data/csv/eurostyle_webshop.product_reviews.csv.gz`

---

## 🧪 Step 7: Testing and Validation

### Test the new entity:

```bash
# Test generation only
python3 scripts/data-generation/universal_data_generator_v2.py --mode demo

# Test full pipeline
./eurostyle.sh demo-fast

# Validate data
./eurostyle.sh status
```

### Verify in database:
```sql
SELECT COUNT(*) FROM eurostyle_webshop.product_reviews;
SELECT rating, COUNT(*) as count FROM eurostyle_webshop.product_reviews GROUP BY rating;
```

---

## 🎯 Best Practices

### ✅ DO:
- Follow YAML configuration for all patterns
- Use dependency injection for related data
- Implement realistic business logic
- Add comprehensive logging
- Use consistent naming conventions
- Validate all inputs and outputs

### ❌ DON'T:
- Hard-code values in generation methods
- Skip dependency validation
- Generate unrealistic data distributions
- Ignore foreign key relationships
- Create circular dependencies

---

## 📁 File Structure Summary

```
config/
├── schemas/
│   └── webshop_schema.yaml          # Table definitions
├── data_patterns/
│   └── webshop_patterns.yaml        # Generation rules
└── mappings/
    └── webshop_column_mappings.yaml # CSV mappings

scripts/data-generation/
├── generators/
│   └── webshop_generators.py        # Entity generators  
└── universal_data_generator_v2.py   # Main generator

data/csv/
└── eurostyle_webshop.product_reviews.csv.gz  # Generated data
```

---

## 🚀 Quick Start Template

For adding a new entity called `{entity_name}` to `{domain}`:

1. **Copy this template** and replace `{entity_name}` and `{domain}`
2. **Define schema** in `config/schemas/{domain}_schema.yaml`
3. **Define patterns** in `config/data_patterns/{domain}_patterns.yaml` 
4. **Define mappings** in `config/mappings/{domain}_column_mappings.yaml`
5. **Implement generator** in `scripts/data-generation/generators/{domain}_generators.py`
6. **Integrate** with main generator
7. **Test** with `./eurostyle.sh demo-fast`

This approach ensures **100% WARP.md compliance** and maintainable, scalable entity creation.