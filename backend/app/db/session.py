from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(
    settings.database_url.replace('postgresql+psycopg', 'postgresql+asyncpg'),
    echo=False,
    future=True,
)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


@lru_cache
def get_db() -> object:
    return async_session
