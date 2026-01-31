"""Instrumentation for Agent Lightning integration.

Provides OpenTelemetry-based tracing for the Amy agent.
"""

from typing import Optional, Any, Dict
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
import structlog

logger = structlog.get_logger(__name__)


class AmyCallbackHandler(BaseCallbackHandler):
    """Callback handler for agent instrumentation."""

    def __init__(self):
        """Initialize callback handler."""
        super().__init__()
        self.run_id: Optional[str] = None
        self.spans: list[Dict[str, Any]] = []

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list[str],
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts processing."""
        self.spans.append({
            "type": "llm_start",
            "prompts": prompts,
            "kwargs": kwargs,
        })

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Called when LLM finishes processing."""
        self.spans.append({
            "type": "llm_end",
            "response": response,
            "kwargs": kwargs,
        })

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors."""
        self.spans.append({
            "type": "llm_error",
            "error": str(error),
            "kwargs": kwargs,
        })

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Called when tool starts."""
        self.spans.append({
            "type": "tool_start",
            "tool": serialized.get("name", "unknown"),
            "input": input_str,
            "kwargs": kwargs,
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when tool finishes."""
        self.spans.append({
            "type": "tool_end",
            "output": output[:500],  # Truncate long outputs
            "kwargs": kwargs,
        })

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when tool errors."""
        self.spans.append({
            "type": "tool_error",
            "error": str(error),
            "kwargs": kwargs,
        })


def get_agentlightning_handler():
    """Get Agent Lightning handler if available.

    Returns:
        Handler instance or None if not installed
    """
    try:
        from agentlightning import OtelTracer

        tracer = OtelTracer()
        return tracer.get_langchain_handler()
    except ImportError:
        logger.warning(
            "agentlightning not installed. "
            "Run: pip install agentlightning[apo]"
        )
        return None


def create_instrumentation():
    """Create instrumentation for the agent.

    Returns:
        Dictionary of callbacks
    """
    handler = get_agentlightning_handler()
    if handler:
        return {"callbacks": [handler]}
    return {"callbacks": [AmyCallbackHandler()]}
