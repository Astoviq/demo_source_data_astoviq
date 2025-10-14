#!/bin/bash

# =============================================================================
# EuroStyle Fashion - Development Environment Setup
# =============================================================================

echo "🛠️ Setting up EuroStyle development environment..."

# Navigate to data-generator directory
cd "$(dirname "$0")/../../data-generator" || exit 1

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "⬇️ Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment in the future:"
echo "  cd data-generator"
echo "  source venv/bin/activate"
echo ""
echo "To run data generation:"
echo "  python3 generate_data.py"

