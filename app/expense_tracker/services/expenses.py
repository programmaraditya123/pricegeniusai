from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.categories import CategoryRepository
from app.expense_tracker.repositories.expenses import ExpenseRepository
from app.expense_tracker.permissions import AccountPermissionService
from app.expense_tracker.schemas import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expenses = ExpenseRepository(session)
        self.categories = CategoryRepository(session)
        self.permissions = AccountPermissionService(session)

    async def create(self, user_id: int, data: ExpenseCreate):
        await self._ensure_category(data.category_id)
        if data.account_id is not None:
            await self.permissions.require_expense_creator(data.account_id, user_id)
        expense = await self.expenses.create(user_id, data)
        await self.session.commit()
        return expense

    async def get(self, expense_id: int, user_id: int):
        expense = await self.expenses.get_for_user(expense_id, user_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return expense

    async def list(self, user_id: int, **filters):
        return await self.expenses.list_for_user(user_id=user_id, **filters)

    async def update(self, expense_id: int, user_id: int, data: ExpenseUpdate):
        expense = await self.get(expense_id, user_id)
        if expense.account_id is not None:
            await self.permissions.require_expense_editor(expense.account_id, user_id)
        if data.category_id is not None:
            await self._ensure_category(data.category_id)
        if data.account_id is not None and data.account_id != expense.account_id:
            await self.permissions.require_expense_creator(data.account_id, user_id)
        expense = await self.expenses.update(expense, data)
        await self.session.commit()
        return expense

    async def delete(self, expense_id: int, user_id: int) -> None:
        expense = await self.get(expense_id, user_id)
        if expense.account_id is not None:
            await self.permissions.require_expense_editor(expense.account_id, user_id)
        await self.expenses.delete(expense)
        await self.session.commit()

    async def _ensure_category(self, category_id: int) -> None:
        if await self.categories.get(category_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
