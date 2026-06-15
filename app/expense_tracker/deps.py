from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.models import User
from app.expense_tracker.repositories.users import UserRepository
from app.expense_tracker.security import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/expense-tracker/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise credentials_error

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user

