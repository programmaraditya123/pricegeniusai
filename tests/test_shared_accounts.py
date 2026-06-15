import pytest

from tests.conftest import category_id, register_and_login


pytestmark = pytest.mark.asyncio


async def test_family_account_invites_permissions_and_reports(async_client):
    father_headers = await register_and_login(async_client, "father@example.com")
    mother_headers = await register_and_login(async_client, "mother@example.com")
    food_id = await category_id(async_client, father_headers, "Food")
    health_id = await category_id(async_client, father_headers, "Health")

    account_response = await async_client.post(
        "/api/v1/expense-tracker/accounts",
        headers=father_headers,
        json={"name": "Family", "description": "Household spending", "account_type": "FAMILY"},
    )
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    invite = await async_client.post(
        f"/api/v1/expense-tracker/accounts/{account_id}/invitations",
        headers=father_headers,
        json={"email": "mother@example.com"},
    )
    assert invite.status_code == 201

    accepted = await async_client.post(
        f"/api/v1/expense-tracker/accounts/invitations/{invite.json()['id']}/accept",
        headers=mother_headers,
    )
    assert accepted.status_code == 200

    members = await async_client.get(f"/api/v1/expense-tracker/accounts/{account_id}/members", headers=father_headers)
    assert members.status_code == 200
    mother_member = next(member for member in members.json() if member["user"]["email"] == "mother@example.com")

    father_expense = await async_client.post(
        "/api/v1/expense-tracker/expenses",
        headers=father_headers,
        json={
            "account_id": account_id,
            "amount": "500.00",
            "merchant": "Grocery Store",
            "category_id": food_id,
            "expense_date": "2026-06-15",
        },
    )
    assert father_expense.status_code == 201

    mother_expense = await async_client.post(
        "/api/v1/expense-tracker/expenses",
        headers=mother_headers,
        json={
            "account_id": account_id,
            "amount": "200.00",
            "merchant": "Apollo Pharmacy",
            "category_id": health_id,
            "expense_date": "2026-06-15",
        },
    )
    assert mother_expense.status_code == 201

    forbidden_update = await async_client.patch(
        f"/api/v1/expense-tracker/expenses/{father_expense.json()['id']}",
        headers=mother_headers,
        json={"amount": "550.00"},
    )
    assert forbidden_update.status_code == 403

    role_update = await async_client.patch(
        f"/api/v1/expense-tracker/accounts/{account_id}/members/{mother_member['id']}",
        headers=father_headers,
        json={"role": "ADMIN"},
    )
    assert role_update.status_code == 200

    allowed_update = await async_client.patch(
        f"/api/v1/expense-tracker/expenses/{father_expense.json()['id']}",
        headers=mother_headers,
        json={"amount": "550.00"},
    )
    assert allowed_update.status_code == 200

    summary = await async_client.get(
        f"/api/v1/expense-tracker/reports/accounts/{account_id}/monthly-summary?month=6&year=2026",
        headers=mother_headers,
    )
    assert summary.status_code == 200
    assert summary.json()["total_spending"] == "750.00"

    contributions = await async_client.get(
        f"/api/v1/expense-tracker/reports/accounts/{account_id}/member-contributions?month=6&year=2026",
        headers=father_headers,
    )
    assert contributions.status_code == 200
    assert {item["email"] for item in contributions.json()} == {"father@example.com", "mother@example.com"}


async def test_sync_pull_and_push_create_account(async_client):
    headers = await register_and_login(async_client, "sync-user@example.com")
    food_id = await category_id(async_client, headers, "Food")

    push = await async_client.post(
        "/api/v1/expense-tracker/sync/push",
        headers=headers,
        json={
            "accounts": [{"name": "Mobile Family", "description": None, "account_type": "FAMILY"}],
            "expenses": [
                {
                    "amount": "99.00",
                    "merchant": "Dominos",
                    "description": None,
                    "category_id": food_id,
                    "expense_date": "2026-06-15",
                    "payment_method": "UPI",
                    "account_id": None,
                }
            ],
        },
    )
    assert push.status_code == 200
    assert len(push.json()["accepted"]["accounts"]) == 1
    assert len(push.json()["accepted"]["expenses"]) == 1

    pull = await async_client.post("/api/v1/expense-tracker/sync/pull", headers=headers)
    assert pull.status_code == 200
    assert pull.json()["accounts"][0]["name"] == "Mobile Family"
    assert pull.json()["expenses"][0]["merchant"] == "Dominos"
