from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import BudgetCreate, BudgetRead, BudgetUpdate
from app.expense_tracker.services.budgets import BudgetService


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await BudgetService(session).create(current_user.id, data)


@router.get("", response_model=list[BudgetRead])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await BudgetService(session).list(current_user.id)


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await BudgetService(session).get(budget_id, current_user.id)


@router.patch("/{budget_id}", response_model=BudgetRead)
async def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await BudgetService(session).update(budget_id, current_user.id, data)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await BudgetService(session).delete(budget_id, current_user.id)

