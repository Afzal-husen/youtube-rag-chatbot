import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Ensure the storage directory exists
STORAGE_PATH = "backend/storage"
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

DATABASE_URL = f"sqlite+aiosqlite:///{STORAGE_PATH}/chatbot.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
