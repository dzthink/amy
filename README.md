# ami (Deep Agents)

Personal AI assistant built on LangChain Deep Agents, with a LangGraph server backend
and an optional Deep Agents UI frontend.

## Repository Structure

```
ami/                    # Python agent + LangGraph server
  agent.py              # Agent builder
  graph.py              # LangGraph graph entrypoint
  langgraph.json         # LangGraph server config
  requirements.txt       # Python deps
  .env.example           # Environment variables template
scripts/                # Helper scripts (UI setup, run commands)
web/                    # UI workspace (agent chat UI lives here)
```

## Backend: run the agent (CLI)

```bash
uv venv .venv
uv pip install -r ami/requirements.txt --python .venv/bin/python

# export env vars (see ami/.env.example for sample values)
# export DEEPSEEK_API_KEY=...
# export DEEPSEEK_BASE_URL=https://api.deepseek.com
# export AMI_LLM_MODEL=openai:deepseek-chat

python -m ami "你好，帮我规划本周学习任务"
```

## Backend: run LangGraph server (for UI)

```bash
cd ami
langgraph dev
```

## Frontend: Agent Chat UI

Create the UI with `npx create-agent-chat-app` (wrapped by `./scripts/setup_ui.sh`):

```bash
./scripts/setup_ui.sh
./scripts/sync_ui_config.sh
cd web
pnpm install
pnpm dev
```

UI defaults are synced from `ami/langgraph.json` into `web/.env.local`
via `./scripts/sync_ui_config.sh` (base URL defaults to `http://127.0.0.1:2024`).
Use Assistant ID `ami` (from `ami/langgraph.json`).

## One command (dev)

```bash
./scripts/dev.sh
```

## UI + Agent Integration

The UI reads the LangGraph deployment URL and assistant ID from either local
storage or environment variables:

```
NEXT_PUBLIC_LANGGRAPH_API_URL=http://127.0.0.1:2024
NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=ami
```

You can generate `web/.env.local` with:

```bash
./scripts/sync_ui_config.sh
```
