#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

if [ ! -f "ami/langgraph.json" ]; then
  echo "Missing ami/langgraph.json" >&2
  exit 1
fi

assistant_id="$(python3 - <<'PY'
import json

with open("ami/langgraph.json", "r", encoding="utf-8") as handle:
    data = json.load(handle)

graphs = data.get("graphs", {})
print(next(iter(graphs.keys()), ""))
PY
)"

if [ -z "$assistant_id" ]; then
  echo "No graph id found in ami/langgraph.json" >&2
  exit 1
fi

deployment_url="${LANGGRAPH_API_URL:-http://127.0.0.1:2024}"
out_file="web/.env.local"

{
  echo "NEXT_PUBLIC_LANGGRAPH_API_URL=$deployment_url"
  echo "NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=$assistant_id"
  if [ -n "${NEXT_PUBLIC_LANGSMITH_API_KEY:-}" ]; then
    echo "NEXT_PUBLIC_LANGSMITH_API_KEY=$NEXT_PUBLIC_LANGSMITH_API_KEY"
  fi
} > "$out_file"

echo "Wrote $out_file"
