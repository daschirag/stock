"""
Historical data endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core import get_db, get_logger
from app.models.db import OilPrice, TechnicalIndicator
from app.schemas import OilPriceData, TechnicalIndicatorData
from app.services import data_service, technical_indicator_service


router = APIRouter(tags=["data"])
logger = get_logger(__name__)


@router.get("/data/latest")
async def get_latest_price(
    symbol: str = Query(default="WTI", description="Oil symbol (WTI or BRENT)"),
    db: AsyncSession = Depends(get_db)
):
    """Get the latest oil price."""
    stmt = select(OilPrice).where(
        OilPrice.symbol == symbol
    ).order_by(desc(OilPrice.timestamp)).limit(1)
    
    result = await db.execute(stmt)
    price = result.scalar_one_or_none()
    
    if not price:
        return {"error": "No data available", "symbol": symbol}
    
    return {
        "timestamp": price.timestamp,
        "symbol": price.symbol,
        "open": float(price.open),
        "high": float(price.high),
        "low": float(price.low),
        "close": float(price.close),
        "volume": price.volume
    }


@router.get("/data/historical", response_model=List[OilPriceData])
async def get_historical_prices(
    symbol: str = Query(default="WTI", description="Oil symbol"),
    days: int = Query(default=30, le=365, description="Number of days to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical oil prices."""
    start_date = datetime.now() - timedelta(days=days)
    
    stmt = select(OilPrice).where(
        and_(
            OilPrice.symbol == symbol,
            OilPrice.timestamp >= start_date
        )
    ).order_by(OilPrice.timestamp)
    
    result = await db.execute(stmt)
    prices = result.scalars().all()
    
    return [
        OilPriceData(
            timestamp=p.timestamp,
            symbol=p.symbol,
            open=float(p.open),
            high=float(p.high),
            low=float(p.low),
            close=float(p.close),
            volume=p.volume
        )
        for p in prices
    ]


@router.post("/data/fetch")
async def trigger_data_fetch(
    background_tasks: BackgroundTasks,
    symbol: str = Query(default="WTI", description="Oil symbol"),
    days: int = Query(default=365, le=730, description="Number of days to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger background data fetching.
    
    This endpoint starts a background task to fetch oil price data.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    async def fetch_and_save():
        """Background task to fetch and save data."""
        try:
            # Fetch prices
            prices = await data_service.fetch_oil_prices(
                symbol=symbol,
                start_date=start_date
            )
            
            # Save to database
            saved_count = await data_service.save_oil_prices(db, prices)
            
            # Calculate technical indicators
            if saved_count > 0:
                indicator_count = await technical_indicator_service.calculate_all_indicators(
                    db, symbol, lookback_days=days
                )
                logger.info(f"Calculated {indicator_count} technical indicators")
            
            logger.info(f"Data fetch completed: {saved_count} prices saved")
            
        except Exception as e:
            logger.error(f"Error in background data fetch: {e}")
    
    background_tasks.add_task(fetch_and_save)
    
    return {
        "status": "started",
        "message": f"Background data fetch initiated for {symbol}",
        "days": days
    }


@router.get("/indicators", response_model=List[TechnicalIndicatorData])
async def get_technical_indicators(
    symbol: str = Query(default="WTI", description="Oil symbol"),
    indicator_names: Optional[str] = Query(
        default=None,
        description="Comma-separated indicator names (e.g., 'RSI,MACD_LINE')"
    ),
    days: int = Query(default=30, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db)
):
    """Get technical indicators."""
    start_date = datetime.now() - timedelta(days=days)
    
    # Build query
    conditions = [
        TechnicalIndicator.symbol == symbol,
        TechnicalIndicator.timestamp >= start_date
    ]
    
    if indicator_names:
        names_list = [name.strip() for name in indicator_names.split(",")]
        conditions.append(TechnicalIndicator.indicator_name.in_(names_list))
    
    stmt = select(TechnicalIndicator).where(
        and_(*conditions)
    ).order_by(TechnicalIndicator.timestamp)
    
    result = await db.execute(stmt)
    indicators = result.scalars().all()
    
    return [
        TechnicalIndicatorData(
            timestamp=ind.timestamp,
            symbol=ind.symbol,
            indicator_name=ind.indicator_name,
            value=float(ind.value)
        )
        for ind in indicators
    ]


@router.post("/indicators/calculate")
async def trigger_indicator_calculation(
    background_tasks: BackgroundTasks,
    symbol: str = Query(default="WTI", description="Oil symbol"),
    days: int = Query(default=365, le=730, description="Lookback days"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger background technical indicator calculation.
    """
    async def calculate_and_save():
        """Background task to calculate indicators."""
        try:
            count = await technical_indicator_service.calculate_all_indicators(
                db, symbol, lookback_days=days
            )
            logger.info(f"Calculated {count} technical indicators")
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
    
    background_tasks.add_task(calculate_and_save)
    
    return {
        "status": "started",
        "message": f"Indicator calculation initiated for {symbol}",
        "days": days
    }
