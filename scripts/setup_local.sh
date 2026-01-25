#!/bin/bash

# Setup script for local development with venv

echo "🚀 Setting up AI Call Center Assistant - Local Development"
echo "==========================================================="

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  1. Activate venv:  source venv/bin/activate"
echo "  2. Run app:        streamlit run app.py --server.port=7860"
echo "  3. Open browser:   http://localhost:7860"
echo ""
echo "To deactivate venv: deactivate"
