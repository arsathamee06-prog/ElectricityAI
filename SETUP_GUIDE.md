# Setup and Usage Guide - Electricity Demand Forecasting System

## Quick Start (5 minutes)

### Windows Users

```bash
# 1. Navigate to project directory
cd c:\Users\Admin\Desktop\ElectricityAI

# 2. Run setup script
setup.bat

# 3. Train models (after venv is activated)
python backend/train_models.py --data_path data/sample_electricity.csv

# 4. Start the API server
python backend/app.py

# 5. In another terminal, run the system
python run_system.py
```

### macOS/Linux Users

```bash
# 1. Navigate to project directory
cd ElectricityAI

# 2. Run setup script
bash setup.sh

# 3. Train models (after venv is activated)
python backend/train_models.py --data_path data/sample_electricity.csv

# 4. Start the API server
python backend/app.py

# 5. In another terminal, run the system
python run_system.py
```

---

## Detailed Setup Instructions

### Step 1: Prerequisites

- **Python 3.8+** (Download from https://www.python.org/downloads/)
- **pip** (Usually comes with Python)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (Web API)
- pandas & numpy (Data processing)
- scikit-learn (ML preprocessing)
- statsmodels (ARIMA, SARIMA)
- prophet (Facebook's Prophet)
- TensorFlow & Keras (LSTM)
- And other supporting libraries

**Note:** This may take 5-10 minutes on first install.

### Step 4: Prepare Your Data

Your electricity demand CSV should have these columns:
```csv
timestamp,demand
2024-01-01 00:00:00,85.2
2024-01-01 01:00:00,82.5
...
```

Place your CSV file in the `data/` directory.

### Step 5: Train Models

```bash
python backend/train_models.py --data_path data/your_data.csv
```

This will:
1. Load and clean the data
2. Perform feature engineering
3. Train 4 models (ARIMA, SARIMA, Prophet, LSTM)
4. Compare performance metrics
5. Select the best model
6. Save all models as `.pkl` files

**Expected output:**
```
===================================================
Model Evaluation
===================================================

ARIMA:
  rmse: 12.45
  mae: 9.87
  mape: 8.92%
  r2: 0.8456
  directional_accuracy: 78.45%

SARIMA:
  rmse: 11.23
  mae: 8.95
  mape: 7.34%
  r2: 0.8789
  directional_accuracy: 82.10%

PROPHET:
  rmse: 13.56
  mae: 10.45
  mape: 9.67%
  r2: 0.8123
  directional_accuracy: 75.34%

LSTM:
  rmse: 10.89
  mae: 8.45
  mape: 6.89%
  r2: 0.8912
  directional_accuracy: 85.23%

===================================================
BEST MODEL: LSTM (rmse: 10.89)
===================================================
```

### Step 6: Start the Flask API

In a **new terminal** (with venv activated):

```bash
python backend/app.py
```

You should see:
```
Running on http://0.0.0.0:5000
```

The API is now ready to serve predictions!

### Step 7: Open the Dashboard

Option A: Directly open the HTML file
```
Double-click: frontend/index.html
```

Option B: Use a local server
```bash
python -m http.server 8000
# Then visit: http://localhost:8000/frontend/
```

Option C: Use the quick start script
```bash
python run_system.py
```

---

## Project Structure

```
ElectricityAI/
├── frontend/
│   ├── index.html          # Main dashboard
│   ├── styles.css          # Dashboard styling
│   └── app.js              # Frontend logic & charts
│
├── backend/
│   ├── app.py              # Flask API server
│   ├── train_models.py     # Model training pipeline
│   ├── models_manager.py   # Model training implementations
│   └── __init__.py
│
├── models/                 # Trained ML models storage
│   ├── arima_model.pkl
│   ├── sarima_model.pkl
│   ├── prophet_model.pkl
│   ├── lstm_model.h5
│   └── model_info.json
│
├── data/                   # Data storage
│   └── sample_electricity.csv
│
├── utils/
│   ├── data_processor.py   # Data cleaning & preprocessing
│   ├── metrics.py          # Performance metrics
│   └── __init__.py
│
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── setup.bat               # Windows setup script
├── setup.sh                # Linux/Mac setup script
├── run_system.py           # Quick start script
├── README.md               # Project overview
└── SETUP_GUIDE.md          # This file
```

---

## API Endpoints

### GET `/api/status`
Get system and models status
```json
{
  "status": "ready",
  "models_loaded": true,
  "total_predictions": 42
}
```

### POST `/api/predict`
Generate electricity demand forecast
```json
{
  "days_ahead": 7,
  "model_type": "best"
}
```

### GET `/api/models/best`
Get best performing model info

### GET `/api/models/comparison`
Compare all models' performance

### GET `/api/historical`
Get historical actual vs predicted data

### GET `/api/insights`
Get trend analysis and seasonal patterns

### GET `/api/logs`
Get prediction history logs

### POST `/api/clear-logs`
Clear prediction logs

---

## Dashboard Features

### 📊 Dashboard Tab
- Real-time metrics cards
- Forecast generation with custom parameters
- Interactive forecast chart
- Historical vs predicted comparison

### 📈 Models Tab
- Performance comparison table (RMSE, MAE, MAPE, R², Accuracy)
- Highlight best performing model
- Performance comparison chart

### 📅 Insights Tab
- Seasonal patterns analysis
- Current trend information
- Anomaly detection
- Forecast confidence level
- Demand decomposition chart

### 📝 Logs Tab
- Complete prediction history
- System health status
- Download logs as CSV
- Clear logs functionality

---

## Configuration

Edit `config.py` to customize:

```python
# Data preprocessing
DATA_CONFIG = {
    'test_size': 0.2,
    'missing_value_threshold': 0.5,
    'outlier_method': 'iqr',
}

# Model parameters
MODELS_CONFIG = {
    'arima': {'order': (5, 1, 2)},
    'sarima': {'order': (1, 1, 1), 'seasonal_order': (1, 1, 1, 12)},
    'prophet': {'yearly_seasonality': True},
    'lstm': {'sequence_length': 24, 'epochs': 50}
}

# API settings
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'max_forecast_days': 90
}
```

---

## Troubleshooting

### Issue: "Python is not installed"
**Solution:** Download Python 3.8+ from https://www.python.org/downloads/

### Issue: ModuleNotFoundError
**Solution:** Make sure venv is activated and all packages installed:
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution:** Change port in `config.py`:
```python
API_CONFIG = {'port': 5001}  # Use different port
```

### Issue: LSTM training is very slow
**Solution:** Reduce sequence length or epochs in `config.py`:
```python
'lstm': {
    'sequence_length': 12,  # Reduce from 24
    'epochs': 25  # Reduce from 50
}
```

### Issue: Models not loading
**Solution:** Make sure you've trained models first:
```bash
python backend/train_models.py --data_path data/sample_electricity.csv
```

### Issue: Dashboard doesn't connect to API
**Solution:** Check if Flask server is running at http://localhost:5000

---

## Model Selection Guide

| Model | Use Case | Pros | Cons |
|-------|----------|------|------|
| **ARIMA** | Linear trends | Interpretable, fast | Limited for complex patterns |
| **SARIMA** | Seasonal data | Handles seasonality | Longer training time |
| **Prophet** | High-level patterns | Robust, good for gaps | Less precise |
| **LSTM** | Complex patterns | Best accuracy, learns trends | Slow, requires more data |

---

## Performance Tips

1. **Use more data (6+ months)** for better LSTM training
2. **Adjust seasonality period** if your data has different patterns
3. **Tune LSTM hyperparameters** for your specific use case
4. **Use GPU** for faster LSTM training (install CUDA/cuDNN)

---

## Data Format

Your CSV should have at least 100 data points. Supported formats:

```csv
# Format 1: Hourly data
timestamp,demand
2024-01-01 00:00:00,85.2

# Format 2: Daily data
date,consumption
2024-01-01,2100.5

# Format 3: With additional columns (extra columns are ignored)
timestamp,demand,temperature,humidity
2024-01-01 00:00:00,85.2,22.5,65
```

---

## Advanced Usage

### Custom Model Training
```python
from backend.models_manager import ModelsManager
from utils.data_processor import DataProcessor

config = {...}
processor = DataProcessor(config)
manager = ModelsManager(config)

# Load and process data
df = processor.load_data('data/your_data.csv')
df = processor.clean_data(df)

# Train specific model
manager.train_lstm(df['demand'].values)
manager.save_models('models/')
```

### Using the API Programmatically
```python
import requests

response = requests.post('http://localhost:5000/api/predict', json={
    'days_ahead': 14,
    'model_type': 'lstm'
})

predictions = response.json()['predictions']
```

---

## Support & Contributing

For issues or questions:
1. Check this guide's troubleshooting section
2. Review log files in `logs/` directory
3. Check Flask console output for error details

---

## License

MIT License - See LICENSE file

---

## Next Steps

1. ✅ Train models on your data
2. ✅ Monitor forecast accuracy
3. ✅ Adjust model parameters
4. ✅ Deploy to production
5. ✅ Set up automated retraining

Happy Forecasting! ⚡
