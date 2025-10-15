#!/usr/bin/env python3
"""
Fix Boolean Format in CSV Files for ClickHouse Compatibility
============================================================

ClickHouse expects boolean values as 'true'/'false' (lowercase) 
but the Universal Data Generator V2 outputs Python booleans as 'True'/'False'.

This script fixes all CSV files to use proper boolean format.
"""

import gzip
import csv
import os
from pathlib import Path
import tempfile
import shutil

def fix_boolean_in_csv(file_path):
    """Fix boolean values in a single CSV file."""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+t', delete=False, newline='') as temp_file:
        temp_path = temp_file.name
        
        try:
            # Read the original file
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', newline='') as original:
                    reader = csv.reader(original)
                    writer = csv.writer(temp_file)
                    
                    # Process each row
                    for row in reader:
                        fixed_row = []
                        for cell in row:
                            # Replace boolean values
                            if cell == 'True':
                                fixed_row.append('true')
                            elif cell == 'False':
                                fixed_row.append('false')
                            else:
                                fixed_row.append(cell)
                        writer.writerow(fixed_row)
            else:
                with open(file_path, 'r', newline='') as original:
                    reader = csv.reader(original)
                    writer = csv.writer(temp_file)
                    
                    # Process each row
                    for row in reader:
                        fixed_row = []
                        for cell in row:
                            # Replace boolean values
                            if cell == 'True':
                                fixed_row.append('true')
                            elif cell == 'False':
                                fixed_row.append('false')
                            else:
                                fixed_row.append(cell)
                        writer.writerow(fixed_row)
                        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            os.unlink(temp_path)
            return False
        
        # Replace the original file with the fixed version
        if file_path.suffix == '.gz':
            # Compress the fixed file
            with open(temp_path, 'rb') as temp_in:
                with gzip.open(file_path, 'wb') as compressed_out:
                    shutil.copyfileobj(temp_in, compressed_out)
        else:
            shutil.move(temp_path, file_path)
        
        # Clean up temp file if it still exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            
        return True

def main():
    """Fix all CSV files in the data/csv directory."""
    csv_dir = Path("data/csv")
    
    if not csv_dir.exists():
        print("❌ data/csv directory not found")
        return
        
    # Find all CSV files (compressed and uncompressed)
    csv_files = list(csv_dir.glob("*.csv")) + list(csv_dir.glob("*.csv.gz"))
    
    if not csv_files:
        print("❌ No CSV files found in data/csv/")
        return
        
    print(f"🔧 Fixing boolean format in {len(csv_files)} CSV files...")
    
    fixed_count = 0
    for file_path in csv_files:
        print(f"  📝 Fixing {file_path.name}")
        if fix_boolean_in_csv(file_path):
            fixed_count += 1
        else:
            print(f"  ❌ Failed to fix {file_path.name}")
    
    print(f"✅ Fixed boolean format in {fixed_count}/{len(csv_files)} files")

if __name__ == "__main__":
    main()