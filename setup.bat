@echo off
REM Electricity Demand Forecasting System - Setup and Run Script

echo.
echo ========================================
echo Electricity Demand Forecasting System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Train models:
echo    python backend/train_models.py --data_path data/sample_electricity.csv
echo.
echo 2. Start Flask API (in a new terminal):
echo    python backend/app.py
echo.
echo 3. Open Dashboard:
echo    Open frontend/index.html in your browser
echo.
echo Or run the quick start script after training:
echo    python run_system.py
echo.
pause
