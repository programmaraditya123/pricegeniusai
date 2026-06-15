from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import Expense, ExpenseAccount, User


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def metrics(self) -> dict:
        since = datetime.now(UTC) - timedelta(days=30)
        users_count = await self.session.scalar(select(func.count(User.id)))
        expenses_count = await self.session.scalar(select(func.count(Expense.id)))
        active_accounts = await self.session.scalar(select(func.count(ExpenseAccount.id)))
        user_growth = await self.session.scalar(select(func.count(User.id)).where(User.created_at >= since))
        expense_growth = await self.session.scalar(select(func.count(Expense.id)).where(Expense.created_at >= since))
        return {
            "users_count": int(users_count or 0),
            "expenses_count": int(expenses_count or 0),
            "active_accounts": int(active_accounts or 0),
            "user_growth_30d": int(user_growth or 0),
            "expense_growth_30d": int(expense_growth or 0),
        }
