# Agent Core (Python + ADK)

ADK-based agent core intended to run locally on macOS and deploy to Linux as a service for iOS/web clients.

Goals:
- Single codebase for local and server modes.
- Markdown storage on disk (`data/`).
- Clean API surface for multiple frontends.

Local mode:
- Run an ADK agent process on the same machine as the macOS client.

Server mode:
- Run the ADK agent in Linux as a backend for iOS/web.

Notes:
- `google-adk` is the official ADK package name used by CopilotKit's ADK starter.
- CopilotKit runtime is hosted in the web app via `web/src/app/api/copilotkit/route.js`.

Entry point:
- `src/agent_core/server.py`

Local dev:
- `cd agent && uv venv`
- `source .venv/bin/activate`
- `uv pip install -e .`
- `python -m agent_core.server`
- `cd web && npm install && npm run dev`

Environment:
- `AGENT_CORE_PORT` default `8000`
- `AGENT_CORE_HOST` default `127.0.0.1`
- `AMY_LLM_MODEL` default `deepseek/deepseek-chat`
- `DEEPSEEK_API_KEY` required for DeepSeek via LiteLLM
