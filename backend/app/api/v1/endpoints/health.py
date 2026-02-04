"""
Health check endpoint.
"""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import db_available, engine
from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify API and database connectivity.
    Works even when database is unavailable at startup.
    """
    if not db_available:
        return HealthResponse(
            status="healthy",
            database="unavailable",
        )
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "disconnected"
    return HealthResponse(
        status="healthy" if database_status == "connected" else "unhealthy",
        database=database_status,
    )
