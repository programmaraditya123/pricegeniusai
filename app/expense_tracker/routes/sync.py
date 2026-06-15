from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import SyncPullResponse, SyncPushRequest, SyncPushResponse
from app.expense_tracker.services.sync import SyncService


router = APIRouter(prefix="/sync", tags=["expense sync"])


@router.post("/push", response_model=SyncPushResponse)
async def push_sync(
    data: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await SyncService(session).push(current_user.id, data)


@router.post("/pull", response_model=SyncPullResponse)
async def pull_sync(
    updated_since: datetime | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await SyncService(session).pull(current_user.id, updated_since)
