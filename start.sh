#!/usr/bin/env bash
# Convenience launcher: starts backend (8000) and frontend (5173) in parallel.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

(cd "$ROOT/backend" && uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

(cd "$ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
