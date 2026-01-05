#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

./scripts/sync_ui_config.sh

if command -v lsof >/dev/null 2>&1; then
  existing_pid="$(lsof -ti tcp:2024 2>/dev/null || true)"
  if [ -n "$existing_pid" ]; then
    echo "Port 2024 in use by PID $existing_pid, stopping it..."
    kill "$existing_pid"
  fi

  existing_ui_pid="$(lsof -ti tcp:3000 2>/dev/null || true)"
  if [ -n "$existing_ui_pid" ]; then
    echo "Port 3000 in use by PID $existing_ui_pid, stopping it..."
    kill "$existing_ui_pid"
  fi
fi

cd "$root_dir/ami"
langgraph dev --no-browser &
langgraph_pid=$!

cleanup() {
  if kill -0 "$langgraph_pid" 2>/dev/null; then
    kill "$langgraph_pid"
  fi
}
trap cleanup EXIT

cd "$root_dir/web"
npm run dev
