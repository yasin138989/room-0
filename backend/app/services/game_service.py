from __future__ import annotations

from app.core.security import validate_telegram_init_data


def determine_game_winner(players: list[dict]) -> str | None:
    detectives = [p for p in players if p.get('role_name') == 'detective' and p.get('is_alive', True)]
    spies = [p for p in players if p.get('role_name') == 'spy' and p.get('is_alive', True)]
    others = [p for p in players if p.get('role_name') != 'spy' and p.get('is_alive', True)]

    if not spies and detectives:
        return 'detectives'

    if len(spies) >= len(others):
        return 'spies'

    independent = [p for p in players if p.get('role_name') == 'independent' and p.get('is_alive', True)]
    if independent:
        return 'independent'

    return None


def get_or_create_user_from_init_data(init_data: str, bot_token: str) -> dict:
    payload = validate_telegram_init_data(init_data, bot_token)
    user = payload.get('user', {})
    return {
        'telegram_id': user.get('id'),
        'username': user.get('username'),
        'first_name': user.get('first_name'),
        'last_name': user.get('last_name'),
    }
