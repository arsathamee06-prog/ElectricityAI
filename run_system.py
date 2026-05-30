"""
Quick start script to run the entire Electricity Demand Forecasting System
Usage: python run_system.py
"""

import subprocess
import os
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")
    
    try:
        process = subprocess.Popen(cmd, shell=True)
        return process
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    print("\n" + "="*50)
    print("Electricity Demand Forecasting System - Quick Start")
    print("="*50)
    
    # Check if models are trained
    models_dir = Path("models")
    model_files = list(models_dir.glob("*_model.pkl")) + list(models_dir.glob("*_model.h5"))
    
    if not model_files:
        print("\n⚠️  No trained models found!")
        print("\nPlease train models first:")
        print("  python backend/train_models.py --data_path data/sample_electricity.csv")
        print("\nAfter training, run this script again.")
        sys.exit(1)
    
    print("\n✓ Trained models found!")
    print(f"  - {len(model_files)} model files detected")
    
    # Start Flask API
    print("\n[1/2] Starting Flask API Server...")
    flask_process = run_command("python backend/app.py", "Flask API Server")
    
    if flask_process is None:
        sys.exit(1)
    
    # Wait for Flask to start
    print("\nWaiting for API to start...")
    time.sleep(3)
    
    # Open browser (Windows)
    if sys.platform == 'win32':
        print("\n[2/2] Opening Dashboard in browser...")
        frontend_path = os.path.abspath("frontend/index.html")
        os.startfile(frontend_path)
    elif sys.platform == 'darwin':  # macOS
        print("\n[2/2] Opening Dashboard in browser...")
        os.system(f"open 'file://{os.path.abspath(\"frontend/index.html\")}'")
    else:  # Linux
        print("\n[2/2] Opening Dashboard in browser...")
        os.system(f"xdg-open 'file://{os.path.abspath(\"frontend/index.html\")}'")
    
    print("\n" + "="*50)
    print("System Ready!")
    print("="*50)
    print("\n✓ API Server: http://localhost:5000")
    print("✓ Dashboard: Opening in your browser...")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        flask_process.terminate()
        print("✓ Server stopped")

if __name__ == '__main__':
    main()
