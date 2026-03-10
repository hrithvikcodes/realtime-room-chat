from fastapi import WebSocket
from uuid import UUID
import asyncio
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: UUID):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
    def disconnect(self, websocket: WebSocket, room_id: UUID):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    async def broadcast_to_room(self,room_id:UUID, message: dict):
        if room_id in self.active_connections:
            connections = self.active_connections[room_id]
            tasks = [connection.send_json(message) for connection in connections]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Broadcast error: {result}")
manager = ConnectionManager()        