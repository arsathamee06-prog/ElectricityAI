"""
Configuration settings for Electricity Demand Forecasting System
"""

import os
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Data Processing
DATA_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.1,
    'missing_value_threshold': 0.5,  # Drop columns with >50% missing values
    'outlier_method': 'iqr',  # 'iqr' or 'zscore'
    'outlier_threshold': 3,
}

# Time Series Models Configuration
MODELS_CONFIG = {
    'arima': {
        'order': (5, 1, 2),
        'seasonal_order': None,
    },
    'sarima': {
        'order': (1, 1, 1),
        'seasonal_order': (1, 1, 1, 12),  # 12 for monthly seasonality
    },
    'prophet': {
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'daily_seasonality': False,
        'seasonality_mode': 'additive',
        'interval_width': 0.95,
    },
    'lstm': {
        'sequence_length': 24,  # 24 days lookback
        'epochs': 50,
        'batch_size': 32,
        'validation_split': 0.2,
        'dropout': 0.2,
        'lstm_units': 64,
        'dense_units': 32,
    },
}

# Model Selection
MODEL_SELECTION = {
    'metric': 'rmse',  # 'rmse', 'mae', or 'mape'
    'test_period_days': 30,
}

# API Configuration
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'max_forecast_days': 90,
    'default_forecast_days': 7,
}

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
}

# Forecasting
FORECAST_CONFIG = {
    'min_data_points': 100,
    'future_periods_default': 7,
    'confidence_interval': 0.95,
}

# Model paths
MODEL_PATHS = {
    'arima': os.path.join(MODELS_DIR, 'arima_model.pkl'),
    'sarima': os.path.join(MODELS_DIR, 'sarima_model.pkl'),
    'prophet': os.path.join(MODELS_DIR, 'prophet_model.pkl'),
    'lstm': os.path.join(MODELS_DIR, 'lstm_model.h5'),
    'best': os.path.join(MODELS_DIR, 'best_model.pkl'),
    'scaler': os.path.join(MODELS_DIR, 'scaler.pkl'),
}

# Performance tracking
TRACKING_CONFIG = {
    'save_predictions': True,
    'prediction_log_file': os.path.join(LOGS_DIR, 'predictions.log'),
    'max_log_entries': 10000,
}
