import { create } from "zustand";
import type { Edge, Node } from "@xyflow/react";

export type AgentConfig = {
  provider: string;
  model: string;
  system_prompt: string;
  user_prompt: string;
  output_fields: { name: string; description: string }[];
  attachments: { name: string; path: string }[];
};

export type MicroserviceConfig = {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  url: string;
  headers: { key: string; value: string }[];
  body: string;
  timeout_seconds: number;
};

export type NodeStatus = "idle" | "running" | "ok" | "error" | "skipped";

export type AppNodeData = {
  label: string;
  config: AgentConfig | MicroserviceConfig;
  status: NodeStatus;
  output?: any;
  error?: string;
  duration_ms?: number;
};

export type AppNode = Node<AppNodeData> & { type: "agent" | "microservice" };

type State = {
  nodes: AppNode[];
  edges: Edge[];
  selectedNodeId: string | null;
  flowId: number | null;
  flowName: string;
  setNodes: (n: AppNode[]) => void;
  setEdges: (e: Edge[]) => void;
  selectNode: (id: string | null) => void;
  addNode: (n: AppNode) => void;
  updateNodeData: (id: string, patch: Partial<AppNodeData>) => void;
  updateNodeConfig: (id: string, patch: Record<string, any>) => void;
  removeNode: (id: string) => void;
  setFlow: (id: number | null, name: string, nodes: AppNode[], edges: Edge[]) => void;
  setFlowName: (name: string) => void;
};

export const defaultAgentConfig = (): AgentConfig => ({
  provider: "anthropic",
  model: "claude-sonnet-4-6",
  system_prompt: "You are a helpful assistant.",
  user_prompt: "",
  output_fields: [],
  attachments: [],
});

export const defaultMicroserviceConfig = (): MicroserviceConfig => ({
  method: "GET",
  url: "",
  headers: [{ key: "Content-Type", value: "application/json" }],
  body: "",
  timeout_seconds: 30,
});

export const useFlowStore = create<State>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  flowId: null,
  flowName: "Untitled flow",
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  selectNode: (id) => set({ selectedNodeId: id }),
  addNode: (n) => set((s) => ({ nodes: [...s.nodes, n] })),
  updateNodeData: (id, patch) =>
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...patch } } : n
      ),
    })),
  updateNodeConfig: (id, patch) =>
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === id
          ? { ...n, data: { ...n.data, config: { ...n.data.config, ...patch } } }
          : n
      ),
    })),
  removeNode: (id) =>
    set((s) => ({
      nodes: s.nodes.filter((n) => n.id !== id),
      edges: s.edges.filter((e) => e.source !== id && e.target !== id),
      selectedNodeId: s.selectedNodeId === id ? null : s.selectedNodeId,
    })),
  setFlow: (flowId, flowName, nodes, edges) =>
    set({ flowId, flowName, nodes, edges, selectedNodeId: null }),
  setFlowName: (flowName) => set({ flowName }),
}));
