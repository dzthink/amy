#!/usr/bin/env bash
set -euo pipefail

ui_name="${UI_NAME:-agent-chat-ui}"
if [ -f "web/package.json" ]; then
  ui_dir="web"
else
  ui_dir="web/${ui_name}"
fi
langgraph_config="ami/langgraph.json"

if [ ! -d "$ui_dir" ]; then
  echo "UI directory not found: $ui_dir" >&2
  echo "Run ./scripts/setup_ui.sh first." >&2
  exit 1
fi

if [ ! -f "$langgraph_config" ]; then
  echo "LangGraph config not found: $langgraph_config" >&2
  exit 1
fi

assistant_id="$(python3 - <<'PY'
import json
with open("ami/langgraph.json", "r", encoding="utf-8") as f:
    data = json.load(f)
graphs = data.get("graphs", {})
print(next(iter(graphs.keys()), "ami"))
PY
)"

base_url="${LANGGRAPH_BASE_URL:-http://127.0.0.1:2024}"

cat > "${ui_dir}/.env.local" <<EOF
NEXT_PUBLIC_LANGGRAPH_BASE_URL="${base_url}"
NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID="${assistant_id}"
EOF

echo "Wrote ${ui_dir}/.env.local"
