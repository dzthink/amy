import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

const agentCoreUrl =
  process.env.AGENT_CORE_URL ??
  process.env.NEXT_PUBLIC_AGENT_CORE_URL ??
  "http://127.0.0.1:8000";

const serviceAdapter = new ExperimentalEmptyAdapter();

export const POST = async (req) => {
  const agentId = req.headers.get("x-agent-id") || undefined;
  const threadId = req.headers.get("x-thread-id") || undefined;
  const runtime = new CopilotRuntime({
    agents: {
      adk: new HttpAgent({
        url: `${agentCoreUrl}/`,
        agentId,
        threadId,
      }),
    },
  });

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
