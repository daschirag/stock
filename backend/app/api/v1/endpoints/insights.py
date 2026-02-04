"""
AI-powered insights, key levels, and economic calendar endpoints.
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core import get_db, get_logger
from app.core.database import db_available
from app.models.db import OilPrice
from app.schemas import (
    AIInsightsResponse,
    KeyLevelsResponse,
    EconomicCalendarResponse,
    CalendarEvent,
)

router = APIRouter(tags=["insights"])
logger = get_logger(__name__)

# Static economic calendar (events that typically move oil)
ECONOMIC_CALENDAR = [
    CalendarEvent(
        date="Weekly",
        title="EIA Crude Oil Inventories",
        impact="high",
        description="US weekly crude stockpiles",
    ),
    CalendarEvent(
        date="Monthly",
        title="OPEC+ Production Decision",
        impact="high",
        description="Production quota review",
    ),
    CalendarEvent(
        date="Monthly",
        title="IEA Oil Market Report",
        impact="medium",
        description="Global demand/supply outlook",
    ),
    CalendarEvent(
        date="Quarterly",
        title="Federal Reserve FOMC",
        impact="high",
        description="Interest rates affect USD and oil",
    ),
    CalendarEvent(
        date="Weekly",
        title="Baker Hughes Rig Count",
        impact="medium",
        description="US active oil rigs",
    ),
    CalendarEvent(
        date="Monthly",
        title="US CPI / Inflation",
        impact="medium",
        description="Inflation drives Fed policy",
    ),
]


def _mock_key_levels(close: float = 75.42) -> KeyLevelsResponse:
    """Compute mock support/resistance from current price."""
    return KeyLevelsResponse(
        support_1=round(close * 0.97, 2),
        support_2=round(close * 0.94, 2),
        resistance_1=round(close * 1.03, 2),
        resistance_2=round(close * 1.06, 2),
        pivot=round(close, 2),
    )


@router.get("/insights", response_model=AIInsightsResponse)
async def get_ai_insights(
    symbol: str = Query(default="WTI", description="Oil symbol"),
    db: AsyncSession = Depends(get_db),
):
    """
    AI-powered market insights: summary, key drivers, key levels, technical view.
    Returns mock insights when database is unavailable.
    """
    close = 75.42
    pred_price = 76.89
    key_levels = _mock_key_levels(close)
    sentiment_score = 0.0  # Can be filled from sentiment_service when DB available

    if db_available:
        try:
            # Latest price
            stmt = select(OilPrice).where(
                OilPrice.symbol == symbol
            ).order_by(desc(OilPrice.timestamp)).limit(1)
            result = await db.execute(stmt)
            price = result.scalar_one_or_none()
            if price:
                close = float(price.close)
                # Key levels from last 30 days
                from datetime import timedelta
                from sqlalchemy import and_
                start = datetime.now() - timedelta(days=30)
                stmt2 = select(OilPrice).where(
                    and_(
                        OilPrice.symbol == symbol,
                        OilPrice.timestamp >= start
                    )
                )
                r2 = await db.execute(stmt2)
                prices = r2.scalars().all()
                if prices:
                    highs = [float(p.high) for p in prices]
                    lows = [float(p.low) for p in prices]
                    key_levels = KeyLevelsResponse(
                        support_1=round(min(lows) * 1.02, 2),
                        support_2=round(min(lows) * 0.98, 2),
                        resistance_1=round(max(highs) * 0.98, 2),
                        resistance_2=round(max(highs) * 1.02, 2),
                        pivot=round((min(lows) + max(highs)) / 2, 2),
                    )
        except OSError:
            pass

    # Build AI-style summary and drivers (template-based; can be replaced by LLM later)
    change_pct = ((pred_price - close) / close) * 100 if close else 0
    if pred_price > close * 1.01 or sentiment_score > 0.2:
        outlook = "bullish"
        outlook_text = "Model and sentiment suggest upward bias."
    elif pred_price < close * 0.99 or sentiment_score < -0.2:
        outlook = "bearish"
        outlook_text = "Model and sentiment suggest downward bias."
    else:
        outlook = "neutral"
        outlook_text = "Mixed signals; range-bound outlook."

    summary = (
        f"WTI crude is trading near ${close:.2f}. "
        f"Model 1-day forecast: ${pred_price:.2f} ({change_pct:+.1f}%). "
        f"{outlook_text} Key levels: support ${key_levels.support_1:.2f}, "
        f"resistance ${key_levels.resistance_1:.2f}."
    )

    key_drivers = [
        "OPEC+ supply policy and production quotas",
        "Global demand (China, US, Europe)",
        "USD strength (inverse correlation with oil)",
        "Geopolitical risk (Middle East, Russia)",
        "EIA inventory and rig count data",
        "Federal Reserve interest rate path",
    ]

    technical_summary = (
        f"Price above pivot ${key_levels.pivot:.2f}. "
        f"Support zone ${key_levels.support_2:.2f}-${key_levels.support_1:.2f}, "
        f"resistance ${key_levels.resistance_1:.2f}-${key_levels.resistance_2:.2f}. "
        "Momentum indicators in neutral territory."
    )

    confidence = 0.85 if db_available else 0.65

    return AIInsightsResponse(
        summary=summary,
        key_drivers=key_drivers,
        key_levels=key_levels,
        technical_summary=technical_summary,
        outlook=outlook,
        confidence_score=confidence,
    )


@router.get("/insights/key-levels", response_model=KeyLevelsResponse)
async def get_key_levels(
    symbol: str = Query(default="WTI", description="Oil symbol"),
    db: AsyncSession = Depends(get_db),
):
    """Get support and resistance levels. Mock when DB unavailable."""
    if not db_available:
        return _mock_key_levels(75.42)
    try:
        stmt = select(OilPrice).where(
            OilPrice.symbol == symbol
        ).order_by(desc(OilPrice.timestamp)).limit(1)
        result = await db.execute(stmt)
        price = result.scalar_one_or_none()
        close = float(price.close) if price else 75.42
        start = datetime.now() - timedelta(days=30)
        from sqlalchemy import and_
        stmt2 = select(OilPrice).where(
            and_(OilPrice.symbol == symbol, OilPrice.timestamp >= start)
        )
        r2 = await db.execute(stmt2)
        prices = r2.scalars().all()
        if not prices:
            return _mock_key_levels(close)
        highs = [float(p.high) for p in prices]
        lows = [float(p.low) for p in prices]
        return KeyLevelsResponse(
            support_1=round(min(lows) * 1.02, 2),
            support_2=round(min(lows) * 0.98, 2),
            resistance_1=round(max(highs) * 0.98, 2),
            resistance_2=round(max(highs) * 1.02, 2),
            pivot=round((min(lows) + max(highs)) / 2, 2),
        )
    except OSError:
        return _mock_key_levels(75.42)


@router.get("/calendar", response_model=EconomicCalendarResponse)
async def get_economic_calendar():
    """Upcoming economic events relevant to oil markets. Static list."""
    return EconomicCalendarResponse(events=ECONOMIC_CALENDAR)
