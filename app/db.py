import os
from dotenv  import load_dotenv
from collections.abc import AsyncGenerator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import(
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or ""

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session

@asynccontextmanager
async def get_db_context():
    '''
    Manual context manager to get a DB session inside long-running loops (like Websockets)
    '''
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()