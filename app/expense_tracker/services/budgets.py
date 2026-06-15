from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.budgets import BudgetRepository
from app.expense_tracker.repositories.categories import CategoryRepository
from app.expense_tracker.schemas import BudgetCreate, BudgetUpdate


class BudgetService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.budgets = BudgetRepository(session)
        self.categories = CategoryRepository(session)

    async def create(self, user_id: int, data: BudgetCreate):
        await self._ensure_category(data.category_id)
        budget = await self.budgets.create(user_id, data)
        await self.session.commit()
        return budget

    async def list(self, user_id: int):
        return await self.budgets.list_for_user(user_id)

    async def get(self, budget_id: int, user_id: int):
        budget = await self.budgets.get_for_user(budget_id, user_id)
        if budget is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
        return budget

    async def update(self, budget_id: int, user_id: int, data: BudgetUpdate):
        budget = await self.get(budget_id, user_id)
        if data.category_id is not None:
            await self._ensure_category(data.category_id)
        budget = await self.budgets.update(budget, data)
        await self.session.commit()
        return budget

    async def delete(self, budget_id: int, user_id: int) -> None:
        budget = await self.get(budget_id, user_id)
        await self.budgets.delete(budget)
        await self.session.commit()

    async def _ensure_category(self, category_id: int) -> None:
        if await self.categories.get(category_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

