#!/usr/bin/env bash
set -euo pipefail

BACKUP_PATH="${1:-./backups/latest.sql}"
if command -v psql >/dev/null 2>&1; then
  psql "${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/room0}" < "$BACKUP_PATH"
  echo "Database restored from $BACKUP_PATH"
else
  echo "psql not found; install PostgreSQL client first."
  exit 1
fi
