from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import UserSettings
from app.expense_tracker.schemas import UserSettingsUpdate


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int) -> UserSettings:
        result = await self.session.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        settings = result.scalar_one_or_none()
        if settings is None:
            settings = UserSettings(user_id=user_id)
            self.session.add(settings)
            await self.session.flush()
            await self.session.refresh(settings)
        return settings

    async def update(self, settings: UserSettings, data: UserSettingsUpdate) -> UserSettings:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, key, value)
        await self.session.flush()
        await self.session.refresh(settings)
        return settings

