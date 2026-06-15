from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import Category


DEFAULT_CATEGORIES = ["Food", "Shopping", "Travel", "Health", "Education", "Bills", "Entertainment", "Rent"]


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def get(self, category_id: int) -> Category | None:
        return await self.session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.name.ilike(name)))
        return result.scalar_one_or_none()

    async def ensure_defaults(self) -> None:
        for name in DEFAULT_CATEGORIES:
            stmt = insert(Category).values(name=name, is_default=True).on_conflict_do_nothing(index_elements=["name"])
            await self.session.execute(stmt)

