"""Async database engine and session."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.models import Base

engine = create_async_engine(
    settings.database_url,
    echo=False,
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create tables if not present (for development). Prefer migrations in production.
    Ignores duplicate table/index errors so startup works after migrations."""
    import sqlalchemy.exc
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except sqlalchemy.exc.ProgrammingError as e:
        if "already exists" not in (str(e) + str(getattr(e, "orig", ""))):
            raise
        # Schema exists (e.g. from migrations); continue
