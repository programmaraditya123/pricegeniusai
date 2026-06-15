from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.expense_tracker.models import Budget
from app.expense_tracker.schemas import BudgetCreate, BudgetUpdate


class BudgetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, data: BudgetCreate) -> Budget:
        budget = Budget(user_id=user_id, **data.model_dump())
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget, attribute_names=["category"])
        return budget

    async def list_for_user(self, user_id: int) -> list[Budget]:
        result = await self.session.execute(
            select(Budget)
            .options(selectinload(Budget.category))
            .where(Budget.user_id == user_id)
            .order_by(Budget.year.desc(), Budget.month.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, budget_id: int, user_id: int) -> Budget | None:
        result = await self.session.execute(
            select(Budget)
            .options(selectinload(Budget.category))
            .where(Budget.id == budget_id, Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, budget: Budget, data: BudgetUpdate) -> Budget:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(budget, key, value)
        await self.session.flush()
        await self.session.refresh(budget)
        await self.session.refresh(budget, attribute_names=["category"])
        return budget

    async def delete(self, budget: Budget) -> None:
        await self.session.delete(budget)
