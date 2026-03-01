"""Pydantic request/response schemas for the API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# --- Runs ---

SCRIPT_NAMES = ("confluence_export", "notebooklm_push")


class TriggerRunsRequest(BaseModel):
    """Request body for POST /runs."""

    scripts: list[str] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="One or two script names: confluence_export, notebooklm_push. Two = chain (export then push).",
    )

    @field_validator("scripts")
    @classmethod
    def scripts_allowed(cls, v: list[str]) -> list[str]:
        for s in v:
            if s not in SCRIPT_NAMES:
                raise ValueError(f"Invalid script: {s}. Allowed: {list(SCRIPT_NAMES)}")
        if len(v) == 2 and (v[0] != "confluence_export" or v[1] != "notebooklm_push"):
            raise ValueError("Chained run must be [confluence_export, notebooklm_push] in that order")
        return v


class RunResponse(BaseModel):
    """Single run in list or detail."""

    model_config = {"from_attributes": True}

    id: str
    script: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    log_output: str | None
    error_message: str | None
    parent_run_id: str | None
    created_at: datetime
    updated_at: datetime


class TriggerRunsResponse(BaseModel):
    """Response for POST /runs (202 Accepted)."""

    run_ids: list[str] = Field(..., description="IDs of created runs (in execution order)")
    message: str = "Runs started"


class ListRunsResponse(BaseModel):
    """Paginated list of runs."""

    runs: list[RunResponse]
    total: int
    limit: int
    offset: int


# --- Files ---

class ExportedFileResponse(BaseModel):
    """Single exported file."""

    model_config = {"from_attributes": True}

    id: str
    run_id: str
    path: str
    title: str | None
    page_id: str | None
    created_at: datetime


class ListFilesResponse(BaseModel):
    """List of exported files (optionally for a run)."""

    files: list[ExportedFileResponse]
    run_id: str | None = None
