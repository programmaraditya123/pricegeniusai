from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.expense_tracker.models import AccountMember, ExpenseAccount, Invitation, User
from app.expense_tracker.schemas import ExpenseAccountCreate, ExpenseAccountUpdate


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_id: int, data: ExpenseAccountCreate) -> ExpenseAccount:
        account = ExpenseAccount(owner_id=owner_id, **data.model_dump())
        self.session.add(account)
        await self.session.flush()
        self.session.add(AccountMember(account_id=account.id, user_id=owner_id, role="OWNER"))
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def list_for_user(self, user_id: int) -> list[ExpenseAccount]:
        result = await self.session.execute(
            select(ExpenseAccount)
            .join(AccountMember, AccountMember.account_id == ExpenseAccount.id)
            .where(AccountMember.user_id == user_id)
            .order_by(ExpenseAccount.created_at.desc(), ExpenseAccount.id.desc())
        )
        return list(result.scalars().unique().all())

    async def get_for_user(self, account_id: int, user_id: int) -> ExpenseAccount | None:
        result = await self.session.execute(
            select(ExpenseAccount)
            .join(AccountMember, AccountMember.account_id == ExpenseAccount.id)
            .where(ExpenseAccount.id == account_id, AccountMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_member(self, account_id: int, user_id: int) -> AccountMember | None:
        result = await self.session.execute(
            select(AccountMember).where(AccountMember.account_id == account_id, AccountMember.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_members(self, account_id: int) -> list[AccountMember]:
        result = await self.session.execute(
            select(AccountMember)
            .options(selectinload(AccountMember.user))
            .where(AccountMember.account_id == account_id)
            .order_by(AccountMember.role, AccountMember.joined_at)
        )
        return list(result.scalars().all())

    async def update(self, account: ExpenseAccount, data: ExpenseAccountUpdate) -> ExpenseAccount:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(account, key, value)
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def delete(self, account: ExpenseAccount) -> None:
        await self.session.delete(account)

    async def create_invitation(self, account_id: int, email: str, invited_by: int) -> Invitation:
        invitation = Invitation(account_id=account_id, email=email.lower(), invited_by=invited_by, status="PENDING")
        self.session.add(invitation)
        await self.session.flush()
        return invitation

    async def list_pending_invitations_for_email(self, email: str) -> list[Invitation]:
        result = await self.session.execute(
            select(Invitation)
            .options(selectinload(Invitation.account))
            .where(Invitation.email == email.lower(), Invitation.status == "PENDING")
            .order_by(Invitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_invitation_for_user(self, invitation_id: int, email: str) -> Invitation | None:
        result = await self.session.execute(
            select(Invitation).where(Invitation.id == invitation_id, Invitation.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def add_member(self, account_id: int, user_id: int, role: str = "MEMBER") -> AccountMember:
        member = AccountMember(account_id=account_id, user_id=user_id, role=role)
        self.session.add(member)
        await self.session.flush()
        return member

    async def update_member_role(self, member: AccountMember, role: str) -> AccountMember:
        member.role = role
        await self.session.flush()
        await self.session.refresh(member, attribute_names=["user"])
        return member

    async def remove_member(self, member: AccountMember) -> None:
        await self.session.delete(member)

    async def list_updated_since(self, user_id: int, updated_since) -> list[ExpenseAccount]:
        stmt = (
            select(ExpenseAccount)
            .join(AccountMember, AccountMember.account_id == ExpenseAccount.id)
            .where(AccountMember.user_id == user_id)
            .order_by(ExpenseAccount.updated_at.asc(), ExpenseAccount.id.asc())
        )
        if updated_since is not None:
            stmt = stmt.where(ExpenseAccount.updated_at > updated_since)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def find_users_by_account_or_owner(self, account_id: int) -> list[User]:
        result = await self.session.execute(
            select(User)
            .join(AccountMember, AccountMember.user_id == User.id)
            .where(AccountMember.account_id == account_id)
            .order_by(User.email)
        )
        return list(result.scalars().all())
