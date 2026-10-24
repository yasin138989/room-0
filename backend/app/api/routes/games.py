from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix='/api/v1', tags=['games'])


@router.get('/games/health')
def games_health() -> dict[str, str]:
    return {'status': 'ok', 'module': 'games'}
