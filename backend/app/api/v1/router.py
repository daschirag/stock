"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, historical, sentiment, predict, websocket, insights


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router)
api_router.include_router(historical.router)
api_router.include_router(sentiment.router)
api_router.include_router(predict.router)
api_router.include_router(websocket.router)
api_router.include_router(insights.router)

# Placeholder for additional endpoints (will be added in later phases)
# api_router.include_router(metrics.router, prefix="/metrics")

