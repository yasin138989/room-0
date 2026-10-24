from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=['health'])


@router.get('/api/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok', 'service': 'ROOM 0'}


@router.get('/api/v1/overview')
async def overview() -> dict[str, str | bool]:
    return {
        'app_name': 'ROOM 0',
        'environment': 'development',
        'livekit_enabled': False,
        'demo_mode': True,
    }
