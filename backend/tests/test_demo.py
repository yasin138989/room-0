from __future__ import annotations

from app.services.demo_service import create_backup


def test_backup_name_generation() -> None:
    assert create_backup().startswith('backup_')
