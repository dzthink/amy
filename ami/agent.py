import os
import sys

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

try:
    from .prompts import SYSTEM_PROMPT
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from prompts import SYSTEM_PROMPT


def build_agent():
    if os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["DEEPSEEK_API_KEY"]
    if os.environ.get("DEEPSEEK_BASE_URL") and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.environ["DEEPSEEK_BASE_URL"]
    model_name = os.environ.get("AMI_LLM_MODEL", "openai:gpt-4o-mini")
    model = init_chat_model(model_name)
    return create_deep_agent(model=model, system_prompt=SYSTEM_PROMPT)
