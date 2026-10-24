from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix='/api/v1', tags=['auth'])


@router.get('/auth/health')
def auth_health() -> dict[str, str]:
    return {'status': 'ok', 'module': 'auth'}
