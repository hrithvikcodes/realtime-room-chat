from fastapi import Request
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
def get_real_ip(request:Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip,storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379/0"))