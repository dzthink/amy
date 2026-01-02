# Requirements

## Functional
- Schedule and todo management, auto-arrange, weekly report writing.
- Daily collection of important news by topic.

## Non-functional
- Web client only; ADK agent runs locally or on Linux.
- Internal data stored as Markdown on local disk.
- Interaction beyond pure chatbot; CopilotKit + AG-UI.
- Agent core implemented in Python with ADK for reuse across platforms.

## Initial assumptions
- Markdown data lives under `data/` with per-domain folders.
- All agent logic runs locally against the Markdown store.
