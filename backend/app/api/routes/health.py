from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import validate_telegram_init_data
from app.db.models import User

router = APIRouter(prefix='/api/v1', tags=['auth'])


@router.post('/auth/telegram/verify')
async def verify_telegram_auth(payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    init_data = payload.get('initData') or payload.get('init_data')
    if not init_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='initData is required')

    try:
        parsed = validate_telegram_init_data(init_data, settings.telegram_bot_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_data = parsed.get('user')
    if not isinstance(user_data, dict):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Telegram user payload is invalid')

    telegram_id = user_data.get('id')
    if telegram_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Telegram user id is missing')

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

    return {
        'ok': True,
        'user': {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    }
