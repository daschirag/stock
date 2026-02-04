"""
Pydantic schemas for request and response models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    horizon: str = Field(..., description="Prediction horizon: '1d', '7d', or '30d'")
    symbol: str = Field(default="WTI", description="Oil symbol: 'WTI' or 'BRENT'")


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    prediction_for: datetime
    horizon: str
    predicted_price: float
    confidence_lower: float
    confidence_upper: float
    model_version: str
    created_at: datetime


class OilPriceData(BaseModel):
    """Oil price OHLC data."""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicatorData(BaseModel):
    """Technical indicator data."""
    timestamp: datetime
    symbol: str
    indicator_name: str
    value: float


class ModelMetricsResponse(BaseModel):
    """Model performance metrics."""
    model_version: str
    rmse: Optional[float] = None
    mae: Optional[float] = None
    mape: Optional[float] = None
    directional_accuracy: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    last_updated: datetime


class SentimentResponse(BaseModel):
    """Sentiment analysis response."""
    timestamp: datetime
    aggregated_score: float
    source_count: int
    top_headlines: List[str]


class KeyLevelsResponse(BaseModel):
    """Support and resistance levels."""
    support_1: float
    support_2: float
    resistance_1: float
    resistance_2: float
    pivot: float


class AIInsightsResponse(BaseModel):
    """AI-generated market insights."""
    summary: str
    key_drivers: List[str]
    key_levels: KeyLevelsResponse
    technical_summary: str
    outlook: str  # bullish / bearish / neutral
    confidence_score: float  # 0-1


class CalendarEvent(BaseModel):
    """Economic calendar event."""
    date: str
    title: str
    impact: str  # high / medium / low
    description: Optional[str] = None


class EconomicCalendarResponse(BaseModel):
    """Upcoming economic events."""
    events: List[CalendarEvent]
