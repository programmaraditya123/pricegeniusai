"""add shared expense accounts

Revision ID: 20260615_0002
Revises: 20260615_0001
Create Date: 2026-06-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260615_0002"
down_revision: str | None = "20260615_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expense_tracker_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("account_type", sa.String(length=50), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["expense_tracker_users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_expense_tracker_accounts_account_type", "expense_tracker_accounts", ["account_type"])
    op.create_index("ix_expense_tracker_accounts_owner_id", "expense_tracker_accounts", ["owner_id"])

    op.create_table(
        "expense_tracker_account_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["expense_tracker_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["expense_tracker_users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("account_id", "user_id", name="uq_account_member_user"),
    )
    op.create_index("ix_expense_tracker_account_members_account_id", "expense_tracker_account_members", ["account_id"])
    op.create_index("ix_expense_tracker_account_members_user_id", "expense_tracker_account_members", ["user_id"])
    op.create_index("ix_expense_tracker_account_members_role", "expense_tracker_account_members", ["role"])

    op.create_table(
        "expense_tracker_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("invited_by", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["expense_tracker_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by"], ["expense_tracker_users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("account_id", "email", "status", name="uq_pending_invitation"),
    )
    op.create_index("ix_expense_tracker_invitations_account_id", "expense_tracker_invitations", ["account_id"])
    op.create_index("ix_expense_tracker_invitations_email", "expense_tracker_invitations", ["email"])
    op.create_index("ix_expense_tracker_invitations_invited_by", "expense_tracker_invitations", ["invited_by"])
    op.create_index("ix_expense_tracker_invitations_status", "expense_tracker_invitations", ["status"])

    op.add_column("expense_tracker_expenses", sa.Column("account_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_expense_tracker_expenses_account_id",
        "expense_tracker_expenses",
        "expense_tracker_accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_expense_tracker_expenses_account_id", "expense_tracker_expenses", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_expense_tracker_expenses_account_id", table_name="expense_tracker_expenses")
    op.drop_constraint("fk_expense_tracker_expenses_account_id", "expense_tracker_expenses", type_="foreignkey")
    op.drop_column("expense_tracker_expenses", "account_id")

    op.drop_index("ix_expense_tracker_invitations_status", table_name="expense_tracker_invitations")
    op.drop_index("ix_expense_tracker_invitations_invited_by", table_name="expense_tracker_invitations")
    op.drop_index("ix_expense_tracker_invitations_email", table_name="expense_tracker_invitations")
    op.drop_index("ix_expense_tracker_invitations_account_id", table_name="expense_tracker_invitations")
    op.drop_table("expense_tracker_invitations")

    op.drop_index("ix_expense_tracker_account_members_role", table_name="expense_tracker_account_members")
    op.drop_index("ix_expense_tracker_account_members_user_id", table_name="expense_tracker_account_members")
    op.drop_index("ix_expense_tracker_account_members_account_id", table_name="expense_tracker_account_members")
    op.drop_table("expense_tracker_account_members")

    op.drop_index("ix_expense_tracker_accounts_owner_id", table_name="expense_tracker_accounts")
    op.drop_index("ix_expense_tracker_accounts_account_type", table_name="expense_tracker_accounts")
    op.drop_table("expense_tracker_accounts")
