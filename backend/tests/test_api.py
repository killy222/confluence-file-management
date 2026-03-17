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


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_spaces_crud_and_list(client: AsyncClient):
    """Full CRUD flow for /spaces: create, list, update, delete."""
    # Create
    r = await client.post(
        "/api/v1/spaces",
        json={"key": "PHS", "label": "Phonix Sales"},
    )
    assert r.status_code == 201
    created = r.json()
    assert created["key"] == "PHS"
    assert created["label"] == "Phonix Sales"
    space_id = created["id"]

    # List
    r = await client.get("/api/v1/spaces")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(s["id"] == space_id for s in data)

    # Update
    r = await client.patch(
        f"/api/v1/spaces/{space_id}",
        json={"label": "Phonix Sales (Updated)"},
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["label"] == "Phonix Sales (Updated)"

    # Delete
    r = await client.delete(f"/api/v1/spaces/{space_id}")
    assert r.status_code == 204


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_trigger_runs_with_space_uses_space_key_on_run(client: AsyncClient):
    """POST /runs with space_id stores resolved space_key on Run row."""
    # Create a space to reference
    r = await client.post(
        "/api/v1/spaces",
        json={"key": "PHS", "label": "Phonix Sales"},
    )
    assert r.status_code == 201
    space = r.json()

    # Trigger a confluence_export run with space_id
    r = await client.post(
        "/api/v1/runs",
        json={"scripts": ["confluence_export"], "space_id": space["id"]},
    )
    assert r.status_code == 202
    data = r.json()
    run_id = data["run_ids"][0]

    # Fetch run detail and assert space_key is present
    r = await client.get(f"/api/v1/runs/{run_id}")
    assert r.status_code == 200
    run = r.json()
    assert run.get("script") == "confluence_export"
    assert run.get("status") == "running"
    assert run.get("space_key") == "PHS"


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_notebooks_crud_and_list(client: AsyncClient):
    """Full CRUD flow for /notebooks: create, list, update, delete."""
    # Create
    r = await client.post(
        "/api/v1/notebooks",
        json={"name": "Phonix Sales"},
    )
    assert r.status_code == 201
    created = r.json()
    assert created["name"] == "Phonix Sales"
    notebook_id = created["id"]

    # List
    r = await client.get("/api/v1/notebooks")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(n["id"] == notebook_id for n in data)

    # Update
    r = await client.patch(
        f"/api/v1/notebooks/{notebook_id}",
        json={"name": "Phonix Sales (Updated)"},
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Phonix Sales (Updated)"

    # Delete
    r = await client.delete(f"/api/v1/notebooks/{notebook_id}")
    assert r.status_code == 204


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required")
async def test_trigger_runs_with_notebook_uses_notebook_name_on_run(client: AsyncClient):
    """POST /runs with notebook_id stores resolved notebook_name on Run row."""
    # Create a notebook target
    r = await client.post(
        "/api/v1/notebooks",
        json={"name": "Phonix Sales"},
    )
    assert r.status_code == 201
    nb = r.json()

    # Trigger a notebooklm_push run with notebook_id
    r = await client.post(
        "/api/v1/runs",
        json={"scripts": ["notebooklm_push"], "notebook_id": nb["id"]},
    )
    assert r.status_code == 202
    data = r.json()
    run_id = data["run_ids"][0]

    # Fetch run detail and assert notebook_name is present
    r = await client.get(f"/api/v1/runs/{run_id}")
    assert r.status_code == 200
    run = r.json()
    assert run.get("script") == "notebooklm_push"
    assert run.get("status") == "running"
    assert run.get("notebook_name") == "Phonix Sales"
