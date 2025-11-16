# app/models/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import redis.asyncio as aioredis
from pymongo import MongoClient
from app.config import settings
import os

# ---------------------------
# PostgreSQL (async)
# ---------------------------
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------
# MongoDB
# ---------------------------
mongo_client = MongoClient(settings.MONGODB_URL)
mongo_db = mongo_client.get_default_database()

def get_mongo():
    return mongo_db


# ---------------------------
# Redis
# ---------------------------
redis_client = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True
)

async def get_redis():
    return redis_client


# ---------------------------
# Init DB
# ---------------------------
async def init_db():
    """
    Create all SQLAlchemy tables that inherit from Base
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return True
