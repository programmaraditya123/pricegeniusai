import pytest

from tests.conftest import category_id, register_and_login


pytestmark = pytest.mark.asyncio


async def test_expense_crud_and_filters(async_client):
    headers = await register_and_login(async_client, "expenses@example.com")
    shopping_id = await category_id(async_client, headers, "Shopping")

    create = await async_client.post(
        "/api/v1/expense-tracker/expenses",
        headers=headers,
        json={
            "amount": "500.00",
            "merchant": "Vishal Mega Mart",
            "description": "Groceries",
            "category_id": shopping_id,
            "expense_date": "2026-06-15",
            "payment_method": "UPI",
        },
    )
    assert create.status_code == 201
    expense = create.json()
    assert expense["merchant"] == "Vishal Mega Mart"

    list_response = await async_client.get(
        "/api/v1/expense-tracker/expenses?merchant=Vishal&amount_min=100&amount_max=600&page=1&size=10",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update = await async_client.patch(
        f"/api/v1/expense-tracker/expenses/{expense['id']}",
        headers=headers,
        json={"amount": "650.00", "description": "Monthly shopping"},
    )
    assert update.status_code == 200
    assert update.json()["description"] == "Monthly shopping"

    get_response = await async_client.get(f"/api/v1/expense-tracker/expenses/{expense['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == expense["id"]

    delete = await async_client.delete(f"/api/v1/expense-tracker/expenses/{expense['id']}", headers=headers)
    assert delete.status_code == 204

    missing = await async_client.get(f"/api/v1/expense-tracker/expenses/{expense['id']}", headers=headers)
    assert missing.status_code == 404


async def test_parse_expense_uses_regex_and_smart_category(async_client):
    headers = await register_and_login(async_client, "parse@example.com")
    response = await async_client.post(
        "/api/v1/expense-tracker/ai/parse-expense",
        headers=headers,
        json={"text": "Today at Vishal Mega Mart total kharcha is 500"},
    )
    assert response.status_code == 200
    assert response.json() == {"amount": "500", "merchant": "Vishal Mega Mart", "category": "Shopping"}

