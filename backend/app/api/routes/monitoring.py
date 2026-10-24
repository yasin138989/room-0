from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix='/api/v1', tags=['monitoring'])
start_time = monotonic()


@router.get('/metrics')
async def get_metrics() -> dict[str, float | int | str]:
    return {
        'uptime_seconds': round(monotonic() - start_time, 2),
        'environment': settings.environment,
        'app_name': settings.app_name,
        'status': 'ok',
    }


@router.get('/ready')
async def ready_check() -> dict[str, str]:
    return {'status': 'ready', 'service': settings.app_name}
