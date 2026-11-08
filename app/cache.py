from redis.asyncio import Redis

from app.config import settings

redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_from_cache(key: str) -> str | None:
    return await redis.get(key)


async def set_to_cache(key: str, value: str, ttl: int = 3600) -> None:
    await redis.set(key, value, ex=ttl)


async def increment_stat(key: str) -> int:
    return await redis.incr(key)


async def get_stat(key: str) -> int:
    val = await redis.get(key)
    return int(val) if val else 0