"""Tests for NotebookLM auth upload endpoint."""

import json
import os

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required for API tests")
async def test_upload_notebooklm_auth_writes_storage_file(tmp_path, client: AsyncClient, monkeypatch):
    """POST /api/v1/auth/notebooklm stores storage_state.json in notebooklm_home."""
    tmp_home = tmp_path / ".notebooklm"
    monkeypatch.setenv("NOTEBOOKLM_HOME", str(tmp_home))

    payload = {"cookies": [], "origins": []}
    data = json.dumps(payload).encode("utf-8")

    files = {"file": ("storage_state.json", data, "application/json")}
    resp = await client.post("/api/v1/auth/notebooklm", files=files)

    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is True

    storage_path = tmp_home / "storage_state.json"
    assert storage_path.is_file()
    written = json.loads(storage_path.read_text(encoding="utf-8"))
    assert written == payload


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL required for API tests")
async def test_upload_notebooklm_auth_rejects_invalid_json(client: AsyncClient):
    """Invalid JSON body returns 400."""
    files = {"file": ("storage_state.json", b"{not-json}", "application/json")}

    resp = await client.post("/api/v1/auth/notebooklm", files=files)

    assert resp.status_code == 400
    body = resp.json()
    assert "detail" in body

