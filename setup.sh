#!/bin/bash

# RealityFix Setup Script
# Automates the setup process for the entire project

echo "=================================="
echo "RealityFix Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version found"
else
    echo "✗ Python 3.8 or higher required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

# Download pretrained models
echo ""
echo "Downloading pretrained models (this may take a few minutes)..."
python3 << EOF
from transformers import AutoTokenizer, AutoModelForSequenceClassification
print("Downloading text model...")
AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
print("✓ Models downloaded successfully")
EOF

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p models
mkdir -p ../tests/example_inputs
mkdir -p ../tests/test_results
mkdir -p ../extension/icons
echo "✓ Directories created"

# Return to root directory
cd ..

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start the backend server:"
echo "   cd backend && python app.py"
echo ""
echo "2. Load the Chrome extension:"
echo "   - Open chrome://extensions/"
echo "   - Enable 'Developer mode'"
echo "   - Click 'Load unpacked'"
echo "   - Select the 'extension' folder"
echo ""
echo "3. Test the API:"
echo "   cd tests && python test_api.py"
echo ""
echo "For more information, see README.md"