#!/usr/bin/env bash
set -euo pipefail

DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

if command -v pg_dump >/dev/null 2>&1; then
  pg_dump "${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/room0}" > "$BACKUP_DIR/room0-$DATE.sql"
  echo "Backup created: $BACKUP_DIR/room0-$DATE.sql"
else
  echo "pg_dump not found; install PostgreSQL client first."
  exit 1
fi
