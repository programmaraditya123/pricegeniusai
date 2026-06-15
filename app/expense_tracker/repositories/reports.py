from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import Category, Expense, MonthlyInsight, User


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def monthly_summary(self, user_id: int, month: int, year: int) -> dict:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
                func.coalesce(func.avg(Expense.amount), 0),
            ).where(Expense.user_id == user_id, Expense.expense_date.between(start, end))
        )
        total, count, average = result.one()
        return {"month": month, "year": year, "total_spending": total, "transaction_count": count, "average_expense": average}

    async def account_monthly_summary(self, account_id: int, month: int, year: int) -> dict:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
                func.coalesce(func.avg(Expense.amount), 0),
            ).where(Expense.account_id == account_id, Expense.expense_date.between(start, end))
        )
        total, count, average = result.one()
        return {"month": month, "year": year, "total_spending": total, "transaction_count": count, "average_expense": average}

    async def category_breakdown(self, user_id: int, month: int, year: int) -> list[dict]:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(Category.name, func.sum(Expense.amount), func.count(Expense.id))
            .join(Category, Category.id == Expense.category_id)
            .where(Expense.user_id == user_id, Expense.expense_date.between(start, end))
            .group_by(Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )
        return [{"category": name, "total": total, "transaction_count": count} for name, total, count in result.all()]

    async def account_category_breakdown(self, account_id: int, month: int, year: int) -> list[dict]:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(Category.name, func.sum(Expense.amount), func.count(Expense.id))
            .join(Category, Category.id == Expense.category_id)
            .where(Expense.account_id == account_id, Expense.expense_date.between(start, end))
            .group_by(Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )
        return [{"category": name, "total": total, "transaction_count": count} for name, total, count in result.all()]

    async def top_merchants(self, user_id: int, month: int, year: int, limit: int) -> list[dict]:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(Expense.merchant, func.sum(Expense.amount), func.count(Expense.id))
            .where(Expense.user_id == user_id, Expense.expense_date.between(start, end))
            .group_by(Expense.merchant)
            .order_by(func.sum(Expense.amount).desc())
            .limit(limit)
        )
        return [{"merchant": merchant, "total": total, "transaction_count": count} for merchant, total, count in result.all()]

    async def account_top_merchants(self, account_id: int, month: int, year: int, limit: int) -> list[dict]:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(Expense.merchant, func.sum(Expense.amount), func.count(Expense.id))
            .where(Expense.account_id == account_id, Expense.expense_date.between(start, end))
            .group_by(Expense.merchant)
            .order_by(func.sum(Expense.amount).desc())
            .limit(limit)
        )
        return [{"merchant": merchant, "total": total, "transaction_count": count} for merchant, total, count in result.all()]

    async def member_contributions(self, account_id: int, month: int, year: int) -> list[dict]:
        start, end = self._month_range(month, year)
        result = await self.session.execute(
            select(User.id, User.email, User.full_name, func.coalesce(func.sum(Expense.amount), 0), func.count(Expense.id))
            .join(Expense, Expense.user_id == User.id)
            .where(Expense.account_id == account_id, Expense.expense_date.between(start, end))
            .group_by(User.id, User.email, User.full_name)
            .order_by(func.sum(Expense.amount).desc())
        )
        return [
            {"user_id": user_id, "email": email, "full_name": full_name, "total": total, "transaction_count": count}
            for user_id, email, full_name, total, count in result.all()
        ]

    async def spending_trend(self, user_id: int, year: int) -> list[dict]:
        month_expr = func.date_trunc("month", Expense.expense_date)
        result = await self.session.execute(
            select(month_expr.label("period"), func.sum(Expense.amount))
            .where(Expense.user_id == user_id, extract("year", Expense.expense_date) == year)
            .group_by(month_expr)
            .order_by(month_expr)
        )
        return [{"period": period.date(), "total": total} for period, total in result.all()]

    async def upsert_monthly_insight(
        self,
        *,
        user_id: int,
        month: int,
        year: int,
        total_spending: Decimal,
        top_category: str | None,
        top_merchant: str | None,
        spending_growth: Decimal,
    ) -> MonthlyInsight:
        result = await self.session.execute(
            select(MonthlyInsight).where(
                MonthlyInsight.user_id == user_id,
                MonthlyInsight.month == month,
                MonthlyInsight.year == year,
            )
        )
        insight = result.scalar_one_or_none()
        if insight is None:
            insight = MonthlyInsight(user_id=user_id, month=month, year=year)
            self.session.add(insight)
        insight.total_spending = total_spending
        insight.top_category = top_category
        insight.top_merchant = top_merchant
        insight.spending_growth = spending_growth
        await self.session.flush()
        return insight

    def _month_range(self, month: int, year: int) -> tuple[date, date]:
        return date(year, month, 1), date(year, month, monthrange(year, month)[1])
