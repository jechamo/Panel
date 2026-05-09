export type FlowSummary = { id: number; name: string; updated_at: string };
export type FlowDetail = FlowSummary & { graph: any };
export type SettingsView = {
  anthropic_api_key: boolean;
  openai_api_key: boolean;
  gemini_api_key: boolean;
  github_token: boolean;
};
export type ProviderSpec = {
  label: string;
  default_model: string;
  models: string[];
  secret_key: string;
};
export type RunResult = {
  node_id: string;
  status: "ok" | "error" | "skipped";
  output?: any;
  error?: string;
  duration_ms: number;
};
export type Variable = {
  path: string;
  placeholder: string;
  source: "cached" | "schema" | "node";
  sample?: string | null;
};

const j = (r: Response) => {
  if (!r.ok) return r.text().then((t) => Promise.reject(new Error(t || r.statusText)));
  return r.json();
};

export const api = {
  listFlows: (): Promise<FlowSummary[]> => fetch("/api/flows").then(j),
  getFlow: (id: number): Promise<FlowDetail> => fetch(`/api/flows/${id}`).then(j),
  createFlow: (name: string, graph: any): Promise<FlowDetail> =>
    fetch("/api/flows", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, graph }),
    }).then(j),
  updateFlow: (id: number, body: { name?: string; graph?: any }): Promise<FlowDetail> =>
    fetch(`/api/flows/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(j),
  deleteFlow: (id: number) => fetch(`/api/flows/${id}`, { method: "DELETE" }),

  getSettings: (): Promise<SettingsView> => fetch("/api/settings").then(j),
  putSetting: (key: string, value: string) =>
    fetch("/api/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, value }),
    }).then(j),
  getProviders: (): Promise<Record<string, ProviderSpec>> =>
    fetch("/api/settings/providers").then(j),

  uploadFile: async (file: File): Promise<{ name: string; path: string; size: number }> => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch("/api/files/upload", { method: "POST", body: fd }).then(j);
  },

  variables: (
    nodes: any[],
    edges: any[],
    last_outputs: Record<string, any>,
    node_id: string
  ): Promise<{ variables: Variable[] }> =>
    fetch("/api/introspect/variables", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes, edges, last_outputs, node_id }),
    }).then(j),

  run: (graph: any, node_id?: string): Promise<{ results: RunResult[] }> =>
    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ graph, node_id: node_id ?? null }),
    }).then(j),
};
