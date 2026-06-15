from datetime import date
from decimal import Decimal

from sqlalchemy import Select, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.expense_tracker.models import AccountMember, Category, Expense
from app.expense_tracker.schemas import ExpenseCreate, ExpenseUpdate


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, data: ExpenseCreate) -> Expense:
        expense = Expense(user_id=user_id, **data.model_dump())
        self.session.add(expense)
        await self.session.flush()
        await self.session.refresh(expense, attribute_names=["category"])
        return expense

    async def get_for_user(self, expense_id: int, user_id: int) -> Expense | None:
        result = await self.session.execute(
            select(Expense)
            .options(selectinload(Expense.category))
            .where(Expense.id == expense_id, self._visible_to_user(user_id))
        )
        return result.scalar_one_or_none()

    async def get_personal_for_user(self, expense_id: int, user_id: int) -> Expense | None:
        result = await self.session.execute(
            select(Expense)
            .options(selectinload(Expense.category))
            .where(Expense.id == expense_id, Expense.user_id == user_id, Expense.account_id.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: int,
        page: int,
        size: int,
        category: str | None = None,
        merchant: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        amount_min: Decimal | None = None,
        amount_max: Decimal | None = None,
        account_id: int | None = None,
    ) -> tuple[list[Expense], int]:
        stmt = (
            select(Expense)
            .join(Expense.category)
            .options(selectinload(Expense.category))
            .order_by(Expense.expense_date.desc(), Expense.id.desc())
        )
        if account_id is not None:
            stmt = stmt.where(
                Expense.account_id == account_id,
                exists().where(AccountMember.account_id == account_id, AccountMember.user_id == user_id),
            )
        else:
            stmt = stmt.where(self._visible_to_user(user_id))
        stmt = self._apply_filters(stmt, category, merchant, date_from, date_to, amount_min, amount_max)

        total_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = await self.session.scalar(total_stmt)
        result = await self.session.execute(stmt.offset((page - 1) * size).limit(size))
        return list(result.scalars().all()), int(total or 0)

    async def update(self, expense: Expense, data: ExpenseUpdate) -> Expense:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(expense, key, value)
        await self.session.flush()
        await self.session.refresh(expense)
        await self.session.refresh(expense, attribute_names=["category"])
        return expense

    async def delete(self, expense: Expense) -> None:
        await self.session.delete(expense)

    async def list_updated_since(self, user_id: int, updated_since) -> list[Expense]:
        stmt = (
            select(Expense)
            .options(selectinload(Expense.category))
            .where(self._visible_to_user(user_id))
            .order_by(Expense.updated_at.asc(), Expense.id.asc())
        )
        if updated_since is not None:
            stmt = stmt.where(Expense.updated_at > updated_since)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _visible_to_user(self, user_id: int):
        account_membership = exists().where(
            AccountMember.account_id == Expense.account_id,
            AccountMember.user_id == user_id,
        )
        return or_(
            Expense.user_id == user_id,
            Expense.account_id.is_not(None) & account_membership,
        )

    def _apply_filters(
        self,
        stmt: Select[tuple[Expense]],
        category: str | None,
        merchant: str | None,
        date_from: date | None,
        date_to: date | None,
        amount_min: Decimal | None,
        amount_max: Decimal | None,
    ) -> Select[tuple[Expense]]:
        if category:
            stmt = stmt.where(Category.name.ilike(f"%{category}%"))
        if merchant:
            stmt = stmt.where(Expense.merchant.ilike(f"%{merchant}%"))
        if date_from:
            stmt = stmt.where(Expense.expense_date >= date_from)
        if date_to:
            stmt = stmt.where(Expense.expense_date <= date_to)
        if amount_min is not None:
            stmt = stmt.where(Expense.amount >= amount_min)
        if amount_max is not None:
            stmt = stmt.where(Expense.amount <= amount_max)
        return stmt
