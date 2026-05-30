# Electricity Demand Forecasting System

A comprehensive web application for predicting electricity demand using multiple machine learning models (ARIMA, SARIMA, Prophet, LSTM) with a modern dashboard for visualization and model comparison.

## Features

- **Multiple ML Models**: ARIMA, SARIMA, Prophet, LSTM
- **Automatic Model Selection**: Compares models and selects the best performer
- **Interactive Dashboard**: Real-time visualization with White.js
- **Model Comparison**: RMSE, MAE, and accuracy metrics
- **Explainability**: Trend insights and seasonal pattern analysis
- **API Monitoring**: Status tracking and prediction logs
- **Data Processing**: Automated cleaning, feature engineering, and missing value handling

## Project Structure

```
ElectricityAI/
├── frontend/              # White.js UI dashboard
├── backend/               # Flask API server
├── models/                # Trained ML models (.pkl files)
├── data/                  # Raw and processed data
├── utils/                 # Helper functions and utilities
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Data

Place your electricity consumption CSV in `data/` folder with columns:
- `timestamp` (datetime)
- `demand` (electricity consumption)

### 4. Train Models

```bash
python backend/train_models.py --data_path data/your_data.csv
```

### 5. Run Backend Server

```bash
python backend/app.py
```

Server runs on `http://localhost:5000`

### 6. Open Dashboard

Open `frontend/index.html` in your browser or set up a local server:

```bash
python -m http.server 8000  # Then visit http://localhost:8000/frontend/
```

## API Endpoints

### GET `/api/status`
System health and model information

### POST `/api/predict`
Get electricity demand predictions
```json
{
  "days_ahead": 7,
  "model_type": "best"
}
```

### GET `/api/models/comparison`
Model performance comparison metrics

### GET `/api/models/best`
Get best performing model info

### GET `/api/historical`
Historical actual vs predicted data

### GET `/api/insights`
Trend analysis and seasonal patterns

### GET `/api/logs`
Prediction logs and history

## Model Performance Metrics

- **RMSE** (Root Mean Squared Error): Lower is better
- **MAE** (Mean Absolute Error): Lower is better
- **MAPE** (Mean Absolute Percentage Error): Percentage error
- **Accuracy**: Based on directional predictions

## Explainability Features

- Seasonal decomposition analysis
- Peak usage time identification
- Trend patterns and anomaly detection
- Model prediction confidence scores

## Configuration

Edit `config.py` to customize:
- Model parameters
- Data preprocessing settings
- API settings
- Logging levels

## Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)
- 2GB RAM minimum
- 500MB disk space for models

## Troubleshooting

### Model Training Issues
- Ensure CSV has correct column names
- Check data has no all-NaN columns
- Verify timestamps are in correct format

### LSTM Training Slow
- Reduce sequence length in config.py
- Use GPU if available
- Reduce number of epochs

### API Connection Error
- Ensure Flask server is running
- Check CORS settings in backend/app.py
- Verify port 5000 is not in use

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please follow PEP 8 style guide and add tests for new features.
