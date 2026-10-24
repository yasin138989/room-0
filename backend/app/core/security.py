from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict[str, Any]:
    """Validate Telegram Mini App initData according to Telegram rules."""
    if not init_data or not bot_token:
        raise ValueError('Telegram initData or bot token is missing')

    fields: dict[str, str] = {}
    for item in init_data.split('&'):
        if not item:
            continue
        if '=' not in item:
            continue
        k, v = item.split('=', 1)
        fields[k] = v

    if 'hash' not in fields:
        raise ValueError('hash is missing in initData')

    provided_hash = fields.pop('hash')
    data_check_string = '\n'.join(f'{k}={fields[k]}' for k in sorted(fields.keys()))
    secret_key = hashlib.sha256(bot_token.encode('utf-8')).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, provided_hash):
        raise ValueError('invalid initData signature')

    auth_date = fields.get('auth_date')
    if auth_date is not None:
        try:
            ts = int(auth_date)
        except ValueError as exc:
            raise ValueError('auth_date is not valid') from exc
        if datetime.now(timezone.utc).timestamp() - ts > 86400:
            raise ValueError('initData has expired')

    parsed: dict[str, Any] = {}
    for key, value in fields.items():
        try:
            parsed[key] = json.loads(value)
        except json.JSONDecodeError:
            parsed[key] = value

    return parsed
