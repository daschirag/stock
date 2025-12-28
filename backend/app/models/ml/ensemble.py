"""
Ensemble framework combining BiLSTM, CNN-LSTM, and XGBoost predictions.
Uses Bayesian optimization for weight tuning.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from app.core import settings, get_logger


logger = get_logger(__name__)


class EnsembleModel:
    """
    Weighted stacking ensemble combining predictions from multiple models.
    
    Models:
    1. BiLSTM-Attention (high-frequency IMFs)
    2. CNN-LSTM (mid-frequency IMFs  
    3. XGBoost (low-frequency IMFs)
    4. Sentiment score (weighted)
    
    Weights optimized using Bayesian optimization.
    """
    
    def __init__(
        self,
        models: Optional[List] = None,
        n_optimization_trials: int = 50
    ):
        """
        Initialize ensemble model.
        
        Args:
            models: List of trained models
            n_optimization_trials: Number of Bayesian optimization trials
        """
        self.models = models or []
        self.n_optimization_trials = n_optimization_trials
        self.weights = None
        self.optuna_available = self._check_optuna()
        
        logger.info(f"Initializing Ensemble with {len(self.models)} models")
    
    def _check_optuna(self) -> bool:
        """Check if Optuna is available."""
        try:
            import optuna
            return True
        except ImportError:
            logger.warning("Optuna not available, will use equal weights")
            return False
    
    def add_model(self, model):
        """Add a model to the ensemble."""
        self.models.append(model)
        logger.info(f"Added model to ensemble. Total models: {len(self.models)}")
    
    def optimize_weights(
        self,
        predictions_list: List[np.ndarray],
        y_true: np.ndarray
    ):
        """
        Optimize ensemble weights using Bayesian optimization.
        
        Args:
            predictions_list: List of prediction arrays from each model
            y_true: True target values
        """
        if self.optuna_available:
            self._optimize_with_optuna(predictions_list, y_true)
        else:
            # Use equal weights as fallback
            self.weights = np.ones(len(predictions_list)) / len(predictions_list)
            logger.info(f"Using equal weights: {self.weights}")
    
    def _optimize_with_optuna(
        self,
        predictions_list: List[np.ndarray],
        y_true: np.ndarray
    ):
        """Optimize weights using Optuna."""
        import optuna
        from sklearn.metrics import mean_squared_error
        
        def objective(trial):
            """Objective function for Optuna."""
            # Suggest weights that sum to 1
            weights = []
            remaining = 1.0
            
            for i in range(len(predictions_list) - 1):
                w = trial.suggest_float(f'weight_{i}', 0.0, remaining)
                weights.append(w)
                remaining -= w
            
            weights.append(remaining)  # Last weight ensures sum = 1
            weights = np.array(weights)
            
            # Weighted prediction
            ensemble_pred = np.zeros_like(predictions_list[0])
            for i, pred in enumerate(predictions_list):
                ensemble_pred += weights[i] * pred
            
            # Calculate MSE
            mse = mean_squared_error(y_true, ensemble_pred)
            return mse
        
        # Create study
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize
        study.optimize(
            objective,
            n_trials=self.n_optimization_trials,
            show_progress_bar=False
        )
        
        # Extract best weights
        best_params = study.best_params
        self.weights = []
        remaining = 1.0
        
        for i in range(len(predictions_list) - 1):
            w = best_params[f'weight_{i}']
            self.weights.append(w)
            remaining -= w
        
        self.weights.append(remaining)
        self.weights = np.array(self.weights)
        
        logger.info(f"Optimized weights: {self.weights}")
        logger.info(f"Best MSE: {study.best_value:.6f}")
    
    def predict(
        self,
        X_high_freq: Optional[np.ndarray] = None,
        X_mid_freq: Optional[np.ndarray] = None,
        X_low_freq: Optional[np.ndarray] = None,
        sentiment_score: Optional[float] = None
    ) -> np.ndarray:
        """
        Make ensemble predictions.
        
        Args:
            X_high_freq: Input for BiLSTM-Attention
            X_mid_freq: Input for CNN-LSTM
            X_low_freq: Input for XGBoost
            sentiment_score: Sentiment score
        
        Returns:
            Ensemble predictions
        """
        predictions = []
        
        # Get predictions from each model
        for i, model in enumerate(self.models):
            if i == 0 and X_high_freq is not None:
                # BiLSTM-Attention
                pred = model.predict(X_high_freq)
                predictions.append(pred)
            elif i == 1 and X_mid_freq is not None:
                # CNN-LSTM
                pred = model.predict(X_mid_freq)
                predictions.append(pred)
            elif i == 2 and X_low_freq is not None:
                # XGBoost
                pred = model.predict(X_low_freq)
                predictions.append(pred)
        
        # Add sentiment prediction if available
        if sentiment_score is not None:
            # Simple sentiment-based adjustment
            sentiment_pred = np.full((len(predictions[0]), 1), sentiment_score)
            predictions.append(sentiment_pred)
        
        # Weighted ensemble
        if self.weights is None:
            # Equal weights if not optimized
            self.weights = np.ones(len(predictions)) / len(predictions)
        
        ensemble_pred = np.zeros_like(predictions[0])
        for i, pred in enumerate(predictions):
            if i < len(self.weights):
                ensemble_pred += self.weights[i] * pred
        
        return ensemble_pred
    
    def predict_with_confidence(
        self,
        X_high_freq: Optional[np.ndarray] = None,
        X_mid_freq: Optional[np.ndarray] = None,
        X_low_freq: Optional[np.ndarray] = None,
        sentiment_score: Optional[float] = None,
        confidence_level: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make predictions with confidence intervals.
        
        Args:
            X_high_freq: Input for BiLSTM-Attention
            X_mid_freq: Input for CNN-LSTM
            X_low_freq: Input for XGBoost
            sentiment_score: Sentiment score
            confidence_level: Confidence level (0-1)
        
        Returns:
            Tuple of (predictions, lower_bound, upper_bound)
        """
        predictions = self.predict(X_high_freq, X_mid_freq, X_low_freq, sentiment_score)
        
        # Calculate prediction variance from individual models
        individual_preds = []
        
        for i, model in enumerate(self.models):
            if i == 0 and X_high_freq is not None:
                individual_preds.append(model.predict(X_high_freq))
            elif i == 1 and X_mid_freq is not None:
                individual_preds.append(model.predict(X_mid_freq))
            elif i == 2 and X_low_freq is not None:
                individual_preds.append(model.predict(X_low_freq))
        
        if individual_preds:
            # Stack predictions
            stacked = np.hstack(individual_preds)
            
            # Calculate standard deviation across models
            std = np.std(stacked, axis=1, keepdims=True)
            
            # Z-score for confidence level
            from scipy import stats
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            
            # Confidence intervals
            lower_bound = predictions - z_score * std
            upper_bound = predictions + z_score * std
        else:
            # No variance info, use fixed percentage
            margin = predictions * 0.05  # 5% margin
            lower_bound = predictions - margin
            upper_bound = predictions + margin
        
        return predictions, lower_bound, upper_bound
    
    def save(self, filepath: str):
        """Save ensemble configuration."""
        import joblib
        
        config = {
            'weights': self.weights,
            'n_models': len(self.models)
        }
        
        joblib.dump(config, filepath)
        logger.info(f"Ensemble config saved to {filepath}")
    
    def load(self, filepath: str):
        """Load ensemble configuration."""
        import joblib
        
        config = joblib.load(filepath)
        self.weights = config['weights']
        
        logger.info(f"Ensemble config loaded from {filepath}")
