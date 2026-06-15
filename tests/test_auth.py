import pytest


pytestmark = pytest.mark.asyncio


async def test_register_login_refresh_and_me(async_client):
    register = await async_client.post(
        "/api/v1/expense-tracker/auth/register",
        json={"email": "auth@example.com", "password": "password123", "full_name": "Auth User"},
    )
    assert register.status_code == 201
    assert register.json()["email"] == "auth@example.com"

    login = await async_client.post(
        "/api/v1/expense-tracker/auth/login",
        json={"email": "auth@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = await async_client.get(
        "/api/v1/expense-tracker/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["full_name"] == "Auth User"

    refresh = await async_client.post(
        "/api/v1/expense-tracker/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


async def test_login_rejects_bad_password(async_client):
    await async_client.post(
        "/api/v1/expense-tracker/auth/register",
        json={"email": "bad-password@example.com", "password": "password123"},
    )
    response = await async_client.post(
        "/api/v1/expense-tracker/auth/login",
        json={"email": "bad-password@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401

