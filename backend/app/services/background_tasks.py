"""
Background tasks for scheduled data fetching and model retraining.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from app.core import settings, get_logger, get_db
from app.services import (
    data_service,
    technical_indicator_service,
    sentiment_service,
    training_service,
    prediction_service
)


logger = get_logger(__name__)


class BackgroundTasks:
    """Manage background tasks for data pipeline."""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start(self):
        """Start all background tasks."""
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        self.running = True
        logger.info("Starting background tasks")
        
        # Schedule tasks
        self.tasks = [
            asyncio.create_task(self.fetch_prices_task()),
            asyncio.create_task(self.calculate_indicators_task()),
            asyncio.create_task(self.fetch_sentiment_task()),
            asyncio.create_task(self.generate_predictions_task()),
        ]
    
    async def stop(self):
        """Stop all background tasks."""
        self.running = False
        logger.info("Stopping background tasks")
        
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
    
    async def fetch_prices_task(self):
        """Periodically fetch oil prices."""
        while self.running:
            try:
                logger.info("Running scheduled price fetch")
                
                async for db in get_db():
                    # Fetch WTI prices
                    prices = await data_service.fetch_oil_prices(
                        symbol="WTI",
                        start_date=datetime.now() - timedelta(days=7)
                    )
                    
                    if prices:
                        saved = await data_service.save_oil_prices(db, prices)
                        logger.info(f"Saved {saved} WTI price records")
                    
                    # Fetch Brent prices
                    prices = await data_service.fetch_oil_prices(
                        symbol="BRENT",
                        start_date=datetime.now() - timedelta(days=7)
                    )
                    
                    if prices:
                        saved = await data_service.save_oil_prices(db, prices)
                        logger.info(f"Saved {saved} Brent price records")
                    
                    break  # Exit async generator
                
            except Exception as e:
                logger.error(f"Error in price fetch task: {e}")
            
            # Run every hour
            await asyncio.sleep(3600)
    
    async def calculate_indicators_task(self):
        """Periodically calculate technical indicators."""
        # Wait 5 minutes before first run
        await asyncio.sleep(300)
        
        while self.running:
            try:
                logger.info("Running scheduled indicator calculation")
                
                async for db in get_db():
                    # Calculate for WTI
                    count = await technical_indicator_service.calculate_all_indicators(
                        db, symbol="WTI", lookback_days=90
                    )
                    logger.info(f"Calculated {count} WTI indicators")
                    
                    # Calculate for Brent
                    count = await technical_indicator_service.calculate_all_indicators(
                        db, symbol="BRENT", lookback_days=90
                    )
                    logger.info(f"Calculated {count} Brent indicators")
                    
                    break
                
            except Exception as e:
                logger.error(f"Error in indicator calculation task: {e}")
            
            # Run every 6 hours
            await asyncio.sleep(21600)
    
    async def fetch_sentiment_task(self):
        """Periodically fetch sentiment data."""
        # Wait 10 minutes before first run
        await asyncio.sleep(600)
        
        while self.running:
            try:
                logger.info("Running scheduled sentiment fetch")
                
                async for db in get_db():
                    sentiment_records = await sentiment_service.fetch_news_sentiment(
                        query="crude oil",
                        days_back=1
                    )
                    
                    if sentiment_records:
                        saved = await sentiment_service.save_sentiment_data(
                            db, sentiment_records
                        )
                        logger.info(f"Saved {saved} sentiment records")
                    
                    break
                
            except Exception as e:
                logger.error(f"Error in sentiment fetch task: {e}")
            
            # Run every 4 hours
            await asyncio.sleep(14400)
    
    async def generate_predictions_task(self):
        """Periodically generate new predictions."""
        # Wait 15 minutes before first run
        await asyncio.sleep(900)
        
        while self.running:
            try:
                logger.info("Running scheduled prediction generation")
                
                async for db in get_db():
                    # Generate 1-day prediction for WTI
                    prediction = await prediction_service.generate_prediction(
                        db, symbol="WTI", horizon="1d"
                    )
                    await prediction_service.save_prediction(db, prediction)
                    logger.info(f"Generated WTI 1d prediction: ${prediction['predicted_price']}")
                    
                    # Generate 7-day prediction
                    prediction = await prediction_service.generate_prediction(
                        db, symbol="WTI", horizon="7d"
                    )
                    await prediction_service.save_prediction(db, prediction)
                    logger.info(f"Generated WTI 7d prediction: ${prediction['predicted_price']}")
                    
                    break
                
            except Exception as e:
                logger.error(f"Error in prediction generation task: {e}")
            
            # Run every 12 hours
            await asyncio.sleep(43200)


# Global instance
background_tasks = BackgroundTasks()
