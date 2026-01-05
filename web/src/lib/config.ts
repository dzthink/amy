export interface StandaloneConfig {
  deploymentUrl: string;
  assistantId: string;
  langsmithApiKey?: string;
}

const CONFIG_KEY = "deep-agent-config";
const ENV_DEPLOYMENT_URL = process.env.NEXT_PUBLIC_LANGGRAPH_API_URL;
const ENV_ASSISTANT_ID = process.env.NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID;
const ENV_LANGSMITH_API_KEY = process.env.NEXT_PUBLIC_LANGSMITH_API_KEY;

function getEnvConfig(): StandaloneConfig | null {
  if (!ENV_DEPLOYMENT_URL || !ENV_ASSISTANT_ID) {
    return null;
  }

  return {
    deploymentUrl: ENV_DEPLOYMENT_URL,
    assistantId: ENV_ASSISTANT_ID,
    langsmithApiKey: ENV_LANGSMITH_API_KEY || undefined,
  };
}

export function getConfig(): StandaloneConfig | null {
  if (typeof window === "undefined") return null;

  const stored = localStorage.getItem(CONFIG_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return getEnvConfig();
    }
  }

  return getEnvConfig();
}

export function saveConfig(config: StandaloneConfig): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
}
