from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.settings import SettingsRepository
from app.expense_tracker.schemas import UserSettingsUpdate


class SettingsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = SettingsRepository(session)

    async def get(self, user_id: int):
        settings = await self.settings.get_or_create(user_id)
        await self.session.commit()
        return settings

    async def update(self, user_id: int, data: UserSettingsUpdate):
        settings = await self.settings.get_or_create(user_id)
        settings = await self.settings.update(settings, data)
        await self.session.commit()
        return settings

