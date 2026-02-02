"""Orchestrator Agent - Main agent for task handling."""

from typing import Optional, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
import os
import structlog

import config
from .memory import MemorySystem
from .tools import FileTool, SearchTool
from .skills import SummarizeSkill, WebSearchSkill

logger = structlog.get_logger(__name__)


class Orchestrator:
    """Main orchestrator agent that coordinates tools and memory."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize orchestrator.

        Args:
            api_key: API key (from .env if not provided)
            base_url: Base URL for OpenAI-compatible API (from .env if not provided)
            model: Model name (from config.py)
            max_tokens: Max tokens (from config.py)
            temperature: Temperature (from config.py)
        """
        self.memory = MemorySystem(
            semantic_file=config.MEMORY_SEMANTIC_FILE,
            episodic_dir=config.MEMORY_EPISODIC_DIR,
        )

        # Initialize tools
        self.file_tool = FileTool()
        self.search_tool = SearchTool()
        self.summarize_skill = SummarizeSkill()
        self.web_search_skill = WebSearchSkill()

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=api_key or config.LLM_API_KEY,
            base_url=base_url or config.LLM_BASE_URL,
            model=model or config.LLM_MODEL,
            max_tokens=max_tokens or config.LLM_MAX_TOKENS,
            temperature=temperature or config.LLM_TEMPERATURE,
        )

        # Build tools list
        self.tools = self._build_tools()

        # Create agent
        self.agent = self._create_agent()

        logger.info("Orchestrator initialized")

    def _build_tools(self) -> List[BaseTool]:
        """Build list of available tools.

        Returns:
            List of LangChain tools
        """
        from langchain_core.tools import convert_to_openai_tool

        tools = [
            self.file_tool.read_file,
            self.file_tool.write_file,
            self.file_tool.list_directory,
            self.file_tool.create_directory,
            self.search_tool.search_files,
            self.search_tool.grep,
            self.summarize_skill.summarize_text,
            self.summarize_skill.extract_key_points,
            self.web_search_skill.web_search,
            self.web_search_skill.web_fetch,
        ]
        return [convert_to_openai_tool(t) for t in tools]

    def _create_agent(self):
        """Create the LangGraph ReAct agent.

        Returns:
            Compiled agent executor
        """
        system_prompt = config.AGENT_SYSTEM_PROMPT

        # Add memory context to system prompt
        semantic_memory = self.memory.read_semantic_memory()
        if semantic_memory:
            system_prompt += f"""

## User Semantic Memory

{semantic_memory}
"""
        return create_react_agent(self.llm, self.tools, prompt=system_prompt)

    def _get_memory_context(self) -> str:
        """Get relevant memory context for current conversation.

        Returns:
            Context string from memories
        """
        context_parts = []

        # Get semantic memory
        semantic = self.memory.read_semantic_memory()
        if semantic:
            context_parts.append(f"### Semantic Memory\n\n{semantic}")

        # Get recent episodic memories
        recent = self.memory.get_recent_episodic_memories(days=7)
        if recent:
            context_parts.append(f"### Recent Conversations\n\n{'---'.join(recent)}")

        return "\n\n".join(context_parts) if context_parts else ""

    async def run(
        self,
        message: str,
        conversation_history: Optional[List[BaseMessage]] = None,
        stream: bool = True,
    ) -> Any:
        """Run the agent with a user message.

        Args:
            message: User message
            conversation_history: Previous conversation messages
            stream: Whether to stream output

        Returns:
            Agent response
        """
        # Add conversation turn to episodic memory
        self.memory.add_conversation_turn("user", message)

        # Prepare inputs
        inputs = {"messages": [HumanMessage(content=message)]}

        # Run agent
        if stream:
            return await self.agent.ainvoke(inputs)
        else:
            return await self.agent.ainvoke(inputs)

    async def stream(
        self,
        message: str,
        conversation_history: Optional[List[BaseMessage]] = None,
    ):
        """Stream agent response.

        Args:
            message: User message
            conversation_history: Previous conversation messages

        Yields:
            Tokens from the agent response
        """
        inputs = {"messages": [HumanMessage(content=message)]}
        async for chunk in self.agent.astream(inputs):
            if "messages" in chunk:
                for msg in chunk["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        yield msg.content

        # Add assistant turn to memory
        # Note: Would need to capture the full response first
