"""
Most-Wanted Identification System
MongoDB Async Connection via Motor
"""
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

_client: AsyncIOMotorClient = None


async def connect_db():
    global _client
    _client = AsyncIOMotorClient(settings.MONGO_URI)
    print(f"[DB] Connected to MongoDB: {settings.MONGO_URI}")


async def close_db():
    global _client
    if _client:
        _client.close()
        print("[DB] MongoDB connection closed.")


def get_db():
    return _client[settings.MONGO_DB_NAME]
