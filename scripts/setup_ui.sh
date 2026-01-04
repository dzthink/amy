#!/usr/bin/env bash
set -euo pipefail

ui_root="web"

if [ -f "$ui_root/package.json" ]; then
  echo "UI already present at $ui_root"
  exit 0
fi

if [ -d "$ui_root" ] && [ -n "$(ls -A "$ui_root")" ]; then
  echo "Path exists but is not an Agent Chat UI project: $ui_root" >&2
  echo "Move it aside or delete it, then re-run." >&2
  exit 1
fi

npx create-agent-chat-app --project-name "$ui_root"
