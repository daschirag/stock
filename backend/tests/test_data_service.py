"""
Test data service.
"""
import pytest
from datetime import datetime, timedelta

from app.services.data_service import DataService


@pytest.mark.asyncio
async def test_fetch_oil_prices_mock():
    """Test fetching oil prices with mock data."""
    service = DataService()
    
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    prices = await service.fetch_oil_prices("WTI", start_date, end_date)
    
    assert len(prices) > 0
    assert all("timestamp" in p for p in prices)
    assert all("symbol" in p for p in prices)
    assert all("close" in p for p in prices)
    
    await service.close()


@pytest.mark.asyncio
async def test_fetch_fred_data_mock():
    """Test FRED data fetching with mock."""
    service = DataService()
    
    start_date = datetime.now() - timedelta(days=30)
    data = await service.fetch_fred_data("DEXUSEU", start_date)
    
    assert len(data) > 0
    assert all("date" in d for d in data)
    assert all("value" in d for d in data)
    
    await service.close()
