import redis.asyncio as redis
import json
from backend.app.core.settings import settings

redis_client = redis.Redis(
    host=settings.CACHE_REDIS_HOST,
    port=settings.CACHE_REDIS_PORT,
    db=settings.CACHE_REDIS_DB,
    decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES
)


async def cache_get(key: str):
    value = await redis_client.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value, ex: int = 300):
    await redis_client.set(key, json.dumps(value), ex=ex)
