#!/usr/bin/env python3
"""
Fix CSV null handling issues for ClickHouse compatibility.

This script addresses common CSV parsing issues:
1. Replace \\N with empty string for nullable date fields
2. Fix malformed quotes around null values
3. Handle performance review rating schema mismatches
"""

import os
import csv
import gzip
import re
import sys
from pathlib import Path

def fix_csv_nulls(csv_file_path):
    """Fix null value issues in a CSV file."""
    
    if not os.path.exists(csv_file_path):
        print(f"⚠️  File not found: {csv_file_path}")
        return False
    
    print(f"🔧 Fixing null values in {os.path.basename(csv_file_path)}")
    
    # Read the compressed file
    try:
        with gzip.open(csv_file_path, 'rt', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {csv_file_path}: {e}")
        return False
    
    # Fix common null value issues
    original_content = content
    
    # 1. Replace quoted \\N with empty string for nullable fields
    content = re.sub(r',"\\N",', r',"",', content)
    content = re.sub(r',"\\N"$', r',""', content, flags=re.MULTILINE)
    
    # 2. Fix malformed quotes around nulls  
    content = re.sub(r'"\\"N"', r'""', content)
    
    # 3. Handle performance reviews - convert string ratings to numeric
    if 'performance_reviews' in csv_file_path:
        # Map rating strings to decimal values
        rating_map = {
            '"EXCEEDS_EXPECTATIONS"': '4.0',
            '"MEETS_EXPECTATIONS"': '3.0', 
            '"BELOW_EXPECTATIONS"': '2.0',
            '"UNSATISFACTORY"': '1.0'
        }
        for old_rating, new_rating in rating_map.items():
            content = content.replace(old_rating, new_rating)
    
    # 4. Fix DateTime format issues - ensure proper format
    content = re.sub(r'(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2})', r'\1', content)
    
    # Only write back if content changed
    if content != original_content:
        try:
            with gzip.open(csv_file_path, 'wt', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed null values in {os.path.basename(csv_file_path)}")
            return True
        except Exception as e:
            print(f"❌ Error writing {csv_file_path}: {e}")
            return False
    else:
        print(f"ℹ️  No changes needed for {os.path.basename(csv_file_path)}")
        return True

def main():
    """Fix null values in all CSV files in the data/csv directory."""
    
    csv_dir = Path("data/csv")
    if not csv_dir.exists():
        print(f"❌ CSV directory not found: {csv_dir}")
        return 1
    
    print("🚀 Fixing CSV null value issues...")
    
    # Find all CSV.gz files
    csv_files = list(csv_dir.glob("*.csv.gz"))
    
    if not csv_files:
        print("⚠️  No CSV.gz files found in data/csv")
        return 1
    
    print(f"📦 Found {len(csv_files)} CSV files to process")
    
    success_count = 0
    for csv_file in sorted(csv_files):
        if fix_csv_nulls(csv_file):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(csv_files)} files processed successfully")
    
    if success_count == len(csv_files):
        print("✅ All CSV files processed successfully!")
        return 0
    else:
        print("⚠️  Some files had issues - check output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())