import json
from datetime import UTC, datetime
from typing import Any

from redis.asyncio import Redis

from app.expense_tracker.config import get_settings


class RedisJobQueue:
    queue_key = "expense_tracker:jobs"

    def __init__(self, redis: Redis | None = None):
        self.redis = redis or Redis.from_url(get_settings().redis_url, decode_responses=True)

    async def enqueue(self, task: str, payload: dict[str, Any] | None = None) -> None:
        message = {"task": task, "payload": payload or {}, "queued_at": datetime.now(UTC).isoformat()}
        await self.redis.lpush(self.queue_key, json.dumps(message))

    async def dequeue(self, timeout: int = 5) -> dict[str, Any] | None:
        item = await self.redis.brpop(self.queue_key, timeout=timeout)
        if item is None:
            return None
        return json.loads(item[1])


class BackgroundJobService:
    def __init__(self, queue: RedisJobQueue | None = None):
        self.queue = queue or RedisJobQueue()

    async def enqueue_monthly_insights(self, user_id: int, month: int, year: int) -> None:
        await self.queue.enqueue("monthly_insights_generation", {"user_id": user_id, "month": month, "year": year})

    async def enqueue_budget_alerts(self, user_id: int, month: int, year: int) -> None:
        await self.queue.enqueue("budget_alerts", {"user_id": user_id, "month": month, "year": year})

    async def enqueue_cleanup_expired_tokens(self) -> None:
        await self.queue.enqueue("cleanup_expired_tokens")

    async def enqueue_report_generation(self, user_id: int, month: int, year: int) -> None:
        await self.queue.enqueue("report_generation", {"user_id": user_id, "month": month, "year": year})
