# Architecture

## Core responsibilities
- ADK agent definition and orchestration.
- Markdown storage access (read/write/query).
- Schedule and todo management.
- Topic news collection and digest.
- Weekly report generation.
- CopilotKit runtime adapter for frontend integrations.

## Non-goals
- UI rendering.
- Platform-specific capabilities (handled in frontends).

## Suggested module layout (Python)
- `src/agent_core/` ADK agent and core APIs
- `src/agent_core/server.py` ADK FastAPI entry (AG-UI)
- `src/agent_core/storage/` Markdown adapters and filesystem IO
- `src/agent_core/schedule/` scheduling and todo logic
- `src/agent_core/news/` topic ingestion and summarization
- `src/agent_core/reports/` weekly report logic

## Web app (Next.js)
- `web/src/app/` CopilotKit UI
- `web/src/app/api/copilotkit/route.js` CopilotKit runtime endpoint
