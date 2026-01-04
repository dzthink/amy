#!/usr/bin/env bash
set -euo pipefail

# Load env vars for local runs
if [ -f ami/.env ]; then
  set -a
  # shellcheck disable=SC1091
  source ami/.env
  set +a
fi

echo "OPENAI_API_KEY=${OPENAI_API_KEY:-unset}"
echo "AMI_MODEL=${AMI_MODEL:-openai:gpt-4o-mini}"
