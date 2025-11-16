# app/storage/redis_cache.py
import json
import structlog
from typing import Any, Optional
from app.models.database import get_redis

logger = structlog.get_logger()


class RedisCache:
    """Redis caching utilities"""
    
    def __init__(self):
        self.ttl = 3600  # 1 hour default TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis = await get_redis()
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Cache get failed", exc_info=e, key=key)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            redis = await get_redis()
            await redis.set(
                key,
                json.dumps(value),
                ex=ttl or self.ttl
            )
            return True
        except Exception as e:
            logger.warning("Cache set failed", exc_info=e, key=key)
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis = await get_redis()
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", exc_info=e, key=key)
            return False