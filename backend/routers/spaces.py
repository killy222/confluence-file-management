"""CRUD API for saved Confluence spaces (key + label)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import ConfluenceSpace
from backend.schemas import (
    ConfluenceSpaceCreate,
    ConfluenceSpaceRead,
    ConfluenceSpaceUpdate,
)

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("", response_model=list[ConfluenceSpaceRead])
async def list_spaces(db: AsyncSession = Depends(get_db)) -> list[ConfluenceSpaceRead]:
    result = await db.execute(select(ConfluenceSpace).order_by(ConfluenceSpace.label, ConfluenceSpace.key))
    spaces = result.scalars().all()
    return [ConfluenceSpaceRead.model_validate(s) for s in spaces]


@router.post("", response_model=ConfluenceSpaceRead, status_code=status.HTTP_201_CREATED)
async def create_space(
    body: ConfluenceSpaceCreate,
    db: AsyncSession = Depends(get_db),
) -> ConfluenceSpaceRead:
    # Enforce unique key at application level for friendlier error
    existing = await db.execute(select(ConfluenceSpace).where(ConfluenceSpace.key == body.key))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Space key already exists")
    space = ConfluenceSpace(key=body.key, label=body.label)
    db.add(space)
    await db.commit()
    await db.refresh(space)
    return ConfluenceSpaceRead.model_validate(space)


@router.patch("/{space_id}", response_model=ConfluenceSpaceRead)
async def update_space(
    space_id: str,
    body: ConfluenceSpaceUpdate,
    db: AsyncSession = Depends(get_db),
) -> ConfluenceSpaceRead:
    space = await db.get(ConfluenceSpace, space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    if body.key is not None and body.key != space.key:
        existing = await db.execute(select(ConfluenceSpace).where(ConfluenceSpace.key == body.key))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Space key already exists")
        space.key = body.key
    if body.label is not None:
        space.label = body.label
    await db.commit()
    await db.refresh(space)
    return ConfluenceSpaceRead.model_validate(space)


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    space_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    space = await db.get(ConfluenceSpace, space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    await db.delete(space)
    await db.commit()
    return None

