from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.notifications import NotificationRepository


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notifications = NotificationRepository(session)

    async def create(self, user_id: int, title: str, message: str, type_: str):
        notification = await self.notifications.create(user_id, title, message, type_)
        return notification

    async def list(self, user_id: int, page: int, size: int):
        return await self.notifications.list_for_user(user_id, page, size)

    async def mark_read(self, notification_id: int, user_id: int):
        notification = await self.notifications.get_for_user(notification_id, user_id)
        if notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notification.is_read = True
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: int) -> dict[str, bool]:
        await self.notifications.mark_all_read(user_id)
        await self.session.commit()
        return {"ok": True}

    async def delete(self, notification_id: int, user_id: int) -> None:
        notification = await self.notifications.get_for_user(notification_id, user_id)
        if notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        await self.notifications.delete(notification)
        await self.session.commit()

