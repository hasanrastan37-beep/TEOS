import redis.asyncio as aioredis
from src.core.settings import settings

redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_redis():
    return redis
