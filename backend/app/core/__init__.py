"""
Core package initialization.
"""
from app.core.config import settings
from app.core.logging import setup_logging, get_logger, set_correlation_id, get_correlation_id
from app.core.database import get_db, init_db, close_db


__all__ = [
    "settings",
    "setup_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "get_db",
    "init_db",
    "close_db",
]
