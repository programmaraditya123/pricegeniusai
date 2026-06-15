from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int | None, action: str, resource: str) -> AuditLog:
        log = AuditLog(user_id=user_id, action=action, resource=resource)
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_for_user(self, user_id: int, page: int, size: int) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all())

