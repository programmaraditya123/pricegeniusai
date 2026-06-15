"""create expense tracker tables

Revision ID: 20260615_0001
Revises:
Create Date: 2026-06-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260615_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expense_tracker_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_expense_tracker_users_email", "expense_tracker_users", ["email"], unique=True)

    op.create_table(
        "expense_tracker_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_expense_tracker_categories_name", "expense_tracker_categories", ["name"], unique=True)

    op.create_table(
        "expense_tracker_expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("merchant", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["expense_tracker_categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["expense_tracker_users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_expense_tracker_expenses_user_id", "expense_tracker_expenses", ["user_id"])
    op.create_index("ix_expense_tracker_expenses_category_id", "expense_tracker_expenses", ["category_id"])
    op.create_index("ix_expense_tracker_expenses_expense_date", "expense_tracker_expenses", ["expense_date"])
    op.create_index("ix_expense_tracker_expenses_merchant", "expense_tracker_expenses", ["merchant"])

    op.create_table(
        "expense_tracker_budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("monthly_limit", sa.Numeric(12, 2), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["expense_tracker_categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["expense_tracker_users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_period"),
    )
    op.create_index("ix_expense_tracker_budgets_user_id", "expense_tracker_budgets", ["user_id"])
    op.create_index("ix_expense_tracker_budgets_category_id", "expense_tracker_budgets", ["category_id"])

    op.create_table(
        "expense_tracker_monthly_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("total_spending", sa.Numeric(12, 2), nullable=False),
        sa.Column("top_category", sa.String(length=100), nullable=True),
        sa.Column("top_merchant", sa.String(length=255), nullable=True),
        sa.Column("spending_growth", sa.Numeric(8, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["expense_tracker_users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "month", "year", name="uq_monthly_insight_period"),
    )
    op.create_index("ix_expense_tracker_monthly_insights_user_id", "expense_tracker_monthly_insights", ["user_id"])

    categories = [
        {"name": "Food", "is_default": True},
        {"name": "Shopping", "is_default": True},
        {"name": "Travel", "is_default": True},
        {"name": "Health", "is_default": True},
        {"name": "Education", "is_default": True},
        {"name": "Bills", "is_default": True},
        {"name": "Entertainment", "is_default": True},
        {"name": "Rent", "is_default": True},
    ]
    op.bulk_insert(sa.table("expense_tracker_categories", sa.column("name"), sa.column("is_default")), categories)


def downgrade() -> None:
    op.drop_index("ix_expense_tracker_monthly_insights_user_id", table_name="expense_tracker_monthly_insights")
    op.drop_table("expense_tracker_monthly_insights")
    op.drop_index("ix_expense_tracker_budgets_category_id", table_name="expense_tracker_budgets")
    op.drop_index("ix_expense_tracker_budgets_user_id", table_name="expense_tracker_budgets")
    op.drop_table("expense_tracker_budgets")
    op.drop_index("ix_expense_tracker_expenses_merchant", table_name="expense_tracker_expenses")
    op.drop_index("ix_expense_tracker_expenses_expense_date", table_name="expense_tracker_expenses")
    op.drop_index("ix_expense_tracker_expenses_category_id", table_name="expense_tracker_expenses")
    op.drop_index("ix_expense_tracker_expenses_user_id", table_name="expense_tracker_expenses")
    op.drop_table("expense_tracker_expenses")
    op.drop_index("ix_expense_tracker_categories_name", table_name="expense_tracker_categories")
    op.drop_table("expense_tracker_categories")
    op.drop_index("ix_expense_tracker_users_email", table_name="expense_tracker_users")
    op.drop_table("expense_tracker_users")
