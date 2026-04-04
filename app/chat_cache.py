import json 
from app.redis_client import redis_client
from uuid import UUID

async def cache_message(room_id: UUID, message:dict):
    key = f"room:{room_id}:messages"
    data = json.dumps(message, default=str)
    async with redis_client.pipeline() as pipe:
        pipe.rpush(key, data)  
        pipe.ltrim(key, -100, -1)  
        await pipe.execute()  

async def get_cached_messages(room_id: UUID, limit: int = 100) -> list[dict]:
    key = f"room:{room_id}:messages"
    data = await redis_client.lrange(key, -limit, -1)  # type: ignore
    return [json.loads(item) for item in data]

async def format_messages_for_ai(room_id: UUID) -> list[str]:
    messages = await get_cached_messages(room_id)
    return [f"{m['sender']}: {m['content']}" for m in messages]