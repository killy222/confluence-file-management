"""Exported files API: list files from runs."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.models import ExportedFile, Run
from backend.schemas import ExportedFileResponse, ListFilesResponse

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=ListFilesResponse)
async def list_files(
    run_id: str | None = Query(None, description="Filter by run ID; omit for latest run's files"),
    db: AsyncSession = Depends(get_db),
) -> ListFilesResponse:
    """List exported files, optionally for a specific run or latest run."""
    if run_id:
        run = await db.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        r = select(ExportedFile).where(ExportedFile.run_id == run_id).order_by(ExportedFile.created_at)
    else:
        # Latest run that has exported files (e.g. latest confluence_export)
        sub = select(Run.id).where(Run.script == "confluence_export").order_by(Run.started_at.desc()).limit(1)
        result = await db.execute(sub)
        latest_id = result.scalars().one_or_none()
        if not latest_id:
            return ListFilesResponse(files=[], run_id=None)
        r = select(ExportedFile).where(ExportedFile.run_id == latest_id).order_by(ExportedFile.created_at)
        run_id = latest_id
    result = await db.execute(r)
    files = result.scalars().all()
    return ListFilesResponse(
        files=[ExportedFileResponse.model_validate(f) for f in files],
        run_id=run_id,
    )


@router.get("/by-run/{run_id}", response_model=ListFilesResponse)
async def list_files_by_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> ListFilesResponse:
    """List exported files for a specific run."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    result = await db.execute(
        select(ExportedFile).where(ExportedFile.run_id == run_id).order_by(ExportedFile.created_at)
    )
    files = result.scalars().all()
    return ListFilesResponse(files=[ExportedFileResponse.model_validate(f) for f in files], run_id=run_id)
