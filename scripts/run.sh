#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Starting backend on http://127.0.0.1:8000"
echo "Frontend bootstrap is pending Fase 2."

cd "${REPO_ROOT}/backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000