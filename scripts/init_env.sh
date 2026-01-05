#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

ensure_venv() {
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
}

ensure_python_deps() {
  local requirements="$root_dir/ami/requirements.txt"
  if command -v uv >/dev/null 2>&1; then
    uv pip install -r "$requirements" --python "$root_dir/.venv/bin/python"
    return
  fi
  pip install -r "$requirements"
}

ensure_node_deps() {
  cd "$root_dir/web"
  if [ ! -d "node_modules" ]; then
    npm install
    return
  fi
  if ! npm list --depth=0 >/dev/null 2>&1; then
    npm install
  fi
}

ensure_venv
ensure_python_deps
ensure_node_deps

echo "Init complete."
