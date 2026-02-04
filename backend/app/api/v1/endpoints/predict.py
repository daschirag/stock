"""
Prediction endpoints for generating price forecasts.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.core import get_db, get_logger
from app.core.database import db_available
from app.schemas import PredictionRequest, PredictionResponse
from app.services import prediction_service
from app.models.db import Prediction


router = APIRouter(tags=["predictions"])
logger = get_logger(__name__)


def _mock_prediction_response(horizon: str = "1d", symbol: str = "WTI") -> PredictionResponse:
    """Return mock prediction when DB is unavailable."""
    now = datetime.now()
    horizon_days = {"1d": 1, "7d": 7, "30d": 30}
    days = horizon_days.get(horizon, 1)
    return PredictionResponse(
        prediction_for=now + timedelta(days=days),
        horizon=horizon,
        predicted_price=76.89,
        confidence_lower=74.21,
        confidence_upper=79.57,
        model_version="v1.0.0",
        created_at=now,
    )


@router.post("/predict", response_model=PredictionResponse)
async def generate_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate oil price prediction.
    Returns mock prediction when database is unavailable.
    """
    if not db_available:
        return _mock_prediction_response(request.horizon, request.symbol)
    try:
        prediction_dict = await prediction_service.generate_prediction(
            db=db,
            symbol=request.symbol,
            horizon=request.horizon
        )
        await prediction_service.save_prediction(db, prediction_dict)
        return PredictionResponse(**prediction_dict)
    except OSError as e:
        logger.warning(f"Database unreachable, returning mock prediction: {e}")
        return _mock_prediction_response(request.horizon, request.symbol)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/history", response_model=List[PredictionResponse])
async def get_prediction_history(
    horizon: str = Query(default=None, description="Filter by horizon"),
    limit: int = Query(default=100, le=1000, description="Number of predictions to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical predictions. Returns empty list when database is unavailable."""
    if not db_available:
        return []
    try:
        query = select(Prediction).order_by(desc(Prediction.created_at))
        if horizon:
            query = query.where(Prediction.horizon == horizon)
        query = query.limit(limit)
        result = await db.execute(query)
        predictions = result.scalars().all()
        return [
            PredictionResponse(
                prediction_for=p.prediction_for,
                horizon=p.horizon,
                predicted_price=float(p.predicted_price),
                confidence_lower=float(p.confidence_lower),
                confidence_upper=float(p.confidence_upper),
                model_version=p.model_version,
                created_at=p.created_at
            )
            for p in predictions
        ]
    except OSError as e:
        logger.warning(f"Database unreachable for prediction history: {e}")
        return []
