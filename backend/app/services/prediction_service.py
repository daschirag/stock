"""
Prediction service for generating oil price forecasts.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core import settings, get_logger
from app.models.db import OilPrice, Prediction
from app.services import preprocessing_service, training_service, sentiment_service


logger = get_logger(__name__)


class PredictionService:
    """Service for generating price predictions."""
    
    async def generate_prediction(
        self,
        db: AsyncSession,
        symbol: str = "WTI",
        horizon: str = "1d"
    ) -> Dict:
        """
        Generate price prediction.
        
        Args:
            db: Database session
            symbol: Oil symbol
            horizon: Forecast horizon ('1d', '7d', '30d')
        
        Returns:
            Prediction dictionary
        """
        # Map horizon to days
        horizon_days = {'1d': 1, '7d': 7, '30d': 30}
        days = horizon_days.get(horizon, 1)
        
        # Get recent price data
        stmt = select(OilPrice).where(
            OilPrice.symbol == symbol
        ).order_by(desc(OilPrice.timestamp)).limit(settings.sequence_length)
        
        result = await db.execute(stmt)
        recent_prices = result.scalars().all()
        
        if len(recent_prices) < settings.sequence_length:
            raise ValueError(f"Insufficient data: need {settings.sequence_length} records")
        
        # Reverse to chronological order
        recent_prices = recent_prices[::-1]
        
        # Extract close prices
        close_prices = np.array([float(p.close) for p in recent_prices])
        
        # Normalize
        import pandas as pd
        df = pd.DataFrame({'close': close_prices})
        normalized, scaler = preprocessing_service.normalize_prices(df, ['close'])
        
        normalized_prices = normalized['close'].values
        
        # Reshape for model input
        X = normalized_prices.reshape(1, settings.sequence_length, 1)
        
        # Generate prediction using ensemble
        if training_service.ensemble_model is None:
            # Use simple moving average as fallback
            logger.warning("No trained model available, using moving average")
            predicted_normalized = np.mean(normalized_prices[-7:])
        else:
            # Get ensemble prediction with confidence intervals
            pred, lower, upper = training_service.ensemble_model.predict_with_confidence(
                X_high_freq=X if training_service.bilstm_model else None,
                X_mid_freq=X if training_service.cnn_lstm_model else None,
                X_low_freq=X if training_service.xgboost_model else None
            )
            
            predicted_normalized = pred[0][0]
            lower_normalized = lower[0][0]
            upper_normalized = upper[0][0]
        
        # Denormalize
        predicted_price = scaler.inverse_transform([[predicted_normalized]])[0][0]
        
        if training_service.ensemble_model:
            confidence_lower = scaler.inverse_transform([[lower_normalized]])[0][0]
            confidence_upper = scaler.inverse_transform([[upper_normalized]])[0][0]
        else:
            # Fallback: 5% margin
            confidence_lower = predicted_price * 0.95
            confidence_upper = predicted_price * 1.05
        
        # Calculate prediction timestamp
        last_timestamp = recent_prices[-1].timestamp
        prediction_for = last_timestamp + timedelta(days=days)
        
        # Get sentiment adjustment
        sentiment_data = await sentiment_service.get_aggregated_sentiment(db, days_back=7)
        sentiment_score = sentiment_data.get('weighted_average', 0.0)
        
        # Apply sentiment adjustment (±2% based on sentiment)
        sentiment_adjustment = 1 + (sentiment_score * 0.02)
        predicted_price *= sentiment_adjustment
        confidence_lower *= sentiment_adjustment
        confidence_upper *= sentiment_adjustment
        
        prediction_dict = {
            'prediction_for': prediction_for,
            'horizon': horizon,
            'predicted_price': round(predicted_price, 2),
            'confidence_lower': round(confidence_lower, 2),
            'confidence_upper': round(confidence_upper, 2),
            'model_version': settings.model_version,
            'sentiment_score': sentiment_score,
            'created_at': datetime.now()
        }
        
        logger.info(
            f"Generated prediction for {symbol} {horizon}: "
            f"${predicted_price:.2f} [{confidence_lower:.2f}, {confidence_upper:.2f}]"
        )
        
        return prediction_dict
    
    async def save_prediction(
        self,
        db: AsyncSession,
        prediction_dict: Dict
    ) -> int:
        """
        Save prediction to database.
        
        Args:
            db: Database session
            prediction_dict: Prediction data
        
        Returns:
            Prediction ID
        """
        prediction = Prediction(
            created_at=prediction_dict['created_at'],
            model_version=prediction_dict['model_version'],
            prediction_for=prediction_dict['prediction_for'],
            horizon=prediction_dict['horizon'],
            predicted_price=Decimal(str(prediction_dict['predicted_price'])),
            confidence_lower=Decimal(str(prediction_dict['confidence_lower'])),
            confidence_upper=Decimal(str(prediction_dict['confidence_upper']))
        )
        
        db.add(prediction)
        await db.commit()
        await db.refresh(prediction)
        
        logger.info(f"Saved prediction with ID: {prediction.id}")
        return prediction.id


# Global instance
prediction_service = PredictionService()
