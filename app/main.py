import os
from fastapi import FastAPI
from app.routers import user
from app.routers import room
from contextlib import asynccontextmanager
from app import db
from app.routers import message
from app.routers import websocket
from app.middleware import log_requests
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import  _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield  # 
    
    #  Shutdown
    await db.engine.dispose()

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore

app.include_router(user.router)
app.include_router(room.router)
app.include_router(message.router)
app.include_router(websocket.router)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)   

@app.get("/health")
async def health_check():
    return {"status": "OK"}
