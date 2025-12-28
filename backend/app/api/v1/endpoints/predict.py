"""
Prediction endpoints for generating price forecasts.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.core import get_db, get_logger
from app.schemas import PredictionRequest, PredictionResponse
from app.services import prediction_service
from app.models.db import Prediction


router = APIRouter(tags=["predictions"])
logger = get_logger(__name__)


@router.post("/predict", response_model=PredictionResponse)
async def generate_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate oil price prediction.
    
    Request body:
    - horizon: '1d', '7d', or '30d'
    - symbol: 'WTI' or 'BRENT'
    """
    try:
        # Generate prediction
        prediction_dict = await prediction_service.generate_prediction(
            db=db,
            symbol=request.symbol,
            horizon=request.horizon
        )
        
        # Save to database
        await prediction_service.save_prediction(db, prediction_dict)
        
        return PredictionResponse(**prediction_dict)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/history", response_model=List[PredictionResponse])
async def get_prediction_history(
    horizon: str = Query(default=None, description="Filter by horizon"),
    limit: int = Query(default=100, le=1000, description="Number of predictions to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical predictions."""
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
