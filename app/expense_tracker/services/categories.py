from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.categories import CategoryRepository


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.categories = CategoryRepository(session)

    async def ensure_defaults(self) -> None:
        await self.categories.ensure_defaults()
        await self.session.commit()

    async def list(self):
        return await self.categories.list()

