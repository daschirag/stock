"""
Database connection and session management.
Safe for environments without PostgreSQL (Railway / local / CI).
"""

import os
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# -------------------------------------------------------------------
# Database availability flag
# -------------------------------------------------------------------
db_available: bool = True

engine = None
AsyncSessionLocal: Optional[async_sessionmaker] = None


# -------------------------------------------------------------------
# Initialize engine safely
# -------------------------------------------------------------------
def _create_engine():
    """
    Create async SQLAlchemy engine if DATABASE_URL is available.
    """
    global db_available

    if not settings.database_url:
        logger.warning("DATABASE_URL not set. Running without database.")
        db_available = False
        return None

    try:
        async_database_url = (
            settings.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
            .replace("postgres://", "postgresql+asyncpg://")
        )

        return create_async_engine(
            async_database_url,
            echo=False,
            poolclass=NullPool if settings.environment == "test" else None,
            pool_pre_ping=True,
        )

    except Exception as e:
        logger.warning(
            "Failed to create database engine. Continuing without DB: %s", e
        )
        db_available = False
        return None


# Create engine and session factory
engine = _create_engine()

if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# -------------------------------------------------------------------
# Dependency
# -------------------------------------------------------------------
async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    Dependency for getting async database session.
    Returns None if DB is unavailable.
    """
    if not db_available or not AsyncSessionLocal:
        yield None
        return

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# -------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------
async def init_db() -> None:
    """
    Initialize database connection.
    Does NOT crash app if DB is unavailable.
    """
    global db_available

    if not engine:
        db_available = False
        return

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
        db_available = True
    except Exception as e:
        db_available = False
        logger.warning(
            "Database unavailable. App will run without DB: %s", e
        )


# -------------------------------------------------------------------
# Shutdown
# -------------------------------------------------------------------
async def close_db() -> None:
    """
    Close database connection.
    """
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")