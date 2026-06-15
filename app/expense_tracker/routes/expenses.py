from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate, PaginatedExpenses
from app.expense_tracker.services.expenses import ExpenseService


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ExpenseService(session).create(current_user.id, data)


@router.get("", response_model=PaginatedExpenses)
async def list_expenses(
    category: str | None = None,
    merchant: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    amount_min: Decimal | None = None,
    amount_max: Decimal | None = None,
    account_id: int | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    items, total = await ExpenseService(session).list(
        current_user.id,
        page=page,
        size=size,
        category=category,
        merchant=merchant,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
        account_id=account_id,
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ExpenseService(session).get(expense_id, current_user.id)


@router.patch("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await ExpenseService(session).update(expense_id, current_user.id, data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ExpenseService(session).delete(expense_id, current_user.id)
