from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.config import get_settings
from app.expense_tracker.models import User
from app.expense_tracker.repositories.users import UserRepository
from app.expense_tracker.schemas import Token, UserCreate
from app.expense_tracker.security import create_token, decode_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.settings = get_settings()

    async def register(self, data: UserCreate) -> User:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
        user = await self.users.create(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            avatar_url=data.avatar_url,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(self, email: str, password: str) -> Token:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return self._tokens_for(user)

    async def refresh(self, refresh_token: str) -> Token:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Wrong token type")
            user = await self.users.get_by_id(int(payload["sub"]))
        except (KeyError, TypeError, ValueError):
            user = None
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        return self._tokens_for(user)

    def _tokens_for(self, user: User) -> Token:
        access = create_token(
            str(user.id),
            "access",
            timedelta(minutes=self.settings.access_token_expire_minutes),
        )
        refresh = create_token(
            str(user.id),
            "refresh",
            timedelta(days=self.settings.refresh_token_expire_days),
        )
        return Token(access_token=access, refresh_token=refresh)

