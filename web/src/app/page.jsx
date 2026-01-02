"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

const agentCoreUrl =
  process.env.NEXT_PUBLIC_AGENT_CORE_URL ?? "http://127.0.0.1:8000";

const createConversation = () => ({
  id: `c-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
  title: "New chat",
  updated: "刚刚",
  threadId: globalThis.crypto?.randomUUID?.() ?? `thread-${Date.now()}`,
});

export default function Page() {
  const [agents, setAgents] = useState([]);
  const [activeAgentId, setActiveAgentId] = useState("");
  const [conversationsByAgent, setConversationsByAgent] = useState({});
  const [activeConversationId, setActiveConversationId] = useState("");
  const agentsInitialized = useRef(false);

  useEffect(() => {
    let isActive = true;
    const loadAgents = async () => {
      try {
        const response = await fetch(`${agentCoreUrl}/agents`);
        if (!response.ok) return;
        const payload = await response.json();
        const loaded = payload.agents ?? [];
        if (!isActive) return;
        setAgents(loaded);
        if (!agentsInitialized.current && loaded.length > 0) {
          const firstAgent = loaded[0];
          const initialConversation = createConversation();
          setConversationsByAgent({
            [firstAgent.id]: [initialConversation],
          });
          setActiveAgentId(firstAgent.id);
          setActiveConversationId(initialConversation.id);
          agentsInitialized.current = true;
        }
      } catch (error) {
        console.warn("Failed to load agents:", error);
      }
    };
    loadAgents();
    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (!activeAgentId || conversationsByAgent[activeAgentId]) return;
    const fallbackConversation = createConversation();
    setConversationsByAgent((prev) => ({
      ...prev,
      [activeAgentId]: [fallbackConversation],
    }));
    setActiveConversationId(fallbackConversation.id);
  }, [activeAgentId, conversationsByAgent]);

  const conversations = conversationsByAgent[activeAgentId] ?? [];

  const activeAgent = useMemo(
    () => agents.find((agent) => agent.id === activeAgentId),
    [agents, activeAgentId]
  );

  const activeConversation = useMemo(
    () => conversations.find((chat) => chat.id === activeConversationId),
    [conversations, activeConversationId]
  );

  const handleAddConversation = () => {
    if (!activeAgentId) return;
    const newConversation = createConversation();
    setConversationsByAgent((prev) => ({
      ...prev,
      [activeAgentId]: [newConversation, ...(prev[activeAgentId] ?? [])],
    }));
    setActiveConversationId(newConversation.id);
  };

  const copilotThreadId = activeConversation?.threadId ?? "";
  const copilotHeaders = useMemo(
    () => ({
      "x-agent-id": activeAgentId,
      "x-thread-id": copilotThreadId,
    }),
    [activeAgentId, copilotThreadId]
  );

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="adk"
      threadId={copilotThreadId}
      headers={copilotHeaders}
    >
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-mark">A</div>
            <div>
              <p className="brand-title">Amy Agent</p>
              <p className="brand-subtitle">ADK Console</p>
            </div>
          </div>

          <div className="sidebar-actions">
            <button className="new-chat" onClick={handleAddConversation}>
              + New chat
            </button>
            <div className="search">
              <span className="search-icon">⌕</span>
              <input placeholder="搜索" />
            </div>
          </div>

          <div className="section">
            <div className="section-header">
              <h2>Agents</h2>
              <span className="pill">{agents.length}</span>
            </div>
            <div className="agent-list">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className={`agent-block ${
                    agent.id === activeAgentId ? "active" : ""
                  }`}
                >
                  <button
                    className="agent-card"
                    onClick={() => {
                      setActiveAgentId(agent.id);
                      const first = conversationsByAgent[agent.id]?.[0];
                      setActiveConversationId(first?.id ?? "");
                    }}
                  >
                    <div className="agent-avatar">
                      {agent.name.slice(0, 1).toUpperCase()}
                    </div>
                    <div className="agent-meta">
                      <p>{agent.name}</p>
                      <span>{agent.description}</span>
                    </div>
                  </button>
                  <div className="agent-history">
                    <div className="section-header small">
                      <h3>History</h3>
                      <button className="ghost" onClick={handleAddConversation}>
                        + New
                      </button>
                    </div>
                    <div className="conversation-list">
                      {(conversationsByAgent[agent.id] ?? []).map((chat) => (
                        <button
                          key={chat.id}
                          className={`conversation-item ${
                            chat.id === activeConversationId ? "active" : ""
                          }`}
                          onClick={() => {
                            setActiveAgentId(agent.id);
                            setActiveConversationId(chat.id);
                          }}
                        >
                          <div>
                            <p>{chat.title}</p>
                            <span>{chat.updated}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="main">
          <header className="chat-header">
            <div>
              <p className="eyebrow">Active agent</p>
              <h1>{activeAgent?.name ?? "Loading..."}</h1>
              <p className="subtle">
                {activeConversation?.title ?? "Select a conversation"}
              </p>
            </div>
            <div className="header-actions">
              <button className="secondary">Share</button>
              <button className="primary">Start task</button>
            </div>
          </header>

          <section className="chat-layout">
            <div className="chat-panel">
              <div className="chat-stream">
                <CopilotChat
                  key={activeConversationId ?? "empty"}
                  className="copilot-chat"
                  labels={{
                    title: activeAgent?.name ?? "Agent",
                    placeholder: "输入消息或 / 调用工具…",
                  }}
                  onSubmitMessage={(message) => {
                    const trimmed = message.trim();
                    if (!trimmed || !activeConversation || !activeAgentId) return;
                    setConversationsByAgent((prev) => {
                      const list = prev[activeAgentId] ?? [];
                      return {
                        ...prev,
                        [activeAgentId]: list.map((chat) =>
                          chat.id === activeConversation.id
                            ? {
                                ...chat,
                                title:
                                  chat.title === "New chat"
                                    ? trimmed.slice(0, 32)
                                    : chat.title,
                                updated: "刚刚",
                              }
                            : chat
                        ),
                      };
                    });
                  }}
                />
              </div>
            </div>

            <aside className="workspace">
              <div className="workspace-card">
                <p className="eyebrow">Workspace</p>
                <h3>Agent Output</h3>
                <p className="subtle">
                  Reserve this area for charts, tool logs, or real-time artifacts.
                </p>
              </div>
              <div className="workspace-grid">
                <div className="workspace-tile">
                  <p className="tile-title">Tasks</p>
                  <p>3 running · 2 queued</p>
                </div>
                <div className="workspace-tile">
                  <p className="tile-title">Memory</p>
                  <p>Synced 1.2k notes</p>
                </div>
                <div className="workspace-tile">
                  <p className="tile-title">Tools</p>
                  <p>Calendar, Docs, Metrics</p>
                </div>
                <div className="workspace-tile">
                  <p className="tile-title">Signals</p>
                  <p>+12% engagement</p>
                </div>
              </div>
            </aside>
          </section>
        </main>
      </div>
    </CopilotKit>
  );
}
