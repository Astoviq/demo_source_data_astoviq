#!/bin/bash

echo "🗜️ EuroStyle Data Compression Utility" 
echo "====================================="

cd generated_data

if ls *.csv 1> /dev/null 2>&1; then
    echo "📦 Compressing CSV data files..."
    gzip *.csv
    echo "✅ Compression completed!"
    echo "📊 Space saved:"
    du -sh *.gz | tail -5
    echo "Total compressed size: $(du -sh . | cut -f1)"
else
    echo "ℹ️  No uncompressed CSV files found."
    echo "📁 Current compressed files:"
    ls -lah *.gz | head -5 | cut -d' ' -f5,9
    echo "Total compressed size: $(du -sh . | cut -f1)"
fi
