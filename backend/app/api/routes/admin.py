from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix='/api/v1/admin', tags=['admin'])


@router.get('/overview')
def admin_overview() -> dict:
    return {
        'users_total': 0,
        'users_online': 0,
        'active_games': 0,
        'tables_reserved': 0,
        'status': 'ok',
    }
