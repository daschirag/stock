"""
Preprocessing service for data normalization and feature engineering.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

from app.core import get_logger


logger = get_logger(__name__)


class PreprocessingService:
    """Service for data preprocessing and normalization."""
    
    def __init__(self):
        self.scalers: Dict[str, MinMaxScaler] = {}
    
    def normalize_prices(
        self,
        prices: pd.DataFrame,
        feature_columns: List[str] = None
    ) -> Tuple[pd.DataFrame, MinMaxScaler]:
        """
        Normalize price data using MinMax scaling.
        
        Args:
            prices: DataFrame with price data
            feature_columns: Columns to normalize (default: ['open', 'high', 'low', 'close'])
        
        Returns:
            Tuple of (normalized DataFrame, scaler)
        """
        if feature_columns is None:
            feature_columns = ['open', 'high', 'low', 'close']
        
        # Create a copy to avoid modifying original
        normalized_df = prices.copy()
        
        # Initialize scaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        
        # Fit and transform
        normalized_df[feature_columns] = scaler.fit_transform(prices[feature_columns])
        
        logger.info(f"Normalized {len(feature_columns)} price features")
        return normalized_df, scaler
    
    def denormalize_prices(
        self,
        normalized_prices: np.ndarray,
        scaler: MinMaxScaler
    ) -> np.ndarray:
        """
        Reverse normalization to get original price scale.
        
        Args:
            normalized_prices: Normalized price array
            scaler: Fitted scaler
        
        Returns:
            Original scale prices
        """
        return scaler.inverse_transform(normalized_prices)
    
    def create_sequences(
        self,
        data: np.ndarray,
        sequence_length: int,
        forecast_horizon: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction.
        
        Args:
            data: Input data array
            sequence_length: Length of input sequence
            forecast_horizon: Number of steps to forecast
        
        Returns:
            Tuple of (X sequences, y targets)
        """
        X, y = [], []
        
        for i in range(len(data) - sequence_length - forecast_horizon + 1):
            X.append(data[i:i + sequence_length])
            y.append(data[i + sequence_length:i + sequence_length + forecast_horizon])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Created {len(X)} sequences with length {sequence_length}")
        return X, y
    
    def add_technical_features(
        self,
        df: pd.DataFrame,
        indicators: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Add technical indicators as features to price data.
        
        Args:
            df: Price DataFrame
            indicators: Technical indicators DataFrame
        
        Returns:
            Combined DataFrame
        """
        # Pivot indicators to columns
        indicators_pivot = indicators.pivot(
            index='timestamp',
            columns='indicator_name',
            values='value'
        )
        
        # Merge with price data
        combined = df.join(indicators_pivot, how='left')
        
        # Forward fill NaN values
        combined = combined.fillna(method='ffill').fillna(method='bfill')
        
        logger.info(f"Added {len(indicators_pivot.columns)} technical features")
        return combined
    
    def split_train_val_test(
        self,
        data: np.ndarray,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            data: Input data
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
        
        Returns:
            Tuple of (train, validation, test) sets
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
            "Ratios must sum to 1.0"
        
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train = data[:train_end]
        val = data[train_end:val_end]
        test = data[val_end:]
        
        logger.info(
            f"Split data: train={len(train)}, val={len(val)}, test={len(test)}"
        )
        return train, val, test
    
    def calculate_returns(
        self,
        prices: pd.Series
    ) -> pd.Series:
        """
        Calculate percentage returns.
        
        Args:
            prices: Price series
        
        Returns:
            Returns series
        """
        returns = prices.pct_change()
        return returns.fillna(0)
    
    def calculate_log_returns(
        self,
        prices: pd.Series
    ) -> pd.Series:
        """
        Calculate log returns.
        
        Args:
            prices: Price series
        
        Returns:
            Log returns series
        """
        log_returns = np.log(prices / prices.shift(1))
        return log_returns.fillna(0)
    
    def detect_outliers(
        self,
        data: pd.Series,
        n_std: float = 3.0
    ) -> pd.Series:
        """
        Detect outliers using standard deviation method.
        
        Args:
            data: Data series
            n_std: Number of standard deviations for threshold
        
        Returns:
            Boolean series indicating outliers
        """
        mean = data.mean()
        std = data.std()
        
        outliers = (data < mean - n_std * std) | (data > mean + n_std * std)
        
        n_outliers = outliers.sum()
        logger.info(f"Detected {n_outliers} outliers ({n_outliers/len(data)*100:.2f}%)")
        return outliers
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        method: str = 'ffill'
    ) -> pd.DataFrame:
        """
        Handle missing values in DataFrame.
        
        Args:
            df: Input DataFrame
            method: Fill method ('ffill', 'bfill', 'interpolate')
        
        Returns:
            DataFrame with missing values handled
        """
        if method == 'ffill':
            filled = df.fillna(method='ffill').fillna(method='bfill')
        elif method == 'bfill':
            filled = df.fillna(method='bfill').fillna(method='ffill')
        elif method == 'interpolate':
            filled = df.interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
        else:
            raise ValueError(f"Unknown method: {method}")
        
        n_missing_before = df.isna().sum().sum()
        n_missing_after = filled.isna().sum().sum()
        
        logger.info(
            f"Handled {n_missing_before} missing values, {n_missing_after} remaining"
        )
        return filled


# Global instance
preprocessing_service = PreprocessingService()
