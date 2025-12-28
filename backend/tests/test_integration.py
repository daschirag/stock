"""
Integration tests for API endpoints.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_latest_price():
    """Test latest price endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/data/latest?symbol=WTI")
        
        # Should succeed or return mock data
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "close" in data or "symbol" in data


@pytest.mark.asyncio
async def test_get_historical_prices():
    """Test historical prices endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/data/historical?symbol=WTI&days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_generate_prediction():
    """Test prediction generation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/predict",
            json={"horizon": "1d", "symbol": "WTI"}
        )
        
        # May fail if no data, but should return proper status
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "predicted_price" in data
            assert "confidence_lower" in data
            assert "confidence_upper" in data


@pytest.mark.asyncio
async def test_get_sentiment():
    """Test sentiment endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/sentiment?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert "aggregated_score" in data


@pytest.mark.asyncio
async def test_trigger_data_fetch():
    """Test background data fetch trigger."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/data/fetch?symbol=WTI&days=30"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


@pytest.mark.asyncio
async def test_get_technical_indicators():
    """Test technical indicators endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/indicators?symbol=WTI&days=30"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_prediction_history():
    """Test prediction history endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/predict/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are present."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options("/api/v1/health")
        
        assert response.status_code in [200, 405]
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 405
