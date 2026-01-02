"""ADK agent wiring based on CopilotKit's official ADK integration."""

from __future__ import annotations

import os
from typing import Dict, Optional

from ag_ui_adk import ADKAgent
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from .storage.markdown_store import (
    read_news_topics,
    read_todos,
    write_news_topics,
    write_todos,
)


def set_todos(tool_context: ToolContext, todos: list[str]) -> Dict[str, str]:
    """Replace the todo list stored in the agent state."""
    cleaned = [item.strip() for item in todos if item and item.strip()]
    write_todos(cleaned)
    tool_context.state["todos"] = cleaned
    return {"status": "success", "message": "Todos updated."}


def set_news_topics(tool_context: ToolContext, topics: list[str]) -> Dict[str, str]:
    """Replace the news topics stored in the agent state."""
    cleaned = [item.strip() for item in topics if item and item.strip()]
    write_news_topics(cleaned)
    tool_context.state["news_topics"] = cleaned
    return {"status": "success", "message": "News topics updated."}


def on_before_agent(callback_context: CallbackContext):
    """Initialize state keys if missing."""
    if "todos" not in callback_context.state:
        callback_context.state["todos"] = read_todos()
    if "news_topics" not in callback_context.state:
        callback_context.state["news_topics"] = read_news_topics()

    return None


def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inject current state into the system instruction."""
    state = callback_context.state
    todos = state.get("todos", [])
    topics = state.get("news_topics", [])

    original_instruction = llm_request.config.system_instruction
    original_text = ""
    if original_instruction is not None:
        if hasattr(original_instruction, "parts"):
            parts = getattr(original_instruction, "parts") or []
            if parts and hasattr(parts[0], "text"):
                original_text = parts[0].text or ""
        else:
            original_text = str(original_instruction)

    prefix = (
        "You are Amy, a local personal agent. "
        "Current todos: "
        f"{todos}. "
        "Current news topics: "
        f"{topics}. "
        "When updating todos or news topics, call the appropriate tool."
    )
    llm_request.config.system_instruction = prefix + original_text
    return None


def get_agent_metadata() -> Dict[str, str]:
    """Return metadata for the configured ADK agent."""
    return {
        "id": os.getenv("AMY_AGENT_ID", "amy-agent"),
        "name": os.getenv("AMY_AGENT_NAME", "AmyAgent"),
        "description": os.getenv(
            "AMY_AGENT_DESCRIPTION", "Local personal agent for daily tasks."
        ),
    }


def create_agent() -> ADKAgent:
    """Create and return the ADK agent instance."""
    metadata = get_agent_metadata()
    model_name = os.getenv("AMY_LLM_MODEL", "deepseek/deepseek-chat")
    model = LiteLlm(model=model_name)
    amy_agent = LlmAgent(
        name=metadata["name"],
        model=model,
        instruction=(
            "You manage todos and daily news topics. "
            "Use set_todos to replace the full todo list. "
            "Use set_news_topics to replace the full list of news topics."
        ),
        tools=[set_todos, set_news_topics],
        before_agent_callback=on_before_agent,
        before_model_callback=before_model_modifier,
    )

    return ADKAgent(
        adk_agent=amy_agent,
        user_id="amy_local_user",
        session_timeout_seconds=3600,
        use_in_memory_services=True,
    )
