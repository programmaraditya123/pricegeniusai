from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, title: str, message: str, type_: str) -> Notification:
        notification = Notification(user_id=user_id, title=title, message=message, type=type_)
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def list_for_user(self, user_id: int, page: int, size: int) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all())

    async def get_for_user(self, notification_id: int, user_id: int) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def mark_all_read(self, user_id: int) -> None:
        await self.session.execute(
            update(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False)).values(is_read=True)
        )

    async def delete(self, notification: Notification) -> None:
        await self.session.delete(notification)

