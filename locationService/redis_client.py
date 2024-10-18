import redis.asyncio as redis

from config import settings


class RedisFactory:
    """
    Factory class to manage Redis connections using async context manager.
    """
    def __init__(self):
        self.redis_client = None

    async def __aenter__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.redis_client:
            await self.redis_client.close()

# Dependency function to inject Redis client using FastAPI
async def get_redis() -> redis.Redis:
    async with RedisFactory() as redis_client:
        return redis_client