"""API endpoint tests. Require PostgreSQL (DATABASE_URL). Runner is mocked."""

import os

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required for DB tests")
async def test_health(client: AsyncClient):
    """GET /api/v1/health returns 200 and status ok when DB is up."""
    r = await client.get("/api/v1/health")
    assert r.status_code in (200, 503)
    data = r.json()
    assert "status" in data
    if r.status_code == 200:
        assert data["status"] == "ok"
        assert data.get("database") == "connected"


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_trigger_runs_validation(client: AsyncClient):
    """POST /api/v1/runs with invalid scripts returns 400."""
    r = await client.post("/api/v1/runs", json={"scripts": ["invalid_script"]})
    assert r.status_code == 422  # Pydantic validation error


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_trigger_runs_single(client: AsyncClient):
    """POST /api/v1/runs with confluence_export returns 202 and run_ids."""
    r = await client.post("/api/v1/runs", json={"scripts": ["confluence_export"]})
    assert r.status_code == 202
    data = r.json()
    assert "run_ids" in data
    assert len(data["run_ids"]) == 1
    assert data["message"] == "Runs started"


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_trigger_runs_chain(client: AsyncClient):
    """POST /api/v1/runs with both scripts returns 202 and two run_ids."""
    r = await client.post(
        "/api/v1/runs",
        json={"scripts": ["confluence_export", "notebooklm_push"]},
    )
    assert r.status_code == 202
    data = r.json()
    assert len(data["run_ids"]) == 2


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_list_runs(client: AsyncClient):
    """GET /api/v1/runs returns 200 and runs array."""
    r = await client.get("/api/v1/runs")
    assert r.status_code == 200
    data = r.json()
    assert "runs" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["runs"], list)


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_get_run_404(client: AsyncClient):
    """GET /api/v1/runs/non-existent returns 404."""
    r = await client.get("/api/v1/runs/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_list_files(client: AsyncClient):
    """GET /api/v1/files returns 200 and files array."""
    r = await client.get("/api/v1/files")
    assert r.status_code == 200
    data = r.json()
    assert "files" in data
    assert isinstance(data["files"], list)
