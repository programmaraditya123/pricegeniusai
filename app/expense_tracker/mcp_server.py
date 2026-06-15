from datetime import date, datetime
from decimal import Decimal
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.expense_tracker.database import AsyncSessionLocal
from app.expense_tracker.repositories.accounts import AccountRepository
from app.expense_tracker.repositories.budgets import BudgetRepository
from app.expense_tracker.repositories.expenses import ExpenseRepository
from app.expense_tracker.schemas import ExpenseCreate, ExpenseUpdate
from app.expense_tracker.security import decode_token
from app.expense_tracker.services.expenses import ExpenseService
from app.expense_tracker.services.reports import ReportService


mcp = FastMCP("PriceGenius Expense Tracker")


def _user_id_from_token(token: str) -> int:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("MCP tools require an access token")
    return int(payload["sub"])


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def _expense_to_dict(expense) -> dict[str, Any]:
    return _json_safe(
        {
            "id": expense.id,
            "user_id": expense.user_id,
            "account_id": expense.account_id,
            "amount": expense.amount,
            "merchant": expense.merchant,
            "description": expense.description,
            "category_id": expense.category_id,
            "category": expense.category.name if expense.category else None,
            "expense_date": expense.expense_date,
            "payment_method": expense.payment_method,
            "created_at": expense.created_at,
            "updated_at": expense.updated_at,
        }
    )


@mcp.tool()
async def get_expenses(token: str, account_id: int | None = None, page: int = 1, size: int = 20) -> dict[str, Any]:
    """Return paginated expenses visible to the authenticated user."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        items, total = await ExpenseRepository(session).list_for_user(
            user_id=user_id,
            account_id=account_id,
            page=page,
            size=size,
        )
        return {"items": [_expense_to_dict(item) for item in items], "total": total, "page": page, "size": size}


@mcp.tool()
async def create_expense(
    token: str,
    amount: float,
    merchant: str,
    category_id: int,
    expense_date: str,
    description: str | None = None,
    payment_method: str | None = None,
    account_id: int | None = None,
) -> dict[str, Any]:
    """Create a personal or account expense."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        expense = await ExpenseService(session).create(
            user_id,
            ExpenseCreate(
                amount=Decimal(str(amount)),
                merchant=merchant,
                description=description,
                category_id=category_id,
                expense_date=date.fromisoformat(expense_date),
                payment_method=payment_method,
                account_id=account_id,
            ),
        )
        return _expense_to_dict(expense)


@mcp.tool()
async def update_expense(token: str, expense_id: int, updates: dict[str, Any]) -> dict[str, Any]:
    """Update an expense. Shared expenses require OWNER or ADMIN role."""
    user_id = _user_id_from_token(token)
    payload = updates.copy()
    if "amount" in payload and payload["amount"] is not None:
        payload["amount"] = Decimal(str(payload["amount"]))
    if "expense_date" in payload and payload["expense_date"] is not None:
        payload["expense_date"] = date.fromisoformat(payload["expense_date"])
    async with AsyncSessionLocal() as session:
        expense = await ExpenseService(session).update(expense_id, user_id, ExpenseUpdate(**payload))
        return _expense_to_dict(expense)


@mcp.tool()
async def delete_expense(token: str, expense_id: int) -> dict[str, Any]:
    """Delete an expense. Shared expenses require OWNER or ADMIN role."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        await ExpenseService(session).delete(expense_id, user_id)
        return {"deleted": True, "expense_id": expense_id}


@mcp.tool()
async def search_expenses(
    token: str,
    query: str,
    account_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> dict[str, Any]:
    """Search visible expenses by merchant/category text."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        items, total = await ExpenseRepository(session).list_for_user(
            user_id=user_id,
            account_id=account_id,
            merchant=query,
            page=page,
            size=size,
        )
        return {"items": [_expense_to_dict(item) for item in items], "total": total, "page": page, "size": size}


@mcp.tool()
async def get_monthly_summary(token: str, month: int, year: int, account_id: int | None = None) -> dict[str, Any]:
    """Return personal or shared-account monthly spending summary."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        reports = ReportService(session)
        if account_id is None:
            return _json_safe(await reports.monthly_summary(user_id, month, year))
        return _json_safe(await reports.account_monthly_summary(account_id, user_id, month, year))


@mcp.tool()
async def get_budget_status(token: str) -> list[dict[str, Any]]:
    """Return budgets for the authenticated user."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        budgets = await BudgetRepository(session).list_for_user(user_id)
        return _json_safe(
            [
                {
                    "id": budget.id,
                    "category": budget.category.name if budget.category else None,
                    "monthly_limit": budget.monthly_limit,
                    "month": budget.month,
                    "year": budget.year,
                }
                for budget in budgets
            ]
        )


@mcp.tool()
async def get_account_summary(token: str, account_id: int, month: int, year: int) -> dict[str, Any]:
    """Return account totals, category breakdown, top merchants, and member contributions."""
    user_id = _user_id_from_token(token)
    async with AsyncSessionLocal() as session:
        reports = ReportService(session)
        return _json_safe(
            {
                "summary": await reports.account_monthly_summary(account_id, user_id, month, year),
                "category_breakdown": await reports.account_category_breakdown(account_id, user_id, month, year),
                "top_merchants": await reports.account_top_merchants(account_id, user_id, month, year, 5),
                "member_contributions": await reports.member_contributions(account_id, user_id, month, year),
            }
        )


@mcp.resource("expense://recent")
async def recent_expenses() -> str:
    return "Use get_expenses(token, page=1, size=10) to fetch recent visible expenses."


@mcp.resource("expense://budgets")
async def budgets_resource() -> str:
    return "Use get_budget_status(token) to fetch authenticated user budgets."


@mcp.resource("expense://accounts")
async def accounts_resource() -> str:
    return "Use the FastAPI accounts endpoints or get_account_summary(token, account_id, month, year)."


@mcp.resource("expense://summary/current-month")
async def current_month_summary_resource() -> str:
    now = datetime.now()
    return f"Use get_monthly_summary(token, month={now.month}, year={now.year}) for the current month."


if __name__ == "__main__":
    mcp.run()
