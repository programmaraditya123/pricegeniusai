from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import CategoryRead
from app.expense_tracker.services.categories import CategoryService


router = APIRouter(prefix="/categories", tags=["expense categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await CategoryService(session).list()

