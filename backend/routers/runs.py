"""Runs API: trigger and list script runs."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import Run
from backend.runner import execute_runs
from backend.schemas import (
    ListRunsResponse,
    RunResponse,
    TriggerRunsRequest,
    TriggerRunsResponse,
)

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=TriggerRunsResponse, status_code=202)
async def trigger_runs(
    body: TriggerRunsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> TriggerRunsResponse:
    """Start one or two scripts (confluence_export, notebooklm_push). Chain = export then push."""
    now = datetime.now(timezone.utc)
    run_ids: list[str] = []
    parent_id: str | None = None
    for script in body.scripts:
        run_id = str(uuid4())
        run = Run(
            id=run_id,
            script=script,
            status="running",
            started_at=now,
            parent_run_id=parent_id,
            created_at=now,
            updated_at=now,
        )
        db.add(run)
        run_ids.append(run_id)
        parent_id = run_id
    await db.commit()
    background_tasks.add_task(execute_runs, run_ids)
    return TriggerRunsResponse(run_ids=run_ids, message="Runs started")


@router.get("", response_model=ListRunsResponse)
async def list_runs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    script: str | None = Query(None, description="Filter by script name"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> ListRunsResponse:
    """List run history with optional filters and pagination."""
    q = select(Run).order_by(Run.started_at.desc())
    count_q = select(func.count()).select_from(Run)
    if script:
        q = q.where(Run.script == script)
        count_q = count_q.where(Run.script == script)
    if status:
        q = q.where(Run.status == status)
        count_q = count_q.where(Run.status == status)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    runs = result.scalars().all()
    return ListRunsResponse(
        runs=[RunResponse.model_validate(r) for r in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    """Get a single run by ID."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse.model_validate(run)
