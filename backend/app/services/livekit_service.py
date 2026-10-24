from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings


class LiveKitTokenError(Exception):
    pass


def build_livekit_token(
    *,
    user_id: int,
    identity: str,
    room_name: str,
    role: str,
    can_publish: bool,
    can_subscribe: bool = True,
    ttl_seconds: int = 300,
) -> str:
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise LiveKitTokenError('LiveKit is not configured')

    now = datetime.utcnow()
    claims: dict[str, Any] = {
        'iss': settings.livekit_api_key,
        'sub': str(user_id),
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        'jti': f'{identity}-{room_name}-{int(now.timestamp())}',
        'video': True,
        'audio': True,
        'room': room_name,
        'identity': identity,
        'can_publish': can_publish,
        'can_subscribe': can_subscribe,
        'can_publish_data': False,
        'can_publish_sources': ['microphone'] if can_publish else [],
    }

    if role == 'spectator':
        claims['can_publish'] = False
        claims['audio'] = False
        claims['video'] = False
        claims['can_publish_sources'] = []

    return jwt.encode(claims, settings.livekit_api_secret, algorithm='HS256')


def build_room_snapshot(table_id: int, *, is_enabled: bool, user_role: str) -> dict[str, Any]:
    return {
        'table_id': table_id,
        'voice_enabled': is_enabled,
        'role': user_role,
        'livekit_url': settings.livekit_url,
        'timestamp': datetime.utcnow().isoformat(),
    }
