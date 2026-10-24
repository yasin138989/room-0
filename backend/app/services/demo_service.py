from __future__ import annotations

from pathlib import Path


def ensure_demo_seed() -> str:
    root = Path(__file__).resolve().parents[2]
    seed_file = root / 'docs' / 'seed_manifest.txt'
    seed_file.parent.mkdir(parents=True, exist_ok=True)
    seed_file.write_text('demo seed ready\n', encoding='utf-8')
    return str(seed_file)


def create_backup() -> str:
    import hashlib
    import os

    digest = hashlib.sha256(str(os.times()).encode('utf-8')).hexdigest()[:12]
    return f'backup_{digest}.sql'
