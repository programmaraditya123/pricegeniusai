from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.reports import ReportRepository
from app.expense_tracker.permissions import AccountPermissionService


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reports = ReportRepository(session)
        self.permissions = AccountPermissionService(session)

    async def monthly_summary(self, user_id: int, month: int, year: int):
        return await self.reports.monthly_summary(user_id, month, year)

    async def category_breakdown(self, user_id: int, month: int, year: int):
        return await self.reports.category_breakdown(user_id, month, year)

    async def top_merchants(self, user_id: int, month: int, year: int, limit: int):
        return await self.reports.top_merchants(user_id, month, year, limit)

    async def spending_trend(self, user_id: int, year: int):
        return await self.reports.spending_trend(user_id, year)

    async def account_monthly_summary(self, account_id: int, user_id: int, month: int, year: int):
        await self.permissions.require_member(account_id, user_id)
        return await self.reports.account_monthly_summary(account_id, month, year)

    async def account_category_breakdown(self, account_id: int, user_id: int, month: int, year: int):
        await self.permissions.require_member(account_id, user_id)
        return await self.reports.account_category_breakdown(account_id, month, year)

    async def account_top_merchants(self, account_id: int, user_id: int, month: int, year: int, limit: int):
        await self.permissions.require_member(account_id, user_id)
        return await self.reports.account_top_merchants(account_id, month, year, limit)

    async def member_contributions(self, account_id: int, user_id: int, month: int, year: int):
        await self.permissions.require_member(account_id, user_id)
        return await self.reports.member_contributions(account_id, month, year)

    async def generate_monthly_insight(self, user_id: int, month: int, year: int):
        current = await self.reports.monthly_summary(user_id, month, year)
        categories = await self.reports.category_breakdown(user_id, month, year)
        merchants = await self.reports.top_merchants(user_id, month, year, 1)

        previous_month = 12 if month == 1 else month - 1
        previous_year = year - 1 if month == 1 else year
        previous = await self.reports.monthly_summary(user_id, previous_month, previous_year)

        current_total = Decimal(current["total_spending"])
        previous_total = Decimal(previous["total_spending"])
        growth = Decimal("0")
        if previous_total > 0:
            growth = ((current_total - previous_total) / previous_total * Decimal("100")).quantize(Decimal("0.01"))

        insight = await self.reports.upsert_monthly_insight(
            user_id=user_id,
            month=month,
            year=year,
            total_spending=current_total,
            top_category=categories[0]["category"] if categories else None,
            top_merchant=merchants[0]["merchant"] if merchants else None,
            spending_growth=growth,
        )
        await self.session.commit()
        await self.session.refresh(insight)
        return insight
