from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.services.livekit_service import LiveKitTokenError, build_livekit_token, build_room_snapshot

router = APIRouter(prefix='/api/v1/livekit', tags=['livekit'])


@router.get('/status')
def livekit_status() -> dict:
    return {
        'enabled': settings.enable_livekit,
        'url': settings.livekit_url,
        'status': 'configured' if settings.enable_livekit else 'disabled',
        'message': 'LiveKit is active and ready for voice rooms.' if settings.enable_livekit else 'LiveKit is not enabled in this environment.',
    }


@router.post('/token')
def issue_livekit_token(payload: dict) -> dict:
    if not settings.enable_livekit:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='LiveKit is disabled in this environment',
        )

    user_id = payload.get('user_id')
    room_name = payload.get('room_name') or 'room-0-table'
    role = payload.get('role') or 'player'
    if user_id is None:
        raise HTTPException(status_code=400, detail='user_id is required')

    try:
        token = build_livekit_token(
            user_id=int(user_id),
            identity=f'user-{int(user_id)}',
            room_name=str(room_name),
            role=str(role),
            can_publish=role == 'player',
        )
    except LiveKitTokenError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        'token': token,
        'snapshot': build_room_snapshot(int(user_id), is_enabled=True, user_role=str(role)),
        'room_name': str(room_name),
    }
