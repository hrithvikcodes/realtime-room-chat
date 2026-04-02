from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket_manager import manager
from app.db import get_db_context
from app.auth import get_user_from_token
from app.crud.messages import send_message
from app.models.room import Room  
from uuid import UUID

router = APIRouter()

@router.websocket("/ws/{room_id}")
async def chat_socket(websocket: WebSocket, room_id: UUID, token: str = Query(...)):

    
    try:
        async with get_db_context() as db:
            user = await get_user_from_token(token, "access", db)

            room = await db.get(Room, room_id)
            if not room:
                await websocket.close(code=1008)
                return

    except Exception as e:
        print("AUTH ERROR:", e)
        await websocket.close(code=403)
        return

    await manager.connect(websocket, room_id)

    try:
        while True:
            
            try:
                data = await websocket.receive_json()
            except Exception:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            content = data.get("content")
            if not content:
                continue

            
            try:
                async with get_db_context() as db:
                    new_msg = await send_message(
                        room_id=room_id,
                        user_id=user.id,
                        db=db,
                        content=content,
                        file=None
                    )
            except Exception as e:
                print("DB ERROR:", e)
                await websocket.send_json({"error": "Message failed"})
                continue

            
            try:
                await manager.broadcast_to_room(room_id, {
                    "sender": user.name,
                    "content": content,
                    "created_at": str(new_msg.posted_at),
                    "media_url": new_msg.media_url
                })
            except Exception as e:
                print("BROADCAST ERROR:", e)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

    except Exception as e:
        print("FATAL WS ERROR:", e)
        manager.disconnect(websocket, room_id)
        await websocket.close()