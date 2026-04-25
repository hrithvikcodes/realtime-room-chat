
from fastapi import WebSocket
from uuid import UUID
import asyncio
from app.logger import get_logger


logger = get_logger("websocket_manager")

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    async def connect(self, websocket: WebSocket, room_id: UUID):
        await websocket.accept()
        async with self._lock:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = set()
            self.active_connections[room_id].add(websocket)
            logger.info("WebSocket connection added", extra={"room_id": room_id, "total_connections": len(self.active_connections[room_id])})
    async def disconnect(self, websocket: WebSocket, room_id: UUID):
        async with self._lock:
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
        logger.info("WebSocket connection removed", extra={"room_id": room_id})
    async def broadcast_to_room(self, room_id: UUID, message: dict):
        async with self._lock:
            connections = list(self.active_connections.get(room_id, set()))
        if not connections:
            return
        async def send_safe(conn: WebSocket):
            try:
                await conn.send_json(message)
                return None
            except Exception as e:
                logger.error("Failed to send message to WebSocket client", extra={"room_id": room_id, "error": str(e)})
                return conn
        results = await asyncio.gather(*(send_safe(conn) for conn in connections))
        failed_conns = [conn for conn in results if conn is not None]
        for dead in failed_conns:
            await self.disconnect(dead, room_id)    
manager = ConnectionManager()

                               