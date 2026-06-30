#!/bin/bash
echo "========================================"
echo "TikTok Bot Setup (with VENV)"
echo "========================================"
echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
echo ""
echo "Step 2: Activating venv and installing packages..."
source venv/bin/activate
pip install --upgrade pip
pip install selenium webdriver-manager beautifulsoup4 lxml pyyaml python-dotenv
echo ""
echo "Step 3: Creating necessary directories..."
mkdir -p data/logs
mkdir -p sessions
echo ""
echo "Step 4: Setup complete!"
echo ""
echo "========================================"
echo "HOW TO RUN:"
echo "========================================"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Edit config.yaml with your credentials"
echo "3. Add comments to input/comments.txt"
echo "4. Run: python main.py"
echo ""