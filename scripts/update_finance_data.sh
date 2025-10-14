#!/bin/bash

echo "🏦 EuroStyle Finance Data Update Utility"
echo "========================================"

cd "$(dirname "$0")"

# Step 1: Generate new finance data
echo "📊 Generating fresh finance data..."
python3 generate_complete_finance_data.py

if [ $? -ne 0 ]; then
    echo "❌ Finance data generation failed!"
    exit 1
fi

# Step 2: Remove old compressed finance files
echo "🧹 Cleaning old compressed finance data..."
cd ../generated_data
rm -f eurostyle_finance.*.csv.gz

# Step 3: Compress new CSV files
echo "🗜️ Compressing new finance data..."
if ls eurostyle_finance.*.csv 1> /dev/null 2>&1; then
    gzip eurostyle_finance.*.csv
    echo "✅ Finance data compressed successfully!"
    
    # Show compression results
    echo "📊 Compressed finance files:"
    ls -lah eurostyle_finance.*.csv.gz | awk '{print "  " $9 ": " $5}'
    echo "💾 Total finance data size: $(du -sh eurostyle_finance.*.csv.gz | awk '{sum+=$1} END {print sum}')"
else
    echo "⚠️ No finance CSV files found to compress"
fi

echo "🎉 Finance data update completed!"