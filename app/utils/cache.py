import json
import redis
from typing import Any, Optional

from app.core.settings import settings

redis_client = redis.Redis(
    host=settings.CACHE_REDIS_HOST,
    port=settings.CACHE_REDIS_PORT,
    db=settings.CACHE_REDIS_DB,
    decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES,
    password=settings.CACHE_REDIS_PASSWORD
)

async def cache_get(key: str) -> Optional[Any]:
    if settings.DISABLE_REDIS_CACHE:
        # print(f"CACHE_GET: Cache disabled, returning None for key: {key}")
        return None
        
    value = await redis_client.get(key)
    if value:
        # print(f"CACHE_GET: Cache hit for key: {key}")
        return json.loads(value)
    # print(f"CACHE_GET: Cache miss for key: {key}")
    return None


async def cache_set(key: str, value: Any, ex: int = 300):
    if settings.DISABLE_REDIS_CACHE:
        # print(f"CACHE_SET: Cache disabled, skipping set for key: {key}")
        return
        
    # print(f"CACHE_SET: Setting cache for key: {key} with expiration {ex}s")
    await redis_client.set(key, json.dumps(value), ex=ex)