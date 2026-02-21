"""
Main FastAPI application.
Production-ready for Railway / Render / Docker.
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import (
    settings,
    setup_logging,
    get_logger,
    set_correlation_id,
    init_db,
    close_db,
)
from app.api.v1 import api_router


# -------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------
setup_logging()
logger = get_logger(__name__)


# -------------------------------------------------------------------
# Lifespan (startup & shutdown)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Crude Oil Price Prediction API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Using mock data: {not settings.has_api_keys}")

    # Initialize database (safe if DB is not configured)
    try:
        await init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.warning(f"Database not available, continuing without DB: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Crude Oil Price Prediction API")
    try:
        await close_db()
    except Exception:
        pass


# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(
    title="Crude Oil Price Prediction API",
    description="State-of-the-art hybrid ML models for crude oil price prediction",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# -------------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Correlation ID Middleware
# -------------------------------------------------------------------
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """
    Adds a correlation ID to every request for tracing.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    set_correlation_id(correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id

    return response


# -------------------------------------------------------------------
# Global Exception Handler
# -------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        },
    )


# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")


# -------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Crude Oil Price Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# -------------------------------------------------------------------
# Uvicorn entry point (REQUIRED FOR CLOUD DEPLOYMENT)
# -------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )