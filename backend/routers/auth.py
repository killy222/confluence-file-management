"""Authentication-related API endpoints."""

import json
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from backend.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/notebooklm", status_code=status.HTTP_200_OK)
async def upload_notebooklm_auth(file: UploadFile) -> dict:
    """
    Upload NotebookLM auth storage file (storage_state.json).

    The uploaded file content is stored as storage_state.json under the
    NotebookLM home directory so that notebooklm-py can use it via from_storage().
    """
    # Basic content-type guard; allow JSON and plain text.
    if file.content_type not in {"application/json", "text/plain", "application/octet-stream", ""}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type for auth file.",
        )

    # Read with a simple size guard (~256KB)
    max_bytes = 256 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth file too large.",
        )

    text = data.decode("utf-8", errors="strict")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON in auth file: {exc.msg}",
        ) from exc

    # Optional very light structural check: must be a dict.
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth file JSON must be an object.",
        )

    home = Path(settings.get_notebooklm_home())
    home.mkdir(parents=True, exist_ok=True)
    storage_path = home / "storage_state.json"

    # Write atomically to avoid partial writes.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=home) as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, storage_path)

    return {"ok": True}

