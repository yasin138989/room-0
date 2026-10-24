from __future__ import annotations

from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.params import Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import validate_telegram_init_data
from app.db.models import User
from app.db.session import get_db


async def get_authenticated_user(
    x_telegram_init_data: str | None = Header(default=None, alias='X-Telegram-Init-Data'),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail='Telegram initData is missing')

    try:
        payload = validate_telegram_init_data(x_telegram_init_data, settings.telegram_bot_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user_data = payload.get('user')
    if not isinstance(user_data, dict):
        raise HTTPException(status_code=401, detail='Telegram user payload is missing')

    telegram_id = user_data.get('id')
    if not telegram_id:
        raise HTTPException(status_code=401, detail='Telegram user id is missing')

    result = await db.execute(select(User).where(User.telegram_id == int(telegram_id)))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=int(telegram_id),
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user.last_seen_at = datetime.utcnow()
    await db.commit()
    return user
