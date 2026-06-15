import pytest

from tests.conftest import category_id, register_and_login


pytestmark = pytest.mark.asyncio


async def test_monthly_reports_and_insights(async_client):
    headers = await register_and_login(async_client, "reports@example.com")
    food_id = await category_id(async_client, headers, "Food")
    shopping_id = await category_id(async_client, headers, "Shopping")

    for payload in [
        {
            "amount": "300.00",
            "merchant": "Dominos",
            "category_id": food_id,
            "expense_date": "2026-06-01",
            "payment_method": "Card",
        },
        {
            "amount": "700.00",
            "merchant": "Amazon",
            "category_id": shopping_id,
            "expense_date": "2026-06-02",
            "payment_method": "UPI",
        },
        {
            "amount": "500.00",
            "merchant": "Amazon",
            "category_id": shopping_id,
            "expense_date": "2026-06-03",
            "payment_method": "UPI",
        },
    ]:
        response = await async_client.post("/api/v1/expense-tracker/expenses", headers=headers, json=payload)
        assert response.status_code == 201

    summary = await async_client.get(
        "/api/v1/expense-tracker/reports/monthly-summary?month=6&year=2026",
        headers=headers,
    )
    assert summary.status_code == 200
    assert summary.json()["transaction_count"] == 3
    assert summary.json()["total_spending"] == "1500.00"

    breakdown = await async_client.get(
        "/api/v1/expense-tracker/reports/category-breakdown?month=6&year=2026",
        headers=headers,
    )
    assert breakdown.status_code == 200
    assert breakdown.json()[0]["category"] == "Shopping"

    merchants = await async_client.get(
        "/api/v1/expense-tracker/reports/top-merchants?month=6&year=2026&limit=2",
        headers=headers,
    )
    assert merchants.status_code == 200
    assert merchants.json()[0]["merchant"] == "Amazon"

    insight = await async_client.post(
        "/api/v1/expense-tracker/reports/monthly-insights?month=6&year=2026",
        headers=headers,
    )
    assert insight.status_code == 200
    assert insight.json()["top_category"] == "Shopping"
    assert insight.json()["top_merchant"] == "Amazon"
