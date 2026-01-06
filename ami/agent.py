import json
import os
import sys
from typing import Iterable, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from .prompts import ORCHESTRATOR_PROMPT, SUB_AGENT_PROMPTS, SYSTEM_PROMPT
    from .skills import build_skills
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from prompts import ORCHESTRATOR_PROMPT, SUB_AGENT_PROMPTS, SYSTEM_PROMPT
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


class OrchestratorAgent:
    def __init__(
        self,
        router_model,
        self_agent: AmiAgent,
        sub_agents: dict[str, tuple[str, AmiAgent]],
    ):
        self._router_model = router_model
        self._self_agent = self_agent
        self._sub_agents = sub_agents
        self._router_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ORCHESTRATOR_PROMPT),
                (
                    "human",
                    "User request:\n{input}\n\n"
                    "Available sub-agents:\n{agents}\n\n"
                    "Respond with JSON only: "
                    '{"action": "self"|"delegate", "agent": "<name or null>", "reason": "<short>"}',
                ),
            ]
        )

    def _format_agents(self) -> str:
        if not self._sub_agents:
            return "None"
        lines = []
        for name, (description, _) in self._sub_agents.items():
            lines.append(f"- {name}: {description}")
        return "\n".join(lines)

    def _route(self, user_input: str) -> Optional[str]:
        if not self._sub_agents:
            return None
        prompt = self._router_prompt.format_messages(
            input=user_input, agents=self._format_agents()
        )
        response = self._router_model.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return None
        if payload.get("action") != "delegate":
            return None
        agent_name = payload.get("agent")
        if agent_name in self._sub_agents:
            return agent_name
        return None

    def invoke(self, state: dict) -> dict:
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}
        last_message = messages[-1]
        if isinstance(last_message, BaseMessage):
            user_input = last_message.content
        else:
            user_input = last_message.get("content", "")
        agent_name = self._route(user_input)
        if agent_name:
            _, agent = self._sub_agents[agent_name]
            return agent.invoke(state)
        return self._self_agent.invoke(state)


def _build_react_agent(system_prompt: str, model, skills) -> AmiAgent:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    agent = create_react_agent(model, skills, prompt)
    executor = AgentExecutor(agent=agent, tools=skills, memory=memory, verbose=False)
    return AmiAgent(executor, memory)


def build_agent():
    if os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["DEEPSEEK_API_KEY"]
    if os.environ.get("DEEPSEEK_BASE_URL") and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.environ["DEEPSEEK_BASE_URL"]
    model_name = os.environ.get("AMI_LLM_MODEL", "openai:gpt-4o-mini")
    model = init_chat_model(model_name)
    skills = build_skills()
    self_agent = _build_react_agent(SYSTEM_PROMPT, model, skills)
    sub_agents: dict[str, tuple[str, AmiAgent]] = {
        name: (description, _build_react_agent(description, model, skills))
        for name, description in SUB_AGENT_PROMPTS.items()
    }
    return OrchestratorAgent(model, self_agent, sub_agents)
