#!/bin/bash
echo "========================================"
echo "Starting TikTok Bot"
echo "========================================"
echo ""

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting bot..."
python main.py

echo ""
echo "Bot stopped."