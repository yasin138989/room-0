from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
import json


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    if not init_data:
        raise ValueError('init_data is required')

    payload: dict[str, str] = {}
    for item in init_data.split('&'):
        if not item:
            continue
        if '=' not in item:
            continue
        key, value = item.split('=', 1)
        payload[key] = value

    if 'hash' not in payload:
        raise ValueError('hash is missing from init_data')

    provided_hash = payload.pop('hash')
    data_check_string = '\n'.join(f'{key}={payload[key]}' for key in sorted(payload.keys()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    generated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(generated_hash, provided_hash):
        raise ValueError('invalid init_data signature')

    auth_date = payload.get('auth_date')
    if auth_date is not None:
        try:
            timestamp = int(auth_date)
        except ValueError as exc:
            raise ValueError('auth_date is invalid') from exc
        if datetime.now(timezone.utc).timestamp() - timestamp > 86400:
            raise ValueError('init_data expired')

    parsed: dict = {}
    for key, value in payload.items():
        if key == 'user':
            parsed[key] = json.loads(value)
        else:
            try:
                parsed[key] = json.loads(value)
            except json.JSONDecodeError:
                parsed[key] = value
    return parsed
