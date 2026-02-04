"""
Training service for ML models with walk-forward validation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings, get_logger
from app.models.db import OilPrice, TechnicalIndicator, Prediction, ModelMetadata
from app.services import preprocessing_service, vmd_service
from app.models.ml.bilstm_attention import BiLSTMAttentionModel
from app.models.ml.cnn_lstm import CNNLSTMModel
from app.models.ml.xgboost_model import XGBoostModel
from app.models.ml.ensemble import EnsembleModel


logger = get_logger(__name__)


class TrainingService:
    """Service for training ML models with walk-forward validation."""
    
    def __init__(self):
        self.bilstm_model = None
        self.cnn_lstm_model = None
        self.xgboost_model = None
        self.ensemble_model = None
    
    async def prepare_training_data(
        self,
        db: AsyncSession,
        symbol: str = "WTI",
        lookback_days: int = 730
    ) -> Dict[str, np.ndarray]:
        """
        Prepare training data from database.
        
        Args:
            db: Database session
            symbol: Oil symbol
            lookback_days: Number of days to look back
        
        Returns:
            Dictionary with prepared data
        """
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        # Fetch price data
        stmt = select(OilPrice).where(
            OilPrice.symbol == symbol,
            OilPrice.timestamp >= start_date
        ).order_by(OilPrice.timestamp)
        
        result = await db.execute(stmt)
        prices = result.scalars().all()
        
        if not prices:
            raise ValueError(f"No price data found for {symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': p.timestamp,
            'close': float(p.close),
            'high': float(p.high),
            'low': float(p.low),
            'open': float(p.open),
            'volume': p.volume
        } for p in prices])
        
        df.set_index('timestamp', inplace=True)
        
        # Normalize
        normalized_df, scaler = preprocessing_service.normalize_prices(
            df, feature_columns=['close']
        )
        
        # VMD decomposition
        close_prices = normalized_df['close'].values
        modes, _, _ = vmd_service.decompose(close_prices, n_modes=6)
        
        # Cluster IMFs
        clustering_result = vmd_service.cluster_modes(modes, n_clusters=3)
        grouped_modes = clustering_result['grouped_modes']
        
        logger.info(
            f"Prepared data: {len(df)} records, "
            f"{len(grouped_modes['low_freq'])} low-freq IMFs, "
            f"{len(grouped_modes['mid_freq'])} mid-freq IMFs, "
            f"{len(grouped_modes['high_freq'])} high-freq IMFs"
        )
        
        return {
            'original': close_prices,
            'normalized_df': normalized_df,
            'scaler': scaler,
            'high_freq_imfs': grouped_modes['high_freq'],
            'mid_freq_imfs': grouped_modes['mid_freq'],
            'low_freq_imfs': grouped_modes['low_freq']
        }
    
    def train_all_models(
        self,
        data: Dict[str, np.ndarray],
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict[str, any]:
        """
        Train all models (BiLSTM, CNN-LSTM, XGBoost).
        
        Args:
            data: Prepared training data
            epochs: Number of training epochs
            batch_size: Batch size
        
        Returns:
            Training histories
        """
        histories = {}
        
        # Prepare sequences
        sequence_length = settings.sequence_length
        
        # Train BiLSTM for high-frequency IMFs
        if len(data['high_freq_imfs']) > 0:
            logger.info("Training BiLSTM-Attention for high-frequency IMFs")
            
            # Combine high-freq IMFs
            high_freq_signal = np.sum(data['high_freq_imfs'], axis=0)
            
            X_high, y_high = preprocessing_service.create_sequences(
                high_freq_signal,
                sequence_length=sequence_length,
                forecast_horizon=1
            )
            
            X_high = X_high.reshape(X_high.shape[0], X_high.shape[1], 1)
            
            # Split data
            X_train_high, X_val_high, X_test_high = preprocessing_service.split_train_val_test(X_high)
            y_train_high, y_val_high, y_test_high = preprocessing_service.split_train_val_test(y_high)
            
            # Train
            self.bilstm_model = BiLSTMAttentionModel(
                sequence_length=sequence_length,
                n_features=1
            )
            histories['bilstm'] = self.bilstm_model.train(
                X_train_high, y_train_high,
                X_val_high, y_val_high,
                epochs=epochs,
                batch_size=batch_size
            )
        
        # Train CNN-LSTM for mid-frequency IMFs
        if len(data['mid_freq_imfs']) > 0:
            logger.info("Training CNN-LSTM for mid-frequency IMFs")
            
            mid_freq_signal = np.sum(data['mid_freq_imfs'], axis=0)
            
            X_mid, y_mid = preprocessing_service.create_sequences(
                mid_freq_signal,
                sequence_length=sequence_length,
                forecast_horizon=1
            )
            
            X_mid = X_mid.reshape(X_mid.shape[0], X_mid.shape[1], 1)
            
            X_train_mid, X_val_mid, X_test_mid = preprocessing_service.split_train_val_test(X_mid)
            y_train_mid, y_val_mid, y_test_mid = preprocessing_service.split_train_val_test(y_mid)
            
            self.cnn_lstm_model = CNNLSTMModel(
                sequence_length=sequence_length,
                n_features=1
            )
            histories['cnn_lstm'] = self.cnn_lstm_model.train(
                X_train_mid, y_train_mid,
                X_val_mid, y_val_mid,
                epochs=epochs,
                batch_size=batch_size
            )
        
        # Train XGBoost for low-frequency IMFs
        if len(data['low_freq_imfs']) > 0:
            logger.info("Training XGBoost for low-frequency IMFs")
            
            low_freq_signal = np.sum(data['low_freq_imfs'], axis=0)
            
            X_low, y_low = preprocessing_service.create_sequences(
                low_freq_signal,
                sequence_length=sequence_length,
                forecast_horizon=1
            )
            
            X_train_low, X_val_low, X_test_low = preprocessing_service.split_train_val_test(X_low)
            y_train_low, y_val_low, y_test_low = preprocessing_service.split_train_val_test(y_low)
            
            self.xgboost_model = XGBoostModel()
            histories['xgboost'] = self.xgboost_model.train(
                X_train_low, y_train_low,
                X_val_low, y_val_low
            )
        
        # Build ensemble
        logger.info("Building ensemble model")
        self.ensemble_model = EnsembleModel(
            models=[self.bilstm_model, self.cnn_lstm_model, self.xgboost_model]
        )
        
        # Optimize ensemble weights on validation set
        val_predictions = []
        if self.bilstm_model:
            val_predictions.append(self.bilstm_model.predict(X_val_high))
        if self.cnn_lstm_model:
            val_predictions.append(self.cnn_lstm_model.predict(X_val_mid))
        if self.xgboost_model:
            val_predictions.append(self.xgboost_model.predict(X_val_low))
        
        if val_predictions:
            # Use first available validation target
            y_val_ensemble = y_val_high if self.bilstm_model else (y_val_mid if self.cnn_lstm_model else y_val_low)
            self.ensemble_model.optimize_weights(val_predictions, y_val_ensemble)
        
        logger.info("Training completed for all models")
        return histories
    
    async def save_model_metadata(
        self,
        db: AsyncSession,
        version: str,
        metrics: Dict[str, float]
    ):
        """Save model metadata to database."""
        metadata = ModelMetadata(
            version=version,
            trained_at=datetime.now(),
            architecture={
                'bilstm_attention': 'BiLSTM-256 + MultiHeadAttention-8',
                'cnn_lstm': 'Conv1D-64 + LSTM-128',
                'xgboost': 'XGBoost-500',
                'ensemble': 'Bayesian weighted stacking'
            },
            hyperparameters={
                'sequence_length': settings.sequence_length,
                'batch_size': settings.batch_size,
                'learning_rate': settings.learning_rate,
                'epochs': settings.epochs
            },
            training_metrics=metrics,
            is_active=True
        )
        
        # Deactivate previous models
        await db.execute(
            text("UPDATE model_metadata SET is_active = false WHERE is_active = true")
        )
        
        db.add(metadata)
        await db.commit()
        
        logger.info(f"Model metadata saved: {version}")


# Global instance
training_service = TrainingService()
