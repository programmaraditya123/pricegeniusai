from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import (
    CategoryBreakdownItem,
    MonthlyInsightRead,
    MonthlySummary,
    MemberContributionItem,
    SpendingTrendItem,
    TopMerchantItem,
)
from app.expense_tracker.services.reports import ReportService


router = APIRouter(prefix="/reports", tags=["expense reports"])


@router.get("/monthly-summary", response_model=MonthlySummary)
async def monthly_summary(
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).monthly_summary(current_user.id, month, year)


@router.get("/category-breakdown", response_model=list[CategoryBreakdownItem])
async def category_breakdown(
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).category_breakdown(current_user.id, month, year)


@router.get("/top-merchants", response_model=list[TopMerchantItem])
async def top_merchants(
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    limit: int = Query(default=5, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).top_merchants(current_user.id, month, year, limit)


@router.get("/spending-trend", response_model=list[SpendingTrendItem])
async def spending_trend(
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).spending_trend(current_user.id, year)


@router.get("/accounts/{account_id}/monthly-summary", response_model=MonthlySummary)
async def account_monthly_summary(
    account_id: int,
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).account_monthly_summary(account_id, current_user.id, month, year)


@router.get("/accounts/{account_id}/member-contributions", response_model=list[MemberContributionItem])
async def member_contributions(
    account_id: int,
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).member_contributions(account_id, current_user.id, month, year)


@router.get("/accounts/{account_id}/category-breakdown", response_model=list[CategoryBreakdownItem])
async def account_category_breakdown(
    account_id: int,
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).account_category_breakdown(account_id, current_user.id, month, year)


@router.get("/accounts/{account_id}/top-merchants", response_model=list[TopMerchantItem])
async def account_top_merchants(
    account_id: int,
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    limit: int = Query(default=5, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).account_top_merchants(account_id, current_user.id, month, year, limit)


@router.post("/monthly-insights", response_model=MonthlyInsightRead)
async def generate_monthly_insights(
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.now().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ReportService(session).generate_monthly_insight(current_user.id, month, year)
