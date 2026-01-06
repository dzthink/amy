import os
import sys
from typing import Iterable, List

from langchain.agents import AgentExecutor, create_react_agent
from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from .prompts import SYSTEM_PROMPT
    from .skills import build_skills
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from prompts import SYSTEM_PROMPT
    from skills import build_skills


def _normalize_messages(messages: Iterable[BaseMessage | dict]) -> List[BaseMessage]:
    normalized: List[BaseMessage] = []
    for message in messages:
        if isinstance(message, BaseMessage):
            normalized.append(message)
            continue
        role = message.get("role")
        content = message.get("content", "")
        if role == "system":
            normalized.append(SystemMessage(content=content))
        elif role == "assistant":
            normalized.append(AIMessage(content=content))
        else:
            normalized.append(HumanMessage(content=content))
    return normalized


class AmiAgent:
    def __init__(self, executor: AgentExecutor, memory: ConversationBufferMemory):
        self._executor = executor
        self._memory = memory

    def _hydrate_memory(self, messages: Iterable[BaseMessage | dict]) -> None:
        if self._memory.chat_memory.messages:
            return
        normalized = _normalize_messages(messages)
        if normalized:
            self._memory.chat_memory.add_messages(normalized)

    def invoke(self, state: dict) -> dict:
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}
        self._hydrate_memory(messages[:-1])
        last_message = messages[-1]
        if isinstance(last_message, BaseMessage):
            user_input = last_message.content
        else:
            user_input = last_message.get("content", "")
        result = self._executor.invoke({"input": user_input})
        assistant_message = {"role": "assistant", "content": result.get("output", "")}
        return {"messages": list(messages) + [assistant_message]}


def build_agent():
    if os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["DEEPSEEK_API_KEY"]
    if os.environ.get("DEEPSEEK_BASE_URL") and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.environ["DEEPSEEK_BASE_URL"]
    model_name = os.environ.get("AMI_LLM_MODEL", "openai:gpt-4o-mini")
    model = init_chat_model(model_name)

    skills = build_skills()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    agent = create_react_agent(model, skills, prompt)
    executor = AgentExecutor(agent=agent, tools=skills, memory=memory, verbose=False)
    return AmiAgent(executor, memory)
