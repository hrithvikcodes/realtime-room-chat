from fastapi import Request
from jose import jwt, JWTError
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
def get_real_ip(request:Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return get_remote_address(request)

def get_user_or_ip(request:Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token,os.getenv("SECRET_KEY"), algorithms=["HS256"]) # type: ignore
            return payload.get("user_id")
        except JWTError:
            pass
    return get_real_ip(request)

limiter = Limiter(key_func=get_user_or_ip,storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379/0")) # type: ignore