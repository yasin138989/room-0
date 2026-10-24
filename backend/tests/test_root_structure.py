from __future__ import annotations

from pathlib import Path


def test_root_structure() -> None:
    root = Path(__file__).resolve().parents[2]
    for item in ['backend', 'frontend', 'docs', 'scripts', 'deploy']:
        assert (root / item).exists()
