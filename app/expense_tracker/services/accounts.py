from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.models import AccountMember, ExpenseAccount, Invitation, User
from app.expense_tracker.permissions import ADMIN, MEMBER, OWNER, AccountPermissionService
from app.expense_tracker.repositories.accounts import AccountRepository
from app.expense_tracker.schemas import ExpenseAccountCreate, ExpenseAccountUpdate


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.accounts = AccountRepository(session)
        self.permissions = AccountPermissionService(session)

    async def create(self, user_id: int, data: ExpenseAccountCreate) -> ExpenseAccount:
        account = await self.accounts.create(user_id, data)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def list(self, user_id: int) -> list[ExpenseAccount]:
        return await self.accounts.list_for_user(user_id)

    async def get(self, account_id: int, user_id: int) -> ExpenseAccount:
        account = await self.accounts.get_for_user(account_id, user_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return account

    async def update(self, account_id: int, user_id: int, data: ExpenseAccountUpdate) -> ExpenseAccount:
        await self.permissions.require_account_manager(account_id, user_id)
        account = await self.get(account_id, user_id)
        account = await self.accounts.update(account, data)
        await self.session.commit()
        return account

    async def delete(self, account_id: int, user_id: int) -> None:
        await self.permissions.require_account_manager(account_id, user_id)
        account = await self.get(account_id, user_id)
        await self.accounts.delete(account)
        await self.session.commit()

    async def invite(self, account_id: int, user_id: int, email: str) -> Invitation:
        await self.permissions.require_inviter(account_id, user_id)
        try:
            invitation = await self.accounts.create_invitation(account_id, email, user_id)
            await self.session.commit()
            await self.session.refresh(invitation)
            return invitation
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation already exists") from exc

    async def list_my_invites(self, user: User) -> list[Invitation]:
        return await self.accounts.list_pending_invitations_for_email(user.email)

    async def accept_invite(self, invitation_id: int, user: User) -> Invitation:
        invitation = await self._get_pending_invitation(invitation_id, user.email)
        try:
            await self.accounts.add_member(invitation.account_id, user.id, MEMBER)
            invitation.status = "ACCEPTED"
            await self.session.commit()
            await self.session.refresh(invitation)
            return invitation
        except IntegrityError as exc:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member") from exc

    async def reject_invite(self, invitation_id: int, user: User) -> Invitation:
        invitation = await self._get_pending_invitation(invitation_id, user.email)
        invitation.status = "REJECTED"
        await self.session.commit()
        await self.session.refresh(invitation)
        return invitation

    async def list_members(self, account_id: int, user_id: int) -> list[AccountMember]:
        await self.permissions.require_member(account_id, user_id)
        return await self.accounts.list_members(account_id)

    async def update_member_role(self, account_id: int, member_id: int, user_id: int, role: str) -> AccountMember:
        await self.permissions.require_account_manager(account_id, user_id)
        members = await self.accounts.list_members(account_id)
        member = self._find_member(members, member_id)
        if member.role == OWNER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be changed")
        member = await self.accounts.update_member_role(member, role)
        await self.session.commit()
        return member

    async def remove_member(self, account_id: int, member_id: int, user_id: int) -> None:
        await self.permissions.require_account_manager(account_id, user_id)
        members = await self.accounts.list_members(account_id)
        member = self._find_member(members, member_id)
        if member.role == OWNER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner cannot be removed")
        await self.accounts.remove_member(member)
        await self.session.commit()

    async def _get_pending_invitation(self, invitation_id: int, email: str) -> Invitation:
        invitation = await self.accounts.get_invitation_for_user(invitation_id, email)
        if invitation is None or invitation.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        return invitation

    def _find_member(self, members: list[AccountMember], member_id: int) -> AccountMember:
        for member in members:
            if member.id == member_id:
                return member
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
