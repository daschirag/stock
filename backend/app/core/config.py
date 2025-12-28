"""
Configuration settings using Pydantic Settings for the application.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/crude_oil_db",
        description="PostgreSQL database URL"
    )
    
    # Environment
    environment: str = Field(default="development", description="Environment (development/production)")
    
    # API Keys
    eia_api_key: str = Field(default="", description="EIA API key")
    fred_api_key: str = Field(default="", description="FRED API key")
    news_api_key: str = Field(default="", description="NewsAPI key")
    twitter_bearer_token: str = Field(default="", description="Twitter API bearer token")
    
    # Model Configuration
    model_version: str = Field(default="v1.0.0", description="Current model version")
    sequence_length: int = Field(default=60, description="Sequence length for time series")
    batch_size: int = Field(default=32, description="Training batch size")
    epochs: int = Field(default=100, description="Training epochs")
    learning_rate: float = Field(default=0.001, description="Learning rate")
    
    # Backend Configuration
    backend_host: str = Field(default="0.0.0.0", description="Backend host")
    backend_port: int = Field(default=8000, description="Backend port")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="CORS allowed origins (comma-separated)"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")
    
    # GPU Configuration
    use_gpu: str = Field(default="auto", description="GPU usage (auto/true/false)")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"
    
    @property
    def has_api_keys(self) -> bool:
        """Check if any API keys are configured."""
        return bool(
            self.eia_api_key or 
            self.fred_api_key or 
            self.news_api_key or 
            self.twitter_bearer_token
        )


# Global settings instance
settings = Settings()
