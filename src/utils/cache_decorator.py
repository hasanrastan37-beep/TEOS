import functools
import hashlib
import json
from src.core.redis import redis

def redis_cache(ttl: int = 300):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # ساخت کلید
            key_data = json.dumps({"args": args[1:], "kwargs": kwargs}, sort_keys=True)
            key = f"cache:{func.__name__}:{hashlib.md5(key_data.encode()).hexdigest()}"
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
