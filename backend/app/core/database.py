"""
Database connection and session management.
"""
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)

# Set to False if init_db() fails (e.g. no PostgreSQL running). App still starts.
db_available = True


# Convert postgres:// to postgresql+asyncpg://
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgres://", "postgresql+asyncpg://")


# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=False,
    poolclass=NullPool if settings.environment == "test" else None,
    pool_pre_ping=True,
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection. Does not raise if DB is unavailable (e.g. no PostgreSQL)."""
    global db_available
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as e:
        db_available = False
        logger.warning(
            "Database unavailable (app will start anyway; DB endpoints will fail until PostgreSQL is running): %s",
            e,
        )


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")
