import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.expense_tracker.database import Base, get_session
from app.expense_tracker.models import Category
from app.expense_tracker.repositories.categories import DEFAULT_CATEGORIES
from main import app


@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        session.add_all([Category(name=name, is_default=True) for name in DEFAULT_CATEGORIES])
        await session.commit()

    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def register_and_login(client: AsyncClient, email: str = "test@example.com") -> dict[str, str]:
    await client.post(
        "/api/v1/expense-tracker/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"},
    )
    response = await client.post(
        "/api/v1/expense-tracker/auth/login",
        json={"email": email, "password": "password123"},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def category_id(client: AsyncClient, headers: dict[str, str], name: str) -> int:
    response = await client.get("/api/v1/expense-tracker/categories", headers=headers)
    response.raise_for_status()
    for category in response.json():
        if category["name"] == name:
            return category["id"]
    raise AssertionError(f"Category {name} not found")

