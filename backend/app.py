"""
Flask API for Electricity Demand Forecasting System
"""

import logging
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS
import config
from backend.models_manager import ModelsManager
from utils.metrics import MetricsCalculator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOGGING_CONFIG['level']),
    format=config.LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(config.LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize models manager
models_manager = ModelsManager(config)

# Global state
app.model_info = {}
app.prediction_logs = []
app.status_data = {
    'api_status': 'initializing',
    'models_loaded': False,
    'last_prediction': None,
    'total_predictions': 0,
}


def load_models():
    """Load trained models on startup"""
    try:
        models_manager.load_models(config.MODELS_DIR)
        
        # Load model info
        info_path = os.path.join(config.MODELS_DIR, 'model_info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                app.model_info = json.load(f)
        
        app.status_data['models_loaded'] = True
        app.status_data['api_status'] = 'ready'
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load models: {str(e)}")
        app.status_data['api_status'] = 'models_not_found'


def log_prediction(model_used, predictions, forecast_days):
    """Log prediction for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'model': model_used,
        'forecast_days': forecast_days,
        'predictions_count': len(predictions) if predictions is not None else 0
    }
    app.prediction_logs.append(log_entry)
    
    # Keep only last 1000 logs
    if len(app.prediction_logs) > 1000:
        app.prediction_logs = app.prediction_logs[-1000:]
    
    app.status_data['last_prediction'] = log_entry
    app.status_data['total_predictions'] += 1


# ============ API Routes ============

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API and models status"""
    return jsonify({
        'status': app.status_data['api_status'],
        'models_loaded': app.status_data['models_loaded'],
        'available_models': list(models_manager.models.keys()),
        'timestamp': datetime.now().isoformat(),
        'total_predictions': app.status_data['total_predictions'],
        'last_prediction': app.status_data['last_prediction']
    }), 200


@app.route('/api/models/best', methods=['GET'])
def get_best_model():
    """Get best performing model info"""
    if not app.model_info:
        return jsonify({'error': 'No model info available'}), 404
    
    return jsonify({
        'best_model': app.model_info.get('best_model'),
        'training_date': app.model_info.get('training_date'),
        'metrics': app.model_info.get('metrics', {}).get(app.model_info.get('best_model'))
    }), 200


@app.route('/api/models/comparison', methods=['GET'])
def get_models_comparison():
    """Get all models performance comparison"""
    if not app.model_info:
        return jsonify({'error': 'No model info available'}), 404
    
    metrics = app.model_info.get('metrics', {})
    best_model = app.model_info.get('best_model')
    
    comparison = {}
    for model_name, model_metrics in metrics.items():
        comparison[model_name] = {
            'metrics': model_metrics,
            'is_best': model_name == best_model
        }
    
    return jsonify({
        'comparison': comparison,
        'best_model': best_model,
        'training_date': app.model_info.get('training_date')
    }), 200


@app.route('/api/predict', methods=['POST'])
def predict():
    """Make electricity demand predictions"""
    try:
        data = request.json
        
        if not models_manager.models:
            return jsonify({'error': 'Models not loaded'}), 503
        
        # Get parameters
        days_ahead = min(data.get('days_ahead', 7), config.API_CONFIG['max_forecast_days'])
        model_type = data.get('model_type', 'best')
        
        if model_type == 'best':
            model_type = app.model_info.get('best_model', 'arima')
        
        if model_type not in models_manager.models:
            return jsonify({'error': f'Model {model_type} not available'}), 400
        
        # Make prediction based on model type
        predictions = None
        
        if model_type == 'arima':
            predictions = models_manager.predict_arima(steps=days_ahead)
        elif model_type == 'sarima':
            predictions = models_manager.predict_sarima(steps=days_ahead)
        elif model_type == 'prophet':
            predictions = models_manager.predict_prophet(steps=days_ahead)
        elif model_type == 'lstm':
            # For LSTM, we need historical data - generate synthetic for demo
            historical = np.random.normal(100, 20, 100)
            predictions = models_manager.predict_lstm(historical, steps=days_ahead)
        
        if predictions is None:
            return jsonify({'error': f'Prediction failed for {model_type}'}), 500
        
        # Log prediction
        log_prediction(model_type, predictions, days_ahead)
        
        # Generate forecast dates
        forecast_dates = [
            (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            for i in range(len(predictions))
        ]
        
        return jsonify({
            'model': model_type,
            'forecast_days': days_ahead,
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
            'dates': forecast_dates,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get trend insights and seasonal patterns"""
    try:
        insights = {
            'seasonal_patterns': {
                'peak_hours': [18, 19, 20],  # Example peak hours
                'off_peak_hours': [2, 3, 4, 5],
                'seasonal_variation': 'Higher in winter and summer, lower in spring and fall'
            },
            'trends': {
                'overall_trend': 'Slight upward trend',
                'year_over_year_change': '+3.5%',
                'month_over_month_change': '+1.2%'
            },
            'anomalies': {
                'recent_events': [],
                'forecasted_anomalies': []
            }
        }
        
        return jsonify(insights), 200
    except Exception as e:
        logger.error(f"Insights error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get prediction logs"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'logs': app.prediction_logs[-limit:],
        'total': len(app.prediction_logs)
    }), 200


@app.route('/api/historical', methods=['GET'])
def get_historical():
    """Get historical actual vs predicted data"""
    try:
        # This would typically load from database/cache
        # For demo, return synthetic data
        days = request.args.get('days', 30, type=int)
        dates = [
            (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d')
            for i in range(days)
        ]
        
        # Synthetic historical data
        actual = np.random.normal(100, 15, days).tolist()
        predicted = [a + np.random.normal(0, 5) for a in actual]
        
        return jsonify({
            'dates': dates,
            'actual': actual,
            'predicted': predicted
        }), 200
    except Exception as e:
        logger.error(f"Historical data error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Clear prediction logs"""
    app.prediction_logs = []
    return jsonify({'message': 'Logs cleared'}), 200


# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============ Application Startup ============

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Electricity Demand Forecasting API")
    logger.info("=" * 50)
    
    # Load models
    load_models()
    
    # Run Flask app
    app.run(
        host=config.API_CONFIG['host'],
        port=config.API_CONFIG['port'],
        debug=config.API_CONFIG['debug']
    )
