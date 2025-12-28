"""
Test technical indicators.
"""
import pytest
import pandas as pd
import numpy as np

from app.services.technical_indicators import TechnicalIndicatorService


def test_calculate_rsi():
    """Test RSI calculation."""
    service = TechnicalIndicatorService()
    
    # Create sample price data
    prices = pd.Series([44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64])
    
    rsi = service.calculate_rsi(prices, period=14)
    
    assert len(rsi) == len(prices)
    assert not rsi.isna().all()


def test_calculate_macd():
    """Test MACD calculation."""
    service = TechnicalIndicatorService()
    
    # Create sample price data
    prices = pd.Series(np.random.randn(100).cumsum() + 100)
    
    macd_line, signal_line, histogram = service.calculate_macd(prices)
    
    assert len(macd_line) == len(prices)
    assert len(signal_line) == len(prices)
    assert len(histogram) == len(prices)


def test_calculate_bollinger_bands():
    """Test Bollinger Bands calculation."""
    service = TechnicalIndicatorService()
    
    prices = pd.Series(np.random.randn(100).cumsum() + 100)
    
    upper, middle, lower = service.calculate_bollinger_bands(prices, period=20)
    
    assert len(upper) == len(prices)
    assert len(middle) == len(prices)
    assert len(lower) == len(prices)


def test_calculate_ichimoku():
    """Test Ichimoku Cloud calculation."""
    service = TechnicalIndicatorService()
    
    n = 100
    high = pd.Series(np.random.randn(n).cumsum() + 105)
    low = pd.Series(np.random.randn(n).cumsum() + 95)
    close = pd.Series(np.random.randn(n).cumsum() + 100)
    
    ichimoku = service.calculate_ichimoku(high, low, close)
    
    assert "tenkan_sen" in ichimoku
    assert "kijun_sen" in ichimoku
    assert "senkou_span_a" in ichimoku
    assert "senkou_span_b" in ichimoku
    assert "chikou_span" in ichimoku


def test_calculate_obv():
    """Test OBV calculation."""
    service = TechnicalIndicatorService()
    
    close = pd.Series(np.random.randn(50).cumsum() + 100)
    volume = pd.Series(np.random.randint(100000, 500000, size=50))
    
    obv = service.calculate_obv(close, volume)
    
    assert len(obv) == len(close)
