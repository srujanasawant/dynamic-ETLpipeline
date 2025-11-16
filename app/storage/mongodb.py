from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDBStorage:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client.get_default_database()

    async def insert_record(self, collection: str, document: Dict[str, Any]) -> str:
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)

    async def find_records(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.db[collection].find(filters or {}).limit(limit)
        return [doc async for doc in cursor]

    async def get_record(self, collection: str, record_id: Any) -> Optional[Dict[str, Any]]:
        return await self.db[collection].find_one({"_id": record_id})
