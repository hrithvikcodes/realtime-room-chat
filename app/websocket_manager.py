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
    async def broadcast_to_room(self, room_id: UUID, message: dict):
        if room_id not in self.active_connections:
            return

        connections = list(self.active_connections[room_id])

        async def send_safe(conn: WebSocket):
            try:
                await conn.send_json(message)
                return None
            except Exception as e:
                print(f"Broadcast error: {e}")
                return conn  # 

        results = await asyncio.gather(
            *[send_safe(conn) for conn in connections]
        )

    # cleanup dead connections
        for failed_conn in results:
            if failed_conn:
                self.disconnect(failed_conn, room_id)
manager = ConnectionManager()        