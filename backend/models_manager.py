"""
Machine Learning models manager - handles training and predictions
"""

import logging
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

# Try to import all required libraries
try:
    from statsmodels.tsa.arima.model import ARIMA
except:
    ARIMA = None

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except:
    SARIMAX = None

try:
    from prophet import Prophet
except:
    Prophet = None

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
except:
    Sequential = None

logger = logging.getLogger(__name__)


class ModelsManager:
    """Manage training and predictions for all models"""
    
    def __init__(self, config_module):
        # Extract config properly if it's a module
        if hasattr(config_module, 'MODELS_CONFIG'):
            self.models_config = config_module.MODELS_CONFIG
        else:
            self.models_config = config_module.get('MODELS_CONFIG', {})
            
        if hasattr(config_module, 'MODELS_DIR'):
            self.models_dir = config_module.MODELS_DIR
        else:
            self.models_dir = config_module.get('MODELS_DIR', 'models')
            
        self.models = {}
        self.scalers = {}
        self.logger = logging.getLogger(__name__)
    
    # ============ ARIMA Model ============
    def train_arima(self, data):
        """Train ARIMA model"""
        try:
            if ARIMA is None:
                self.logger.warning("ARIMA not available")
                return None
            
            self.logger.info("Training ARIMA model...")
            order = self.models_config.get('arima', {}).get('order', (5, 1, 2))
            
            model = ARIMA(data, order=order)
            fitted_model = model.fit()
            
            self.logger.info(f"ARIMA model trained successfully")
            self.models['arima'] = fitted_model
            return fitted_model
        except Exception as e:
            self.logger.error(f"Error training ARIMA: {str(e)}")
            return None
    
    def predict_arima(self, steps=7):
        """Make predictions with ARIMA"""
        try:
            if 'arima' not in self.models or self.models['arima'] is None:
                return None
            
            forecast = self.models['arima'].get_forecast(steps=steps)
            predictions = forecast.predicted_mean.values
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting with ARIMA: {str(e)}")
            return None
    
    # ============ SARIMA Model ============
    def train_sarima(self, data):
        """Train SARIMA model"""
        try:
            if SARIMAX is None:
                self.logger.warning("SARIMA not available")
                return None
            
            self.logger.info("Training SARIMA model...")
            order = self.models_config.get('sarima', {}).get('order', (1, 1, 1))
            seasonal_order = self.models_config.get('sarima', {}).get('seasonal_order', (1, 1, 1, 12))
            
            model = SARIMAX(data, order=order, seasonal_order=seasonal_order)
            fitted_model = model.fit(disp=False)
            
            self.logger.info(f"SARIMA model trained successfully")
            self.models['sarima'] = fitted_model
            return fitted_model
        except Exception as e:
            self.logger.error(f"Error training SARIMA: {str(e)}")
            return None
    
    def predict_sarima(self, steps=7):
        """Make predictions with SARIMA"""
        try:
            if 'sarima' not in self.models or self.models['sarima'] is None:
                return None
            
            forecast = self.models['sarima'].get_forecast(steps=steps)
            predictions = forecast.predicted_mean.values
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting with SARIMA: {str(e)}")
            return None
    
    # ============ Prophet Model ============
    def train_prophet(self, df):
        """Train Prophet model"""
        try:
            if Prophet is None:
                self.logger.warning("Prophet not available")
                return None
            
            self.logger.info("Training Prophet model...")
            
            # Prepare data for Prophet
            prophet_df = pd.DataFrame({
                'ds': df['timestamp'],
                'y': df['demand']
            })
            
            prophet_config = self.models_config.get('prophet', {})
            model = Prophet(
                yearly_seasonality=prophet_config.get('yearly_seasonality', True),
                weekly_seasonality=prophet_config.get('weekly_seasonality', True),
                daily_seasonality=prophet_config.get('daily_seasonality', False),
                seasonality_mode=prophet_config.get('seasonality_mode', 'additive'),
                interval_width=prophet_config.get('interval_width', 0.95)
            )
            
            model.fit(prophet_df)
            
            self.logger.info(f"Prophet model trained successfully")
            self.models['prophet'] = model
            return model
        except Exception as e:
            self.logger.error(f"Error training Prophet: {str(e)}")
            return None
    
    def predict_prophet(self, steps=7):
        """Make predictions with Prophet"""
        try:
            if 'prophet' not in self.models or self.models['prophet'] is None:
                return None
            
            future = self.models['prophet'].make_future_dataframe(periods=steps, freq='D')
            forecast = self.models['prophet'].predict(future)
            predictions = forecast['yhat'].tail(steps).values
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting with Prophet: {str(e)}")
            return None
    
    # ============ LSTM Model ============
    def train_lstm(self, data):
        """Train LSTM model"""
        try:
            if Sequential is None:
                self.logger.warning("LSTM not available (TensorFlow required)")
                return None
            
            self.logger.info("Training LSTM model...")
            
            # Normalize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data.reshape(-1, 1)).flatten()
            self.scalers['lstm'] = scaler
            
            # Create sequences
            lstm_config = self.models_config.get('lstm', {})
            seq_length = lstm_config.get('sequence_length', 24)
            X, y = self._create_sequences(scaled_data, seq_length)
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Build model
            lstm_units = lstm_config.get('lstm_units', 64)
            dense_units = lstm_config.get('dense_units', 32)
            dropout = lstm_config.get('dropout', 0.2)
            
            model = Sequential([
                LSTM(lstm_units, activation='relu', input_shape=(seq_length, 1)),
                Dropout(dropout),
                Dense(dense_units, activation='relu'),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(), loss='mse', metrics=['mae'])
            
            # Train
            epochs = lstm_config.get('epochs', 50)
            batch_size = lstm_config.get('batch_size', 32)
            
            model.fit(
                X_train.reshape(-1, seq_length, 1),
                y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val.reshape(-1, seq_length, 1), y_val),
                verbose=0
            )
            
            self.logger.info(f"LSTM model trained successfully")
            self.models['lstm'] = model
            return model
        except Exception as e:
            self.logger.error(f"Error training LSTM: {str(e)}")
            return None
    
    def predict_lstm(self, data, steps=7):
        """Make predictions with LSTM"""
        try:
            if 'lstm' not in self.models or self.models['lstm'] is None:
                return None
            
            scaler = self.scalers.get('lstm')
            if scaler is None:
                return None
            
            seq_length = self.models_config.get('lstm', {}).get('sequence_length', 24)
            
            # Normalize input data
            scaled_data = scaler.transform(data.reshape(-1, 1)).flatten()
            
            predictions = []
            current_seq = scaled_data[-seq_length:].copy()
            
            for _ in range(steps):
                next_pred = self.models['lstm'].predict(
                    current_seq.reshape(1, seq_length, 1),
                    verbose=0
                )[0, 0]
                predictions.append(next_pred)
                current_seq = np.append(current_seq[1:], next_pred)
            
            # Inverse scale predictions
            predictions = np.array(predictions).reshape(-1, 1)
            predictions = scaler.inverse_transform(predictions).flatten()
            
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting with LSTM: {str(e)}")
            return None
    
    # ============ Utility Methods ============
    def _create_sequences(self, data, seq_length):
        """Create sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    def save_models(self, models_dir):
        """Save all trained models"""
        try:
            os.makedirs(models_dir, exist_ok=True)
            
            for model_name, model in self.models.items():
                if model_name == 'lstm':
                    path = os.path.join(models_dir, f'{model_name}_model.h5')
                    model.save(path)
                else:
                    path = os.path.join(models_dir, f'{model_name}_model.pkl')
                    joblib.dump(model, path)
                
                self.logger.info(f"Saved {model_name} model to {path}")
            
            # Save scalers
            for scaler_name, scaler in self.scalers.items():
                path = os.path.join(models_dir, f'{scaler_name}_scaler.pkl')
                joblib.dump(scaler, path)
                self.logger.info(f"Saved {scaler_name} scaler to {path}")
        except Exception as e:
            self.logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self, models_dir):
        """Load trained models"""
        try:
            for model_name in ['arima', 'sarima', 'prophet']:
                path = os.path.join(models_dir, f'{model_name}_model.pkl')
                if os.path.exists(path):
                    self.models[model_name] = joblib.load(path)
                    self.logger.info(f"Loaded {model_name} model")
            
            # Load LSTM if available
            lstm_path = os.path.join(models_dir, 'lstm_model.h5')
            if os.path.exists(lstm_path) and Sequential is not None:
                from tensorflow.keras.models import load_model
                self.models['lstm'] = load_model(lstm_path)
                self.logger.info(f"Loaded lstm model")
            
            # Load scalers
            for scaler_name in ['lstm']:
                path = os.path.join(models_dir, f'{scaler_name}_scaler.pkl')
                if os.path.exists(path):
                    self.scalers[scaler_name] = joblib.load(path)
                    self.logger.info(f"Loaded {scaler_name} scaler")
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
