from __future__ import annotations

from app.services.game_service import determine_game_winner


def test_detective_victory() -> None:
    players = [
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'spy', 'is_alive': False},
        {'role_name': 'spy', 'is_alive': False},
        {'role_name': 'independent', 'is_alive': True},
    ]
    assert determine_game_winner(players) == 'detectives'


def test_spy_majority() -> None:
    players = [
        {'role_name': 'spy', 'is_alive': True},
        {'role_name': 'spy', 'is_alive': True},
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'detective', 'is_alive': True},
        {'role_name': 'independent', 'is_alive': True},
    ]
    assert determine_game_winner(players) == 'spies'
