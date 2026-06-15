import json
from typing import Any

from redis.asyncio import Redis

from app.expense_tracker.config import get_settings


class CacheService:
    def __init__(self, redis: Redis | None = None):
        self.redis = redis or Redis.from_url(get_settings().redis_url, decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

