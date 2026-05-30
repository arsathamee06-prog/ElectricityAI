#!/bin/bash
# Electricity Demand Forecasting System - Setup and Run Script

echo ""
echo "========================================"
echo "Electricity Demand Forecasting System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
if [ ! -d venv ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Train models:"
echo "   python backend/train_models.py --data_path data/sample_electricity.csv"
echo ""
echo "2. Start Flask API (in a new terminal):"
echo "   python backend/app.py"
echo ""
echo "3. Open Dashboard:"
echo "   Open frontend/index.html in your browser"
echo ""
echo "Or run the quick start script after training:"
echo "   python run_system.py"
echo ""
