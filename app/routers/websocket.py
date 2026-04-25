from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket_manager import manager
from app.db import get_db_context
from app.auth import get_user_from_token
from app.crud.messages import send_message
from app.models.room import Room  
from app.chat_cache import cache_message
from uuid import UUID
from app.logger import get_logger
logger = get_logger("websocket.router")
router = APIRouter()

@router.websocket("/ws/{room_id}")
async def chat_socket(websocket: WebSocket, room_id: UUID, token: str = Query(...)):

    try:
        async with get_db_context() as db:
            user = await get_user_from_token(token, "access", db)
            room = await db.get(Room, room_id)
            if not room:
                logger.warning("WebSocket connection attempt to non-existent room")
                await websocket.close(code=1008)
                
                return
    except Exception as e:
        logger.error("Authentication error", extra={"room_id": room_id, "error": str(e)})
        await websocket.close(code=403)
        return

    await manager.connect(websocket, room_id)
    logger.info("User connected to room", extra={"room_id": room_id, "user_id": user.id}) 

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                raise
            except Exception:
                logger.error("Failed to receive JSON data", extra={"room_id": room_id})
                try:
                    await websocket.send_json({"error": "Invalid JSON"})
                except Exception as e:
                    logger.error("Failed to send error message", extra={"room_id": room_id, "error": str(e)})
                    break
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
                logger.error("Failed to send message", extra={"room_id": room_id, "error": str(e)})
                try:
                    await websocket.send_json({"error": "Message failed"})
                except Exception as e:
                    logger.error("Failed to send error message", extra={"room_id": room_id, "error": str(e)})
                    break
                continue

            message = {
                "sender": user.name,
                "content": content,
                "created_at": str(new_msg.posted_at),
                "media_url": new_msg.media_url
            }

            try:
                await manager.broadcast_to_room(room_id, message)
            except Exception as e:
                logger.error("Failed to broadcast message to WebSocket clients", extra={"room_id": room_id, "error": str(e)})

            try:
                await cache_message(room_id=room_id, message=message)
            except Exception as e:
                logger.error("Failed to cache message", extra={"room_id": room_id, "error": str(e)})

    except WebSocketDisconnect:
        
        logger.info("User disconnected from room", extra={"room_id": room_id, "user_id": user.id})
    except Exception as e:
        logger.error("FATAL WS ERROR", extra={"room_id": room_id, "error": str(e)})
        
    finally:
        await manager.disconnect(websocket, room_id)