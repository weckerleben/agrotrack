from typing import List, Dict, Any
from fastapi import WebSocket
import json
import structlog

logger = structlog.get_logger()

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connection established", total_connections=len(self.active_connections))
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket connection closed", total_connections=len(self.active_connections))
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            self.disconnect(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to broadcast message", error=str(e))
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_silo_update(self, silo_id: int, reading_data: Dict[str, Any]):
        """Broadcast silo reading update"""
        await self.broadcast({
            "type": "silo_reading",
            "silo_id": silo_id,
            "data": reading_data,
            "timestamp": reading_data.get("timestamp")
        })
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast new alert"""
        await self.broadcast({
            "type": "alert",
            "data": alert_data
        })
    
    async def broadcast_logistics_update(self, logistics_id: str, update_data: Dict[str, Any]):
        """Broadcast logistics update"""
        await self.broadcast({
            "type": "logistics_update",
            "logistics_id": logistics_id,
            "data": update_data
        }) 