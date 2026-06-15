from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.expense_tracker.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "expense_tracker_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    expenses: Mapped[list["Expense"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    insights: Mapped[list["MonthlyInsight"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    owned_accounts: Mapped[list["ExpenseAccount"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    account_memberships: Mapped[list["AccountMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", cascade="all, delete-orphan")


class Category(TimestampMixin, Base):
    __tablename__ = "expense_tracker_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="category")


class ExpenseAccount(TimestampMixin, Base):
    __tablename__ = "expense_tracker_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    account_type: Mapped[str] = mapped_column(String(50), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)

    owner: Mapped[User] = relationship(back_populates="owned_accounts")
    members: Mapped[list["AccountMember"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="account")


class AccountMember(Base):
    __tablename__ = "expense_tracker_account_members"
    __table_args__ = (UniqueConstraint("account_id", "user_id", name="uq_account_member_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_accounts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(50), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped[ExpenseAccount] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="account_memberships")


class Invitation(TimestampMixin, Base):
    __tablename__ = "expense_tracker_invitations"
    __table_args__ = (UniqueConstraint("account_id", "email", "status", name="uq_pending_invitation"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_accounts.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    invited_by: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", server_default="PENDING", index=True)

    account: Mapped[ExpenseAccount] = relationship(back_populates="invitations")


class Expense(TimestampMixin, Base):
    __tablename__ = "expense_tracker_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_tracker_accounts.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    merchant: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_categories.id"), index=True)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    payment_method: Mapped[str | None] = mapped_column(String(100))

    user: Mapped[User] = relationship(back_populates="expenses")
    account: Mapped[ExpenseAccount | None] = relationship(back_populates="expenses")
    category: Mapped[Category] = relationship(back_populates="expenses")


class Budget(TimestampMixin, Base):
    __tablename__ = "expense_tracker_budgets"
    __table_args__ = (UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_categories.id"), index=True)
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="budgets")
    category: Mapped[Category] = relationship(back_populates="budgets")


class MonthlyInsight(TimestampMixin, Base):
    __tablename__ = "expense_tracker_monthly_insights"
    __table_args__ = (UniqueConstraint("user_id", "month", "year", name="uq_monthly_insight_period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    total_spending: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    top_category: Mapped[str | None] = mapped_column(String(100))
    top_merchant: Mapped[str | None] = mapped_column(String(255))
    spending_growth: Mapped[Decimal] = mapped_column(Numeric(8, 2))

    user: Mapped[User] = relationship(back_populates="insights")


class Notification(Base):
    __tablename__ = "expense_tracker_notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50), index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user: Mapped[User] = relationship(back_populates="notifications")


class UserSettings(TimestampMixin, Base):
    __tablename__ = "expense_tracker_user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), unique=True, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", server_default="INR")
    timezone: Mapped[str] = mapped_column(String(100), default="Asia/Kolkata", server_default="Asia/Kolkata")
    language: Mapped[str] = mapped_column(String(20), default="en", server_default="en")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    user: Mapped[User] = relationship(back_populates="settings")


class AuditLog(Base):
    __tablename__ = "expense_tracker_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource: Mapped[str] = mapped_column(String(255), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class PasswordResetToken(Base):
    __tablename__ = "expense_tracker_password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("expense_tracker_users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
