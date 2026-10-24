from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base


def _build_database_url() -> str:
    url = settings.database_url
    if url.startswith('postgresql+psycopg'):
        return url.replace('postgresql+psycopg', 'postgresql+asyncpg', 1)
    return url


engine = create_async_engine(_build_database_url(), echo=False, future=True)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
