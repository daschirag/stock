"""
XGBoost model for low-frequency IMF prediction.
"""
import numpy as np
from typing import Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

from app.core import settings, get_logger


logger = get_logger(__name__)


class XGBoostModel:
    """
    XGBoost regressor for low-frequency IMFs and trend components.
    
    Hyperparameters:
    - n_estimators: 500
    - learning_rate: 0.01
    - max_depth: 5
    - subsample: 0.8
    - colsample_bytree: 0.8
    """
    
    def __init__(
        self,
        n_estimators: int = 500,
        learning_rate: float = 0.01,
        max_depth: int = 5,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42
    ):
        """
        Initialize XGBoost model.
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate
            max_depth: Maximum tree depth
            subsample: Subsample ratio
            colsample_bytree: Column subsample ratio
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state
        
        self.model = None
        self._check_xgboost()
        
        logger.info("Initializing XGBoost model")
    
    def _check_xgboost(self):
        """Check if XGBoost is available."""
        try:
            import xgboost as xgb
            self.xgb_available = True
        except ImportError:
            logger.warning("XGBoost not available, using sklearn GradientBoosting fallback")
            self.xgb_available = False
    
    def build_model(self):
        """Build the XGBoost model."""
        if self.xgb_available:
            import xgboost as xgb
            
            self.model = xgb.XGBRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                subsample=self.subsample,
                colsample_bytree=self.colsample_bytree,
                objective='reg:squarederror',
                random_state=self.random_state,
                n_jobs=-1
            )
            
            logger.info("XGBoost model built successfully")
        else:
            # Fallback to sklearn GradientBoostingRegressor
            from sklearn.ensemble import GradientBoostingRegressor
            
            self.model = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                max_depth=self.max_depth,
                subsample=self.subsample,
                random_state=self.random_state
            )
            
            logger.info("GradientBoosting (sklearn) model built as fallback")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        early_stopping_rounds: int = 50
    ) -> dict:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            early_stopping_rounds: Early stopping rounds
        
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Reshape if needed (flatten sequence dimension)
        if len(X_train.shape) == 3:
            X_train = X_train.reshape(X_train.shape[0], -1)
        if len(y_train.shape) > 1:
            y_train = y_train.ravel()
        
        if X_val is not None:
            if len(X_val.shape) == 3:
                X_val = X_val.reshape(X_val.shape[0], -1)
            if len(y_val.shape) > 1:
                y_val = y_val.ravel()
        
        if self.xgb_available and X_val is not None:
            # XGBoost with early stopping
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=early_stopping_rounds,
                verbose=False
            )
            
            logger.info(f"Training completed. Best iteration: {self.model.best_iteration}")
        else:
            # Train without early stopping
            self.model.fit(X_train, y_train)
            logger.info("Training completed")
        
        # Calculate metrics
        train_score = self.model.score(X_train, y_train)
        val_score = self.model.score(X_val, y_val) if X_val is not None else None
        
        history = {
            'train_r2': train_score,
            'val_r2': val_score
        }
        
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
        
        Returns:
            Predictions
        """
        # Reshape if needed
        if len(X.shape) == 3:
            X = X.reshape(X.shape[0], -1)
        
        predictions = self.model.predict(X)
        return predictions.reshape(-1, 1)
    
    def get_feature_importance(self) -> Dict[int, float]:
        """
        Get feature importance.
        
        Returns:
            Dictionary of feature indices and importance scores
        """
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return {i: float(imp) for i, imp in enumerate(importances)}
        return {}
    
    def save(self, filepath: str):
        """Save model to disk."""
        import joblib
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk."""
        import joblib
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
