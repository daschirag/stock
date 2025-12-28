"""
Test configuration settings.
"""
import pytest
from app.core.config import settings


def test_settings_load():
    """Test that settings load correctly."""
    assert settings is not None
    assert settings.environment in ["development", "production", "test"]
    assert settings.database_url is not None


def test_cors_origins_list():
    """Test CORS origins parsing."""
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) > 0


def test_api_keys_detection():
    """Test API key detection."""
    has_keys = settings.has_api_keys
    assert isinstance(has_keys, bool)
