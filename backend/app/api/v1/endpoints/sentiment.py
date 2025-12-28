"""
Sentiment data endpoints.
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger
from app.services import sentiment_service
from app.schemas import SentimentResponse


router = APIRouter(tags=["sentiment"])
logger = get_logger(__name__)


@router.get("/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    days: int = Query(default=7, le=30, description="Number of days to aggregate"),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated sentiment analysis."""
    aggregated = await sentiment_service.get_aggregated_sentiment(db, days_back=days)
    
    # Get top headlines
    from sqlalchemy import select, desc
    from app.models.db import SentimentData
    
    stmt = select(SentimentData).where(
        SentimentData.timestamp >= datetime.now() - timedelta(days=days)
    ).order_by(
        desc(SentimentData.sentiment_score * SentimentData.credibility_weight)
    ).limit(5)
    
    result = await db.execute(stmt)
    top_sentiment = result.scalars().all()
    
    return SentimentResponse(
        timestamp=datetime.now(),
        aggregated_score=aggregated["weighted_average"],
        source_count=aggregated["article_count"],
        top_headlines=[s.headline for s in top_sentiment if s.headline]
    )


@router.post("/sentiment/fetch")
async def trigger_sentiment_fetch(
    background_tasks: BackgroundTasks,
    days: int = Query(default=7, le=30, description="Number of days to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """Trigger background sentiment data fetching."""
    
    async def fetch_and_save():
        """Background task to fetch sentiment."""
        try:
            sentiment_records = await sentiment_service.fetch_news_sentiment(
                query="crude oil",
                days_back=days
            )
            
            saved_count = await sentiment_service.save_sentiment_data(
                db, sentiment_records
            )
            
            logger.info(f"Saved {saved_count} sentiment records")
            
        except Exception as e:
            logger.error(f"Error fetching sentiment: {e}")
    
    background_tasks.add_task(fetch_and_save)
    
    return {
        "status": "started",
        "message": "Sentiment fetch initiated",
        "days": days
    }
