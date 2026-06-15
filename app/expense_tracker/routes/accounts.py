from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.database import get_session
from app.expense_tracker.deps import get_current_user
from app.expense_tracker.models import User
from app.expense_tracker.schemas import (
    AccountMemberRead,
    ExpenseAccountCreate,
    ExpenseAccountRead,
    ExpenseAccountUpdate,
    InvitationRead,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
)
from app.expense_tracker.services.accounts import AccountService


router = APIRouter(prefix="/accounts", tags=["expense accounts"])


@router.post("", response_model=ExpenseAccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: ExpenseAccountCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).create(current_user.id, data)


@router.get("", response_model=list[ExpenseAccountRead])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).list(current_user.id)


@router.get("/{account_id}", response_model=ExpenseAccountRead)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).get(account_id, current_user.id)


@router.patch("/{account_id}", response_model=ExpenseAccountRead)
async def update_account(
    account_id: int,
    data: ExpenseAccountUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).update(account_id, current_user.id, data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await AccountService(session).delete(account_id, current_user.id)


@router.post("/{account_id}/invitations", response_model=InvitationRead, status_code=status.HTTP_201_CREATED)
async def invite_member(
    account_id: int,
    data: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).invite(account_id, current_user.id, data.email)


@router.get("/invitations/me", response_model=list[InvitationRead])
async def list_my_invitations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).list_my_invites(current_user)


@router.post("/invitations/{invitation_id}/accept", response_model=InvitationRead)
async def accept_invite(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).accept_invite(invitation_id, current_user)


@router.post("/invitations/{invitation_id}/reject", response_model=InvitationRead)
async def reject_invite(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).reject_invite(invitation_id, current_user)


@router.get("/{account_id}/members", response_model=list[AccountMemberRead])
async def list_members(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).list_members(account_id, current_user.id)


@router.patch("/{account_id}/members/{member_id}", response_model=AccountMemberRead)
async def update_member_role(
    account_id: int,
    member_id: int,
    data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await AccountService(session).update_member_role(account_id, member_id, current_user.id, data.role)


@router.delete("/{account_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    account_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await AccountService(session).remove_member(account_id, member_id, current_user.id)

