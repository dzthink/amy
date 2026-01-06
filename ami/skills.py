import importlib
import os
from datetime import datetime, timezone
from typing import Iterable, List

from langchain.tools import tool


@tool
def current_time() -> str:
    """Return the current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


@tool
def echo(text: str) -> str:
    """Echo back the provided text."""
    return text


def _load_mcp_tools() -> List:
    config_path = os.environ.get("AMI_MCP_CONFIG")
    if not config_path:
        return []
    try:
        from langchain_mcp_adapters.tools import load_mcp_tools
    except ImportError:
        return []
    try:
        return list(load_mcp_tools(config_path))
    except Exception:
        return []


def _load_external_skills() -> List:
    module_name = os.environ.get("AMI_SKILLS_MODULE")
    if not module_name:
        return []
    module = importlib.import_module(module_name)
    build_fn = getattr(module, "build_skills", None)
    if callable(build_fn):
        return list(build_fn())
    skills = getattr(module, "SKILLS", None)
    if isinstance(skills, Iterable):
        return list(skills)
    return []


def build_skills() -> List:
    skills: List = [current_time, echo]
    skills.extend(_load_mcp_tools())
    skills.extend(_load_external_skills())
    return skills
