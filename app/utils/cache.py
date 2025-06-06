import redis
import json
from app.core.settings import settings

redis_client = redis.Redis(
    host=settings.CACHE_REDIS_HOST,
    port=settings.CACHE_REDIS_PORT,
    db=settings.CACHE_REDIS_DB,
    decode_responses=settings.CACHE_REDIS_DECODE_RESPONSES
)

def cache_get(key: str):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def cache_set(key: str, value, ex: int = 300):
    redis_client.set(key, json.dumps(value), ex=ex)
