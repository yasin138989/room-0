#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import os
print('Create a secure administrator account with a protected production script.')
print('Do not use a hardcoded admin password in source control.')
PY
