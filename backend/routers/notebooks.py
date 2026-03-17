"""CRUD API for NotebookLM notebook targets (name only)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import NotebookTarget
from backend.schemas import (
    NotebookTargetCreate,
    NotebookTargetRead,
    NotebookTargetUpdate,
)

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookTargetRead])
async def list_notebooks(
    db: AsyncSession = Depends(get_db),
) -> list[NotebookTargetRead]:
    result = await db.execute(select(NotebookTarget).order_by(NotebookTarget.name))
    notebooks = result.scalars().all()
    return [NotebookTargetRead.model_validate(n) for n in notebooks]


@router.post("", response_model=NotebookTargetRead, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    body: NotebookTargetCreate,
    db: AsyncSession = Depends(get_db),
) -> NotebookTargetRead:
    existing = await db.execute(select(NotebookTarget).where(NotebookTarget.name == body.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Notebook name already exists")
    nb = NotebookTarget(name=body.name)
    db.add(nb)
    await db.commit()
    await db.refresh(nb)
    return NotebookTargetRead.model_validate(nb)


@router.patch("/{notebook_id}", response_model=NotebookTargetRead)
async def update_notebook(
    notebook_id: str,
    body: NotebookTargetUpdate,
    db: AsyncSession = Depends(get_db),
) -> NotebookTargetRead:
    nb = await db.get(NotebookTarget, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    if body.name is not None and body.name != nb.name:
        existing = await db.execute(select(NotebookTarget).where(NotebookTarget.name == body.name))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Notebook name already exists")
        nb.name = body.name
    await db.commit()
    await db.refresh(nb)
    return NotebookTargetRead.model_validate(nb)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    nb = await db.get(NotebookTarget, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.delete(nb)
    await db.commit()
    return None

"""CRUD API for saved NotebookLM notebook targets."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import NotebookTarget
from backend.schemas import (
    NotebookTargetCreate,
    NotebookTargetRead,
    NotebookTargetUpdate,
)

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookTargetRead])
async def list_notebooks(db: AsyncSession = Depends(get_db)) -> list[NotebookTargetRead]:
    result = await db.execute(select(NotebookTarget).order_by(NotebookTarget.name))
    notebooks = result.scalars().all()
    return [NotebookTargetRead.model_validate(n) for n in notebooks]


@router.post("", response_model=NotebookTargetRead, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    body: NotebookTargetCreate,
    db: AsyncSession = Depends(get_db),
) -> NotebookTargetRead:
    notebook = NotebookTarget(name=body.name)
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return NotebookTargetRead.model_validate(notebook)


@router.patch("/{notebook_id}", response_model=NotebookTargetRead)
async def update_notebook(
    notebook_id: str,
    body: NotebookTargetUpdate,
    db: AsyncSession = Depends(get_db),
) -> NotebookTargetRead:
    notebook = await db.get(NotebookTarget, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    if body.name is not None:
        notebook.name = body.name
    await db.commit()
    await db.refresh(notebook)
    return NotebookTargetRead.model_validate(notebook)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    notebook = await db.get(NotebookTarget, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.delete(notebook)
    await db.commit()
    return None

