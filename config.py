"""Amy - Personal AI Agent Configuration.

LLM settings and non-sensitive config.
API credentials (api_key, base_url) loaded from .env.
"""

import os

# LLM Configuration
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
LLM_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
LLM_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

# Memory Configuration
MEMORY_SEMANTIC_FILE = "memory/semantic_memory.md"
MEMORY_EPISODIC_DIR = "memory/episodic"
MEMORY_MAX_RECENT = 10

# Agent System Prompt
AGENT_SYSTEM_PROMPT = """You are Amy, a helpful personal AI assistant.
You have access to various tools and a memory system that stores:
- Semantic memory: General knowledge and facts about the user
- Episodic memory: Daily experiences and conversations

Use your tools wisely to help the user with their tasks.
Always be concise, helpful, and respectful.
"""
