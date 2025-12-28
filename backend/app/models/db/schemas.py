"""
SQLAlchemy database models for TimescaleDB.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DECIMAL, BigInteger, Integer, Boolean, DateTime, Text, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class OilPrice(Base):
    """Oil price data with OHLC values."""
    __tablename__ = "oil_prices"
    
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String(10), nullable=False, primary_key=True)
    open = Column(DECIMAL(10, 2))
    high = Column(DECIMAL(10, 2))
    low = Column(DECIMAL(10, 2))
    close = Column(DECIMAL(10, 2))
    volume = Column(BigInteger)
    
    __table_args__ = (
        Index('idx_oil_prices_symbol', 'symbol', 'timestamp'),
    )


class TechnicalIndicator(Base):
    """Technical indicators calculated from price data."""
    __tablename__ = "technical_indicators"
    
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String(10), nullable=False, primary_key=True)
    indicator_name = Column(String(50), nullable=False, primary_key=True)
    value = Column(DECIMAL(15, 6))
    
    __table_args__ = (
        Index('idx_technical_indicators_symbol', 'symbol', 'indicator_name', 'timestamp'),
    )


class Prediction(Base):
    """Model predictions with confidence intervals."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    model_version = Column(String(50))
    prediction_for = Column(TIMESTAMP(timezone=True))
    horizon = Column(String(10))  # '1d', '7d', '30d'
    predicted_price = Column(DECIMAL(10, 2))
    confidence_lower = Column(DECIMAL(10, 2))
    confidence_upper = Column(DECIMAL(10, 2))
    actual_price = Column(DECIMAL(10, 2))
    error = Column(DECIMAL(10, 2))
    
    __table_args__ = (
        Index('idx_predictions_for', 'prediction_for'),
        Index('idx_predictions_created', 'created_at'),
        Index('idx_predictions_horizon', 'horizon'),
    )


class ModelMetadata(Base):
    """ML model metadata and metrics."""
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    trained_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    architecture = Column(JSONB)
    hyperparameters = Column(JSONB)
    training_metrics = Column(JSONB)
    is_active = Column(Boolean, default=False)


class SentimentData(Base):
    """Sentiment analysis data from news sources."""
    __tablename__ = "sentiment_data"
    
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    source = Column(String(50), primary_key=True)
    article_url = Column(Text, primary_key=True)
    headline = Column(Text)
    sentiment_score = Column(DECIMAL(5, 4))  # -1 to 1
    credibility_weight = Column(DECIMAL(3, 2))  # 0 to 1
    
    __table_args__ = (
        Index('idx_sentiment_data_timestamp', 'timestamp'),
    )
