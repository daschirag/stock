"""
Technical indicators calculation service.
Implements Ichimoku Cloud, RSI, MACD, Bollinger Bands, and OBV.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core import get_logger
from app.models.db import OilPrice, TechnicalIndicator


logger = get_logger(__name__)


class TechnicalIndicatorService:
    """Service for calculating technical indicators."""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series
            period: RSI period (default 14)
        
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Avoid division by zero when loss is 0 (replace 0 with small value)
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Price series
            period: Moving average period
            std_dev: Standard deviation multiplier
        
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle_band = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_ichimoku(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series
    ) -> Dict[str, pd.Series]:
        """
        Calculate Ichimoku Cloud components.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
        
        Returns:
            Dictionary with Ichimoku components
        """
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        period9_high = high.rolling(window=9).max()
        period9_low = low.rolling(window=9).min()
        tenkan_sen = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        period26_high = high.rolling(window=26).max()
        period26_low = low.rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen) / 2, shifted 26 periods ahead
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, shifted 26 periods ahead
        period52_high = high.rolling(window=52).max()
        period52_low = low.rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span): Close price shifted 26 periods back
        chikou_span = close.shift(-26)
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "chikou_span": chikou_span
        }
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            close: Close price series
            volume: Volume series
        
        Returns:
            OBV series
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]
        
        return obv
    
    async def calculate_all_indicators(
        self,
        db: AsyncSession,
        symbol: str = "WTI",
        lookback_days: int = 365
    ) -> int:
        """
        Calculate all technical indicators for oil prices.
        
        Args:
            db: Database session
            symbol: Oil symbol
            lookback_days: Number of days to look back
        
        Returns:
            Number of indicator records saved
        """
        # Fetch price data
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        stmt = select(OilPrice).where(
            and_(
                OilPrice.symbol == symbol,
                OilPrice.timestamp >= start_date
            )
        ).order_by(OilPrice.timestamp)
        
        result = await db.execute(stmt)
        prices = result.scalars().all()
        
        if not prices:
            logger.warning(f"No price data found for {symbol}")
            return 0
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "timestamp": p.timestamp,
            "open": float(p.open),
            "high": float(p.high),
            "low": float(p.low),
            "close": float(p.close),
            "volume": p.volume
        } for p in prices])
        
        df.set_index("timestamp", inplace=True)
        
        # Calculate indicators
        indicators_data = []
        
        # RSI
        rsi = self.calculate_rsi(df["close"])
        for timestamp, value in rsi.items():
            if not pd.isna(value):
                indicators_data.append({
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "indicator_name": "RSI",
                    "value": float(value)
                })
        
        # MACD
        macd_line, signal_line, histogram = self.calculate_macd(df["close"])
        for timestamp in macd_line.index:
            if not pd.isna(macd_line[timestamp]):
                indicators_data.extend([
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "MACD_LINE",
                        "value": float(macd_line[timestamp])
                    },
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "MACD_SIGNAL",
                        "value": float(signal_line[timestamp])
                    },
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "MACD_HISTOGRAM",
                        "value": float(histogram[timestamp])
                    }
                ])
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df["close"])
        for timestamp in bb_upper.index:
            if not pd.isna(bb_upper[timestamp]):
                indicators_data.extend([
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "BB_UPPER",
                        "value": float(bb_upper[timestamp])
                    },
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "BB_MIDDLE",
                        "value": float(bb_middle[timestamp])
                    },
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": "BB_LOWER",
                        "value": float(bb_lower[timestamp])
                    }
                ])
        
        # Ichimoku Cloud
        ichimoku = self.calculate_ichimoku(df["high"], df["low"], df["close"])
        for component_name, series in ichimoku.items():
            for timestamp, value in series.items():
                if not pd.isna(value):
                    indicators_data.append({
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "indicator_name": f"ICHIMOKU_{component_name.upper()}",
                        "value": float(value)
                    })
        
        # OBV
        obv = self.calculate_obv(df["close"], df["volume"])
        for timestamp, value in obv.items():
            if not pd.isna(value):
                indicators_data.append({
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "indicator_name": "OBV",
                    "value": float(value)
                })
        
        # Volume MA
        volume_ma = df["volume"].rolling(window=20).mean()
        for timestamp, value in volume_ma.items():
            if not pd.isna(value):
                indicators_data.append({
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "indicator_name": "VOLUME_MA",
                    "value": float(value)
                })
        
        # Save to database
        saved_count = 0
        for indicator in indicators_data:
            # Check if exists
            stmt = select(TechnicalIndicator).where(
                and_(
                    TechnicalIndicator.timestamp == indicator["timestamp"],
                    TechnicalIndicator.symbol == indicator["symbol"],
                    TechnicalIndicator.indicator_name == indicator["indicator_name"]
                )
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                tech_indicator = TechnicalIndicator(
                    timestamp=indicator["timestamp"],
                    symbol=indicator["symbol"],
                    indicator_name=indicator["indicator_name"],
                    value=Decimal(str(indicator["value"]))
                )
                db.add(tech_indicator)
                saved_count += 1
        
        await db.commit()
        logger.info(f"Saved {saved_count} technical indicator records for {symbol}")
        return saved_count


# Global instance
technical_indicator_service = TechnicalIndicatorService()
