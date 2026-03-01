"""Pytest fixtures for backend API tests. Uses real DB with rollback; mocks runner."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import engine, get_db
from backend.main import app


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a session that rolls back after the request (so tests don't persist)."""
    async with engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False, autocommit=False, autoflush=False)
        try:
            yield session
            await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
        await conn.rollback()


@pytest_asyncio.fixture
async def client():
    """Async HTTP client with get_db override (rollback) and mocked execute_runs."""
    app.dependency_overrides[get_db] = override_get_db
    with patch("backend.routers.runs.execute_runs", new_callable=AsyncMock):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac
    app.dependency_overrides.clear()
