#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

ui_name="${UI_NAME:-agent-chat-ui}"
if [ -f "${repo_root}/web/package.json" ]; then
  ui_dir="${repo_root}/web"
else
  ui_dir="${repo_root}/web/${ui_name}"
fi
venv_path="${VENV_PATH:-${repo_root}/.venv}"

if [ ! -d "$ui_dir" ]; then
  echo "UI directory not found: $ui_dir" >&2
  echo "Run ./scripts/setup_ui.sh first." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if [ ! -d "$venv_path" ]; then
  uv venv "$venv_path"
fi

need_install=false
if [ ! -x "${venv_path}/bin/langgraph" ]; then
  need_install=true
else
  if ! "${venv_path}/bin/python" - <<'PY' >/dev/null 2>&1; then
import importlib
import sys

try:
    importlib.import_module("langgraph_api")
except Exception:
    sys.exit(1)
PY
    need_install=true
  fi
fi

if [ "$need_install" = true ]; then
  uv pip install -r "${repo_root}/ami/requirements.txt" --python "${venv_path}/bin/python"
fi

"${repo_root}/scripts/sync_ui_config.sh"

(
  cd "${repo_root}/ami"
  "${venv_path}/bin/langgraph" dev
) &
langgraph_pid=$!

cleanup() {
  if kill -0 "$langgraph_pid" 2>/dev/null; then
    kill "$langgraph_pid"
  fi
}
trap cleanup EXIT

(
  cd "$ui_dir"
  npm install
  npm dev
)

wait "$langgraph_pid"
