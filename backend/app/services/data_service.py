"""
Data fetching service for crude oil prices and macroeconomic indicators.
Supports Yahoo Finance, FRED, and EIA APIs with mock data fallback.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import random

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import settings, get_logger
from app.models.db import OilPrice


logger = get_logger(__name__)


class DataService:
    """Service for fetching oil price and macroeconomic data."""
    
    def __init__(self):
        self.use_mock = not settings.has_api_keys
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def fetch_oil_prices(
        self, 
        symbol: str = "WTI",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch oil price data.
        
        Args:
            symbol: Oil type ('WTI' or 'BRENT')
            start_date: Start date for data
            end_date: End date for data
        
        Returns:
            List of price records
        """
        if self.use_mock:
            logger.info(f"Using mock data for {symbol} prices")
            return await self._generate_mock_oil_prices(symbol, start_date, end_date)
        
        try:
            return await self._fetch_yahoo_finance(symbol, start_date, end_date)
        except Exception as e:
            logger.warning(f"Failed to fetch real data, using mock: {e}")
            return await self._generate_mock_oil_prices(symbol, start_date, end_date)
    
    async def _fetch_yahoo_finance(
        self,
        symbol: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Fetch data from Yahoo Finance API."""
        # Map symbols to Yahoo Finance tickers
        ticker_map = {
            "WTI": "CL=F",  # WTI Crude Oil Futures
            "BRENT": "BZ=F"  # Brent Crude Oil Futures
        }
        
        ticker = ticker_map.get(symbol, "CL=F")
        
        # Use yfinance library approach
        try:
            import yfinance as yf
            
            if not start_date:
                start_date = datetime.now() - timedelta(days=365)
            if not end_date:
                end_date = datetime.now()
            
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            records = []
            for index, row in data.iterrows():
                records.append({
                    "timestamp": index.to_pydatetime(),
                    "symbol": symbol,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if "Volume" in row else 0
                })
            
            logger.info(f"Fetched {len(records)} records from Yahoo Finance for {symbol}")
            return records
            
        except ImportError:
            logger.warning("yfinance not installed, using mock data")
            return await self._generate_mock_oil_prices(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance: {e}")
            raise
    
    async def _generate_mock_oil_prices(
        self,
        symbol: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock oil price data."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        records = []
        current_date = start_date
        
        # Starting prices
        base_prices = {"WTI": 75.0, "BRENT": 80.0}
        current_price = base_prices.get(symbol, 75.0)
        
        while current_date <= end_date:
            # Generate realistic OHLC with some volatility
            daily_change = random.uniform(-0.03, 0.03)  # ±3% daily change
            
            open_price = current_price
            close_price = current_price * (1 + daily_change)
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            volume = random.randint(100000, 500000)
            
            records.append({
                "timestamp": current_date,
                "symbol": symbol,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            current_price = close_price
            current_date += timedelta(days=1)
        
        logger.info(f"Generated {len(records)} mock records for {symbol}")
        return records
    
    async def fetch_fred_data(
        self,
        series_id: str,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch macroeconomic data from FRED API.
        
        Args:
            series_id: FRED series ID (e.g., 'DEXUSEU' for USD/EUR)
            start_date: Start date
        
        Returns:
            List of data points
        """
        if self.use_mock or not settings.fred_api_key:
            logger.info(f"Using mock data for FRED series {series_id}")
            return await self._generate_mock_fred_data(series_id, start_date)
        
        try:
            return await self._fetch_fred_api(series_id, start_date)
        except Exception as e:
            logger.warning(f"Failed to fetch FRED data, using mock: {e}")
            return await self._generate_mock_fred_data(series_id, start_date)
    
    async def _fetch_fred_api(
        self,
        series_id: str,
        start_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Fetch from FRED API."""
        url = "https://api.stlouisfed.org/fred/series/observations"
        
        params = {
            "series_id": series_id,
            "api_key": settings.fred_api_key,
            "file_type": "json"
        }
        
        if start_date:
            params["observation_start"] = start_date.strftime("%Y-%m-%d")
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        records = []
        
        for obs in data.get("observations", []):
            try:
                value = float(obs["value"])
                records.append({
                    "date": datetime.strptime(obs["date"], "%Y-%m-%d"),
                    "value": value
                })
            except (ValueError, KeyError):
                continue
        
        logger.info(f"Fetched {len(records)} records from FRED for {series_id}")
        return records
    
    async def _generate_mock_fred_data(
        self,
        series_id: str,
        start_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Generate mock FRED data."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        
        records = []
        current_date = start_date
        end_date = datetime.now()
        
        # Base values for different series
        base_values = {
            "DEXUSEU": 1.1,  # USD/EUR
            "DFF": 5.0,      # Federal Funds Rate
        }
        base_value = base_values.get(series_id, 100.0)
        
        while current_date <= end_date:
            value = base_value * random.uniform(0.95, 1.05)
            records.append({
                "date": current_date,
                "value": round(value, 4)
            })
            current_date += timedelta(days=1)
        
        return records
    
    async def save_oil_prices(
        self,
        db: AsyncSession,
        prices: List[Dict[str, Any]]
    ) -> int:
        """
        Save oil prices to database.
        
        Args:
            db: Database session
            prices: List of price records
        
        Returns:
            Number of records saved
        """
        saved_count = 0
        
        for price_data in prices:
            # Check if record exists
            stmt = select(OilPrice).where(
                OilPrice.timestamp == price_data["timestamp"],
                OilPrice.symbol == price_data["symbol"]
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                oil_price = OilPrice(
                    timestamp=price_data["timestamp"],
                    symbol=price_data["symbol"],
                    open=Decimal(str(price_data["open"])),
                    high=Decimal(str(price_data["high"])),
                    low=Decimal(str(price_data["low"])),
                    close=Decimal(str(price_data["close"])),
                    volume=price_data["volume"]
                )
                db.add(oil_price)
                saved_count += 1
        
        await db.commit()
        logger.info(f"Saved {saved_count} new oil price records")
        return saved_count


# Global instance
data_service = DataService()
