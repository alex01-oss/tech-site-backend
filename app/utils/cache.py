import json
from redis.asyncio import Redis as AsyncRedis
from typing import Any, Optional

from app.core.settings import settings

redis_client = AsyncRedis(
    host=settings.CACHE_REDIS_HOST,
    port=settings.CACHE_REDIS_PORT,
    db=settings.CACHE_REDIS_DB,
    decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES,
    password=settings.CACHE_REDIS_PASSWORD
)

async def cache_get(key: str) -> Optional[Any]:
    if settings.DISABLE_REDIS_CACHE:
        return None
        
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, ex: int = 300):
    if settings.DISABLE_REDIS_CACHE:
        return
        
    await redis_client.set(key, json.dumps(value), ex=ex)