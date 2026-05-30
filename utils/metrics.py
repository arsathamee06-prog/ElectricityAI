"""
Metrics calculation and model evaluation utilities
"""

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate model performance metrics"""
    
    @staticmethod
    def rmse(y_true, y_pred):
        """Root Mean Squared Error"""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def mae(y_true, y_pred):
        """Mean Absolute Error"""
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def mape(y_true, y_pred):
        """Mean Absolute Percentage Error"""
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        mask = y_true != 0
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    @staticmethod
    def r2(y_true, y_pred):
        """R-squared score"""
        return r2_score(y_true, y_pred)
    
    @staticmethod
    def directional_accuracy(y_true, y_pred):
        """Percentage of correct directional predictions"""
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        if len(y_true) < 2:
            return 0
        
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        
        correct = (true_direction == pred_direction).sum()
        return (correct / len(true_direction)) * 100
    
    @staticmethod
    def calculate_all_metrics(y_true, y_pred):
        """Calculate all metrics at once"""
        return {
            'rmse': MetricsCalculator.rmse(y_true, y_pred),
            'mae': MetricsCalculator.mae(y_true, y_pred),
            'mape': MetricsCalculator.mape(y_true, y_pred),
            'r2': MetricsCalculator.r2(y_true, y_pred),
            'directional_accuracy': MetricsCalculator.directional_accuracy(y_true, y_pred),
        }


class ModelEvaluator:
    """Evaluate and compare models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_models(self, models_predictions, y_true):
        """
        Evaluate multiple models
        
        Args:
            models_predictions: dict with model_name: y_pred
            y_true: actual values
        
        Returns:
            dict with model_name: metrics
        """
        results = {}
        for model_name, y_pred in models_predictions.items():
            if y_pred is not None and len(y_pred) == len(y_true):
                results[model_name] = MetricsCalculator.calculate_all_metrics(y_true, y_pred)
                self.logger.info(f"{model_name} - RMSE: {results[model_name]['rmse']:.4f}, MAE: {results[model_name]['mae']:.4f}")
            else:
                self.logger.warning(f"{model_name}: Invalid predictions")
                results[model_name] = None
        
        return results
    
    def get_best_model(self, results, metric='rmse'):
        """Get best model based on metric"""
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if not valid_results:
            return None, None
        
        if metric in ['rmse', 'mae', 'mape']:
            # Lower is better
            best_model = min(valid_results, key=lambda x: valid_results[x][metric])
        elif metric in ['r2', 'directional_accuracy']:
            # Higher is better
            best_model = max(valid_results, key=lambda x: valid_results[x][metric])
        else:
            best_model = list(valid_results.keys())[0]
        
        return best_model, valid_results[best_model]
    
    def format_results(self, results, best_model=None):
        """Format results for display"""
        formatted = {}
        for model_name, metrics in results.items():
            if metrics is None:
                formatted[model_name] = {'error': 'Training failed'}
            else:
                formatted[model_name] = {
                    'rmse': f"{metrics['rmse']:.2f}",
                    'mae': f"{metrics['mae']:.2f}",
                    'mape': f"{metrics['mape']:.2f}%",
                    'r2': f"{metrics['r2']:.4f}",
                    'directional_accuracy': f"{metrics['directional_accuracy']:.2f}%",
                    'best': model_name == best_model
                }
        
        return formatted
