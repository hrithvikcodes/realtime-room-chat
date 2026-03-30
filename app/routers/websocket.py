from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket_manager import manager
from app.db import get_db_context
from app.auth import get_current_user, get_user_from_token
from app.crud.messages import send_message
from uuid import UUID

router = APIRouter()

@router.websocket("/ws/{room_id}")
async def chat_socket(websocket: WebSocket, room_id:UUID, token: str = Query(...)):
    
    try:
        async with get_db_context() as db:
            user = await get_user_from_token(token, "access",db)
            

    except Exception:
        await websocket.close(code=403)
        return
    
    await manager.connect(websocket, room_id)
    try: 
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue
            async with get_db_context() as db:
                new_msg = await send_message(room_id = room_id, user_id = user.id, db = db , content = content, file = None)
            await manager.broadcast_to_room(room_id, {
                "sender" : user.name,
                "content": content,
                "created_at": str(new_msg.posted_at),
                "media_url": new_msg.media_url
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)