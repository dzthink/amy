# Amy

Personal AI Agent based on LangChain.

## Setup

```bash
# Install dependencies
uv sync

# Configure API key
export ANTHROPIC_API_KEY="your-key"

# Run CLI
uv run python cli.py
```

## Architecture

```
user <-> orchestrator agent <-> tools / skills / subagents
                              <-> memory (md files)
```
