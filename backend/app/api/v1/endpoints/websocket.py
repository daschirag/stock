"""
WebSocket endpoint for real-time price updates.
"""
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio
import json

from app.core import get_logger
from app.services import data_service


router = APIRouter(tags=["websocket"])
logger = get_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.
    
    Sends price updates every 5 seconds.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # In production, fetch real price from data service
            # For now, simulate with mock data
            price_data = {
                "timestamp": datetime.now().isoformat(),
                "symbol": "WTI",
                "price": 75.42 + (asyncio.get_running_loop().time() % 10 - 5) * 0.5,
                "change": 1.23,
                "change_percent": 1.65
            }
            
            await websocket.send_json(price_data)
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/predictions")
async def websocket_predictions(websocket: WebSocket):
    """
    WebSocket endpoint for real-time prediction updates.
    
    Sends new predictions when they become available.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Simulate prediction update every 30 seconds
            prediction_data = {
                "timestamp": datetime.now().isoformat(),
                "horizon": "1d",
                "predicted_price": 76.89,
                "confidence_lower": 74.21,
                "confidence_upper": 79.57,
                "model_version": "v1.0.0"
            }
            
            await websocket.send_json(prediction_data)
            await asyncio.sleep(30)  # Update every 30 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_price_update(price_data: dict):
    """
    Broadcast price update to all connected clients.
    
    Call this from background tasks or data fetching services.
    """
    await manager.broadcast({
        "type": "price_update",
        "data": price_data
    })
