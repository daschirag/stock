"""
Sentiment analysis service for news and social media.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings, get_logger
from app.models.db import SentimentData


logger = get_logger(__name__)


class SentimentService:
    """Service for collecting and analyzing sentiment data."""
    
    def __init__(self):
        self.use_mock = not settings.has_api_keys
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Source credibility weights
        self.credibility_weights = {
            "Bloomberg": 1.0,
            "Reuters": 0.95,
            "CNBC": 0.85,
            "MarketWatch": 0.80,
            "Twitter": 0.40,
            "Reddit": 0.35,
            "Unknown": 0.50
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def fetch_news_sentiment(
        self,
        query: str = "crude oil",
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles and analyze sentiment.
        
        Args:
            query: Search query
            days_back: Number of days to look back
        
        Returns:
            List of sentiment records
        """
        if self.use_mock or not settings.news_api_key:
            logger.info("Using mock sentiment data")
            return await self._generate_mock_sentiment(query, days_back)
        
        try:
            return await self._fetch_news_api(query, days_back)
        except Exception as e:
            logger.warning(f"Failed to fetch news sentiment, using mock: {e}")
            return await self._generate_mock_sentiment(query, days_back)
    
    async def _fetch_news_api(
        self,
        query: str,
        days_back: int
    ) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI."""
        url = "https://newsapi.org/v2/everything"
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "apiKey": settings.news_api_key,
            "language": "en",
            "pageSize": 100
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Analyze sentiment for each article
        sentiment_records = []
        for article in articles:
            headline = article.get("title", "")
            source_name = article.get("source", {}).get("name", "Unknown")
            url = article.get("url", "")
            published_at = article.get("publishedAt", "")
            
            if headline and url:
                # Simple sentiment analysis on headline
                sentiment_score = self._analyze_text_sentiment(headline)
                credibility = self.credibility_weights.get(source_name, 0.5)
                
                sentiment_records.append({
                    "timestamp": datetime.fromisoformat(published_at.replace("Z", "+00:00")),
                    "source": source_name,
                    "article_url": url,
                    "headline": headline,
                    "sentiment_score": sentiment_score,
                    "credibility_weight": credibility
                })
        
        logger.info(f"Fetched {len(sentiment_records)} news articles from NewsAPI")
        return sentiment_records
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis using keyword matching.
        
        For production, use DistilBERT or similar model.
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment score (-1 to 1)
        """
        positive_keywords = [
            "surge", "rally", "gain", "rise", "increase", "bullish", "strong",
            "growth", "high", "boost", "jump", "soar", "recovery", "positive"
        ]
        
        negative_keywords = [
            "fall", "drop", "decline", "decrease", "bearish", "weak", "crash",
            "plunge", "loss", "low", "sink", "tumble", "slump", "negative"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_count
        return max(-1.0, min(1.0, sentiment))
    
    async def _generate_mock_sentiment(
        self,
        query: str,
        days_back: int
    ) -> List[Dict[str, Any]]:
        """Generate mock sentiment data."""
        sentiment_records = []
        
        sources = ["Bloomberg", "Reuters", "CNBC", "MarketWatch", "Twitter"]
        headlines_templates = [
            "Oil prices {direction} amid {factor}",
            "{direction_adj} outlook for crude oil as {factor}",
            "Crude oil {direction} on {factor}",
            "Energy markets {direction} following {factor}",
            "{direction_adj} sentiment in oil markets due to {factor}"
        ]
        
        directions = {
            "rise": ["rise", "rising", "bullish", "positive", "strong"],
            "fall": ["fall", "falling", "bearish", "negative", "weak"]
        }
        
        factors = [
            "OPEC production cuts",
            "geopolitical tensions",
            "demand forecasts",
            "inventory data",
            "economic indicators",
            "supply concerns",
            "refinery maintenance",
            "weather forecasts"
        ]
        
        # Generate 3-5 articles per day
        current_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()
        
        while current_date <= end_date:
            num_articles = random.randint(3, 5)
            
            for _ in range(num_articles):
                # Random sentiment direction
                is_positive = random.random() > 0.5
                direction_type = "rise" if is_positive else "fall"
                
                direction = random.choice(directions[direction_type])
                direction_adj = direction.capitalize()
                factor = random.choice(factors)
                template = random.choice(headlines_templates)
                
                headline = template.format(
                    direction=direction,
                    direction_adj=direction_adj,
                    factor=factor
                )
                
                source = random.choice(sources)
                sentiment_score = random.uniform(0.3, 0.9) if is_positive else random.uniform(-0.9, -0.3)
                
                # Add some noise
                sentiment_score += random.uniform(-0.1, 0.1)
                sentiment_score = max(-1.0, min(1.0, sentiment_score))
                
                sentiment_records.append({
                    "timestamp": current_date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    "source": source,
                    "article_url": f"https://mock-news.com/article-{random.randint(1000, 9999)}",
                    "headline": headline,
                    "sentiment_score": round(sentiment_score, 4),
                    "credibility_weight": self.credibility_weights[source]
                })
            
            current_date += timedelta(days=1)
        
        logger.info(f"Generated {len(sentiment_records)} mock sentiment records")
        return sentiment_records
    
    async def save_sentiment_data(
        self,
        db: AsyncSession,
        sentiment_records: List[Dict[str, Any]]
    ) -> int:
        """
        Save sentiment data to database.
        
        Args:
            db: Database session
            sentiment_records: List of sentiment records
        
        Returns:
            Number of records saved
        """
        saved_count = 0
        
        for record in sentiment_records:
            sentiment_data = SentimentData(
                timestamp=record["timestamp"],
                source=record["source"],
                article_url=record["article_url"],
                headline=record["headline"],
                sentiment_score=Decimal(str(record["sentiment_score"])),
                credibility_weight=Decimal(str(record["credibility_weight"]))
            )
            
            # Merge to avoid duplicates
            db.add(sentiment_data)
            saved_count += 1
        
        try:
            await db.commit()
            logger.info(f"Saved {saved_count} sentiment records")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving sentiment data: {e}")
            saved_count = 0
        
        return saved_count
    
    async def get_aggregated_sentiment(
        self,
        db: AsyncSession,
        days_back: int = 7
    ) -> Dict[str, float]:
        """
        Get aggregated sentiment score.
        
        Args:
            db: Database session
            days_back: Number of days to aggregate
        
        Returns:
            Dictionary with aggregated metrics
        """
        from sqlalchemy import func, and_
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = await db.execute(
            f"""
            SELECT 
                AVG(sentiment_score * credibility_weight) as weighted_avg,
                COUNT(*) as count,
                AVG(sentiment_score) as simple_avg
            FROM sentiment_data
            WHERE timestamp >= '{start_date.isoformat()}'
            """
        )
        
        result = query.fetchone()
        
        if result and result[0] is not None:
            aggregated = {
                "weighted_average": float(result[0]),
                "simple_average": float(result[2]),
                "article_count": int(result[1])
            }
        else:
            aggregated = {
                "weighted_average": 0.0,
                "simple_average": 0.0,
                "article_count": 0
            }
        
        logger.info(f"Aggregated sentiment: {aggregated}")
        return aggregated


# Global instance
sentiment_service = SentimentService()
