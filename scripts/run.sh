#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Starting backend on http://127.0.0.1:8000"
echo "Starting frontend on http://127.0.0.1:5173"

cleanup() {
	if [[ -n "${BACKEND_PID:-}" ]]; then
		kill "${BACKEND_PID}" >/dev/null 2>&1 || true
	fi
}

trap cleanup EXIT INT TERM

cd "${REPO_ROOT}/backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cd "${REPO_ROOT}/frontend"
corepack pnpm dev --host 127.0.0.1 --port 5173