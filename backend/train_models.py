"""
Train machine learning models for electricity demand forecasting
Usage: python backend/train_models.py --data_path data/your_data.csv
"""

import logging
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.data_processor import DataProcessor
from utils.metrics import ModelEvaluator
from backend.models_manager import ModelsManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGGING_CONFIG['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and evaluate all models"""
    
    def __init__(self, config_module):
        # Extract config values from the module
        self.config = config_module
        self.data_processor = DataProcessor(config_module.DATA_CONFIG)
        self.models_manager = ModelsManager(config_module)
        self.evaluator = ModelEvaluator()
        self.logger = logging.getLogger(__name__)
    
    def train_all_models(self, train_data, val_data, test_data):
        """Train all models"""
        self.logger.info("=" * 50)
        self.logger.info("Starting Model Training")
        self.logger.info("=" * 50)
        
        predictions = {}
        
        # Train ARIMA
        self.logger.info("\n[1/4] Training ARIMA...")
        self.models_manager.train_arima(train_data['demand'])
        arima_pred = self.models_manager.predict_arima(steps=len(test_data))
        predictions['arima'] = arima_pred
        
        # Train SARIMA
        self.logger.info("\n[2/4] Training SARIMA...")
        self.models_manager.train_sarima(train_data['demand'])
        sarima_pred = self.models_manager.predict_sarima(steps=len(test_data))
        predictions['sarima'] = sarima_pred
        
        # Train Prophet
        self.logger.info("\n[3/4] Training Prophet...")
        self.models_manager.train_prophet(train_data)
        prophet_pred = self.models_manager.predict_prophet(steps=len(test_data))
        predictions['prophet'] = prophet_pred
        
        # Train LSTM
        self.logger.info("\n[4/4] Training LSTM...")
        self.models_manager.train_lstm(train_data['demand'].values)
        lstm_pred = self.models_manager.predict_lstm(train_data['demand'].values, steps=len(test_data))
        predictions['lstm'] = lstm_pred
        
        return predictions
    
    def evaluate_and_select_best(self, predictions, test_data):
        """Evaluate models and select best one"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("Model Evaluation")
        self.logger.info("=" * 50)
        
        y_true = test_data['demand'].values
        
        # Evaluate all models
        results = self.evaluator.evaluate_models(predictions, y_true)
        
        # Get best model
        metric = self.config.MODEL_SELECTION['metric']
        best_model, best_metrics = self.evaluator.get_best_model(results, metric=metric)
        
        # Format and display results
        formatted = self.evaluator.format_results(results, best_model)
        
        self.logger.info("\nModel Performance Comparison:")
        self.logger.info("-" * 50)
        for model_name, metrics in formatted.items():
            self.logger.info(f"\n{model_name.upper()}:")
            for key, value in metrics.items():
                self.logger.info(f"  {key}: {value}")
        
        self.logger.info("\n" + "=" * 50)
        self.logger.info(f"BEST MODEL: {best_model.upper()} ({metric}: {best_metrics[metric]:.4f})")
        self.logger.info("=" * 50)
        
        return best_model, results
    
    def save_results(self, best_model, results):
        """Save models and results"""
        self.logger.info("\nSaving models...")
        
        # Save all models
        self.models_manager.save_models(self.config.MODELS_DIR)
        
        # Save best model indicator
        best_model_info = {
            'best_model': best_model,
            'training_date': datetime.now().isoformat(),
            'metrics': {name: {k: v.item() if hasattr(v, 'item') else v for k, v in metrics.items()} 
                       if metrics else {} 
                       for name, metrics in results.items()}
        }
        
        import json
        info_path = os.path.join(self.config.MODELS_DIR, 'model_info.json')
        with open(info_path, 'w') as f:
            json.dump(best_model_info, f, indent=2, default=str)
        
        self.logger.info(f"Model info saved to {info_path}")
    
    def run(self, data_path):
        """Main training pipeline"""
        try:
            # Load and process data
            self.logger.info(f"Loading data from {data_path}")
            df = self.data_processor.load_data(data_path)
            
            self.logger.info("Cleaning data...")
            df = self.data_processor.clean_data(df)
            
            self.logger.info("Feature engineering...")
            df = self.data_processor.feature_engineering(df)
            
            # Split data
            train_data, val_data, test_data = self.data_processor.split_data(
                df,
                test_size=self.config.DATA_CONFIG['test_size'],
                validation_size=self.config.DATA_CONFIG['validation_size']
            )
            
            # Train all models
            predictions = self.train_all_models(train_data, val_data, test_data)
            
            # Evaluate and select best
            best_model, results = self.evaluate_and_select_best(predictions, test_data)
            
            # Save results
            self.save_results(best_model, results)
            
            self.logger.info("\n✓ Training pipeline completed successfully!")
            return best_model, results
        
        except Exception as e:
            self.logger.error(f"\n✗ Training failed: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Train electricity demand forecasting models')
    parser.add_argument('--data_path', required=True, help='Path to electricity data CSV')
    args = parser.parse_args()
    
    if not os.path.exists(args.data_path):
        logger.error(f"Data file not found: {args.data_path}")
        sys.exit(1)
    
    trainer = ModelTrainer(config)
    trainer.run(args.data_path)


if __name__ == '__main__':
    main()
