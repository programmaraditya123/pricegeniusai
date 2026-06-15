from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import AccountMember
from app.expense_tracker.repositories.accounts import AccountRepository


OWNER = "OWNER"
ADMIN = "ADMIN"
MEMBER = "MEMBER"


class AccountPermissionService:
    def __init__(self, session: AsyncSession):
        self.accounts = AccountRepository(session)

    async def require_member(self, account_id: int, user_id: int) -> AccountMember:
        member = await self.accounts.get_member(account_id, user_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account access denied")
        return member

    async def require_account_manager(self, account_id: int, user_id: int) -> AccountMember:
        member = await self.require_member(account_id, user_id)
        if member.role != OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can manage this account")
        return member

    async def require_inviter(self, account_id: int, user_id: int) -> AccountMember:
        member = await self.require_member(account_id, user_id)
        if member.role not in {OWNER, ADMIN}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and admins can invite members")
        return member

    async def require_expense_creator(self, account_id: int, user_id: int) -> AccountMember:
        return await self.require_member(account_id, user_id)

    async def require_expense_editor(self, account_id: int, user_id: int) -> AccountMember:
        member = await self.require_member(account_id, user_id)
        if member.role not in {OWNER, ADMIN}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and admins can edit expenses")
        return member

