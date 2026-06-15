from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import RefreshTokenRequest, Token, UserCreate, UserLogin, UserRead
from app.expense_tracker.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["expense auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: AsyncSession = Depends(get_session)):
    return await AuthService(session).register(data)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    return await AuthService(session).login(data.email, data.password)


@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    return await AuthService(session).refresh(data.refresh_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

