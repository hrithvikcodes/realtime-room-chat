from fastapi import FastAPI
from app.routers import user
from app.routers import room
from contextlib import asynccontextmanager
from app import db
from app.routers import message
from app.routers import websocket
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)
    
    yield  # The app runs while this is paused
    
    #  Shutdown: Clean up if needed 
    await db.engine.dispose()

app = FastAPI(lifespan=lifespan)


app.include_router(user.router)
app.include_router(room.router)
app.include_router(message.router)
app.include_router(websocket.router)

@app.get("/health")
async def health_check():
    return {"status": "OK"}
