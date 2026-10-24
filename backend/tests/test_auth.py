from __future__ import annotations

import hashlib
import hmac

from app.core.security import validate_telegram_init_data


def build_init_data(bot_token: str) -> str:
    payload = {
        'auth_date': '1730000000',
        'query_id': 'abc',
        'user': '{"id":42,"first_name":"Ali","last_name":"Sadeghi","username":"ali"}'
    }
    secret = hashlib.sha256(bot_token.encode()).digest()
    data = '\n'.join(f'{key}={payload[key]}' for key in sorted(payload.keys()))
    signature = hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()
    return '&'.join([f'{key}={payload[key]}' for key in sorted(payload.keys())] + [f'hash={signature}'])


def test_valid_init_data() -> None:
    init_data = build_init_data('token123')
    result = validate_telegram_init_data(init_data, 'token123')
    assert result['user']['id'] == 42


def test_invalid_signature() -> None:
    try:
        validate_telegram_init_data('hash=bad', 'token123')
        assert False
    except ValueError:
        pass
