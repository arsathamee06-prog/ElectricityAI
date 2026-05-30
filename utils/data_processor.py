"""
Data processing utilities for cleaning and preprocessing electricity data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime
import joblib
import os

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handle data loading, cleaning, and preprocessing"""
    
    def __init__(self, config_dict=None):
        # Accept either a config module or a config dict
        if config_dict is None:
            # Use default config values
            self.config = {
                'test_size': 0.2,
                'validation_size': 0.1,
                'missing_value_threshold': 0.5,
                'outlier_method': 'iqr',
                'outlier_threshold': 3,
            }
        elif hasattr(config_dict, 'DATA_CONFIG'):
            # It's a config module
            self.config = config_dict.DATA_CONFIG
        else:
            # It's already a dict
            self.config = config_dict
        
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, file_path):
        """Load CSV data"""
        try:
            self.logger.info(f"Loading data from {file_path}")
            df = pd.read_csv(file_path)
            
            # Ensure we have required columns
            if 'timestamp' not in df.columns and 'date' not in df.columns:
                raise ValueError("CSV must contain 'timestamp' or 'date' column")
            
            if 'demand' not in df.columns:
                # Try to find a column with demand-like names
                demand_cols = [col for col in df.columns if 'demand' in col.lower() or 'consumption' in col.lower() or 'usage' in col.lower()]
                if demand_cols:
                    df = df.rename(columns={demand_cols[0]: 'demand'})
                else:
                    raise ValueError("CSV must contain 'demand' column (or similar)")
            
            # Parse timestamp
            date_col = 'timestamp' if 'timestamp' in df.columns else 'date'
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.rename(columns={date_col: 'timestamp'})
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            self.logger.info(f"Data loaded: {len(df)} rows, date range {df['timestamp'].min()} to {df['timestamp'].max()}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_data(self, df):
        """Handle missing values and outliers"""
        try:
            self.logger.info("Starting data cleaning...")
            df = df.copy()
            
            # Handle missing values
            initial_nulls = df.isnull().sum().sum()
            
            # Drop columns with too many missing values
            threshold = len(df) * self.config.get('missing_value_threshold', 0.5)
            df = df.dropna(axis=1, thresh=len(df) - threshold)
            
            # Interpolate missing values for demand
            if df['demand'].isnull().any():
                df['demand'] = df['demand'].interpolate(method='linear', limit_direction='both')
                df['demand'] = df['demand'].fillna(df['demand'].mean())
            
            # Handle outliers
            method = self.config.get('outlier_method', 'iqr')
            Q1 = df['demand'].quantile(0.25)
            Q3 = df['demand'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((df['demand'] < lower_bound) | (df['demand'] > upper_bound)).sum()
            df['demand'] = df['demand'].clip(lower_bound, upper_bound)
            
            self.logger.info(f"Cleaning completed: {initial_nulls} nulls fixed, {outliers} outliers handled")
            return df
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            raise
    
    def feature_engineering(self, df):
        """Create additional features for models"""
        try:
            self.logger.info("Performing feature engineering...")
            df = df.copy()
            
            # Time-based features
            df['year'] = df['timestamp'].dt.year
            df['month'] = df['timestamp'].dt.month
            df['day'] = df['timestamp'].dt.day
            df['dayofweek'] = df['timestamp'].dt.dayofweek
            df['dayofyear'] = df['timestamp'].dt.dayofyear
            df['quarter'] = df['timestamp'].dt.quarter
            df['week'] = df['timestamp'].dt.isocalendar().week
            
            # Lag features (previous days)
            for lag in [1, 7, 14]:
                if lag < len(df):
                    df[f'lag_{lag}'] = df['demand'].shift(lag)
            
            # Rolling statistics
            for window in [7, 14]:
                if window < len(df):
                    df[f'rolling_mean_{window}'] = df['demand'].rolling(window=window).mean()
                    df[f'rolling_std_{window}'] = df['demand'].rolling(window=window).std()
            
            # Drop rows with NaN from lag and rolling features
            df = df.dropna().reset_index(drop=True)
            
            self.logger.info(f"Features created: {len(df.columns)} columns, {len(df)} rows after cleaning")
            return df
        except Exception as e:
            self.logger.error(f"Error in feature engineering: {str(e)}")
            raise
    
    def scale_data(self, data, fit=False):
        """Scale data for LSTM and other models"""
        if fit:
            scaled = self.scaler.fit_transform(data.reshape(-1, 1))
        else:
            scaled = self.scaler.transform(data.reshape(-1, 1))
        return scaled.flatten()
    
    def inverse_scale(self, scaled_data):
        """Inverse transform scaled data"""
        return self.scaler.inverse_transform(scaled_data.reshape(-1, 1)).flatten()
    
    def save_scaler(self, path):
        """Save scaler for later use"""
        joblib.dump(self.scaler, path)
        self.logger.info(f"Scaler saved to {path}")
    
    def load_scaler(self, path):
        """Load saved scaler"""
        self.scaler = joblib.load(path)
        self.logger.info(f"Scaler loaded from {path}")
    
    def create_sequences(self, data, seq_length):
        """Create sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    def split_data(self, df, test_size=None, validation_size=None):
        """Split data into train, validation, and test sets"""
        # Use provided sizes or defaults from config
        if test_size is None:
            test_size = self.config.get('test_size', 0.2)
        if validation_size is None:
            validation_size = self.config.get('validation_size', 0.1)
            
        n = len(df)
        train_idx = int(n * (1 - test_size - validation_size))
        val_idx = int(n * (1 - test_size))
        
        train = df[:train_idx]
        val = df[train_idx:val_idx]
        test = df[val_idx:]
        
        self.logger.info(f"Data split: train={len(train)}, val={len(val)}, test={len(test)}")
        return train, val, test
