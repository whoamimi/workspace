#!/usr/bin/env bash
# Load all variables from .env into the current shell

# Uncomment the following line to activate the virtual environment:
# source .venv/bin/activate

if [ -f ".env" ]; then
  # -a / allexport: automatically export all variables defined
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  echo ".env file not found in $(pwd)" >&2
  return 1 2>/dev/null || exit 1
fi

# makes all scripts in this directory executable
set -euo pipefail

for f in ./scripts/*.sh; do
  [[ -f "$f" ]] || continue
  chmod +x "$f"
done