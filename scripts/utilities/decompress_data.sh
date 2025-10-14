#!/bin/bash

echo "🗜️ EuroStyle Data Decompression Utility"
echo "======================================"

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [--all|--finance|--hr|--webshop|--operational]"
    echo ""
    echo "Options:"
    echo "  --all          Decompress all CSV files"
    echo "  --finance      Decompress only finance CSV files"  
    echo "  --hr           Decompress only HR CSV files"
    echo "  --webshop      Decompress only webshop CSV files"
    echo "  --operational  Decompress only operational CSV files"
    echo "  --help         Show this help message"
    exit 0
fi

cd generated_data

case "$1" in
    --finance)
        echo "📊 Decompressing Finance data..."
        gunzip eurostyle_finance.*.csv.gz
        ;;
    --hr)
        echo "👥 Decompressing HR data..."
        gunzip eurostyle_hr.*.csv.gz
        ;;
    --webshop)
        echo "🛒 Decompressing Webshop data..."
        gunzip eurostyle_webshop.*.csv.gz
        ;;
    --operational)
        echo "⚙️ Decompressing Operational data..."
        gunzip eurostyle_operational.*.csv.gz 2>/dev/null || echo "No operational CSV files found"
        ;;
    --all|"")
        echo "📦 Decompressing all CSV data files..."
        gunzip *.csv.gz
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

echo "✅ Decompression completed!"
echo "💡 Tip: You can re-compress with: gzip *.csv"
