from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.expense_tracker.repositories.accounts import AccountRepository
from app.expense_tracker.repositories.categories import CategoryRepository
from app.expense_tracker.repositories.expenses import ExpenseRepository
from app.expense_tracker.schemas import (
    ExpenseAccountCreate,
    ExpenseAccountUpdate,
    ExpenseCreate,
    ExpenseUpdate,
    SyncConflict,
    SyncPushRequest,
)
from app.expense_tracker.services.expenses import ExpenseService


class SyncService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expenses = ExpenseRepository(session)
        self.accounts = AccountRepository(session)
        self.categories = CategoryRepository(session)
        self.expense_service = ExpenseService(session)

    async def push(self, user_id: int, data: SyncPushRequest) -> dict:
        accepted = {"expenses": [], "accounts": []}
        conflicts: list[SyncConflict] = []

        for item in data.accounts:
            if item.id is None and not item.deleted:
                account = await self.accounts.create(
                    user_id,
                    ExpenseAccountCreate(
                        name=item.name,
                        description=item.description,
                        account_type=item.account_type,
                    ),
                )
                accepted["accounts"].append(account.id)
                continue

            if item.id is None:
                continue
            account = await self.accounts.get_for_user(item.id, user_id)
            if account is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account {item.id} not found")
            if self._is_stale(item.updated_at, account.updated_at):
                conflicts.append(self._conflict("account", item.id, account.id, "server_record_is_newer", account.updated_at))
                continue
            if item.deleted:
                if account.owner_id != user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can delete accounts")
                await self.accounts.delete(account)
            else:
                if account.owner_id != user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can update accounts")
                await self.accounts.update(
                    account,
                    ExpenseAccountUpdate(
                        name=item.name,
                        description=item.description,
                        account_type=item.account_type,
                    ),
                )
            accepted["accounts"].append(item.id)

        for item in data.expenses:
            if item.id is None and not item.deleted:
                expense = await self.expense_service.create(
                    user_id,
                    ExpenseCreate(
                        amount=item.amount,
                        merchant=item.merchant,
                        description=item.description,
                        category_id=item.category_id,
                        expense_date=item.expense_date,
                        payment_method=item.payment_method,
                        account_id=item.account_id,
                    ),
                )
                accepted["expenses"].append(expense.id)
                continue

            if item.id is None:
                continue
            expense = await self.expenses.get_for_user(item.id, user_id)
            if expense is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Expense {item.id} not found")
            if self._is_stale(item.updated_at, expense.updated_at):
                conflicts.append(self._conflict("expense", item.id, expense.id, "server_record_is_newer", expense.updated_at))
                continue
            if item.deleted:
                await self.expense_service.delete(item.id, user_id)
            else:
                await self.expense_service.update(
                    item.id,
                    user_id,
                    ExpenseUpdate(
                        amount=item.amount,
                        merchant=item.merchant,
                        description=item.description,
                        category_id=item.category_id,
                        expense_date=item.expense_date,
                        payment_method=item.payment_method,
                        account_id=item.account_id,
                    ),
                )
            accepted["expenses"].append(item.id)

        await self.session.commit()
        return {"accepted": accepted, "conflicts": conflicts}

    async def pull(self, user_id: int, updated_since: datetime | None):
        expenses = await self.expenses.list_updated_since(user_id, updated_since)
        accounts = await self.accounts.list_updated_since(user_id, updated_since)
        return {"expenses": expenses, "accounts": accounts, "server_time": datetime.now(UTC)}

    def _is_stale(self, client_updated_at: datetime | None, server_updated_at: datetime | None) -> bool:
        if client_updated_at is None or server_updated_at is None:
            return False
        return server_updated_at.replace(tzinfo=client_updated_at.tzinfo) > client_updated_at

    def _conflict(self, entity: str, local_id: int | None, server_id: int, reason: str, server_updated_at: datetime):
        return SyncConflict(
            entity=entity,
            local_id=local_id,
            server_id=server_id,
            reason=reason,
            server_updated_at=server_updated_at,
        )
