from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.audit_logs import AuditLogRepository


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logs = AuditLogRepository(session)

    async def log(self, user_id: int | None, action: str, resource: str) -> None:
        await self.logs.create(user_id, action, resource)

    async def list(self, user_id: int, page: int, size: int):
        return await self.logs.list_for_user(user_id, page, size)

