#!/bin/bash

if [ -z "$1" ]; then
    echo "🔍 EuroStyle Data Preview Utility"
    echo "================================="
    echo "Usage: $0 <filename.csv.gz> [lines]"
    echo ""
    echo "Examples:"
    echo "  $0 eurostyle_finance.currencies.csv.gz"
    echo "  $0 eurostyle_hr.employees.csv.gz 10"
    echo ""
    echo "Available files:"
    ls generated_data/*.gz | sed 's/generated_data\//  - /'
    exit 1
fi

LINES=${2:-20}
FILE="generated_data/$1"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

echo "🔍 Preview of $1 (first $LINES lines):"
echo "$(printf '=%.0s' {1..50})"
gzcat "$FILE" | head -n "$LINES"
echo "$(printf '=%.0s' {1..50})"
echo "💡 Total lines: $(gzcat "$FILE" | wc -l | tr -d ' ')"
