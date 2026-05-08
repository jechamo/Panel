import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type NodeChange,
} from '@xyflow/react';
import { create } from 'zustand';

import type {
  AgentNodeConfig,
  AgentNodeData,
  FlowDocument,
  FlowPayload,
  JsonValue,
  MicroserviceNodeConfig,
  MicroserviceNodeData,
  NodeKind,
  WorkflowNode,
  WorkflowNodeData,
} from '../lib/types';

type FlowState = {
  currentFlowId: string | null;
  currentFlowName: string;
  edges: Edge[];
  nodes: WorkflowNode[];
  selectedNodeId: string | null;
  addNode: (kind: NodeKind) => void;
  buildFlowPayload: () => FlowPayload;
  loadFlow: (flow: FlowDocument) => void;
  selectNode: (nodeId: string | null) => void;
  setCurrentFlowMeta: (flowId: string | null, name: string) => void;
  setNodeRuntimeState: (nodeId: string, status: WorkflowNodeData['status'], output: JsonValue | null, lastError: string | null) => void;
  onConnect: (connection: Connection) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onNodesChange: (changes: NodeChange<WorkflowNode>[]) => void;
  updateNodeData: (nodeId: string, updater: (data: WorkflowNodeData) => WorkflowNodeData) => void;
};

const agentTemplate: Omit<AgentNodeData, 'status'> = {
  kind: 'agent',
  title: 'Agente',
  description: 'Prompt estructurado y salida reusable.',
  lastError: null,
  output: null,
  config: {
    systemPrompt: '',
    userPrompt: '',
    attachments: [],
    outputFields: [
      {
        id: crypto.randomUUID(),
        name: '',
        description: '',
      },
    ],
    model: '',
  } satisfies AgentNodeConfig,
};

const microserviceTemplate: Omit<MicroserviceNodeData, 'status'> = {
  kind: 'microservice',
  title: 'Microservicio',
  description: 'Endpoint HTTP con entrada y salida JSON.',
  lastError: null,
  output: null,
  config: {
    endpoint: '',
    method: 'POST',
    headers: [
      {
        id: crypto.randomUUID(),
        key: '',
        value: '',
      },
    ],
    payload: '{\n  \n}',
  } satisfies MicroserviceNodeConfig,
};

const positions: Record<NodeKind, { x: number; y: number }> = {
  agent: { x: 120, y: 140 },
  microservice: { x: 420, y: 300 },
};

function makeNode(kind: NodeKind, index: number): WorkflowNode {
  const offset = index * 36;
  const position = {
    x: positions[kind].x + offset,
    y: positions[kind].y + offset,
  };

  if (kind === 'agent') {
    return {
      id: crypto.randomUUID(),
      type: 'workflow',
      position,
      data: {
        ...agentTemplate,
        status: 'idle',
      },
    };
  }

  return {
    id: crypto.randomUUID(),
    type: 'workflow',
    position,
    data: {
      ...microserviceTemplate,
      status: 'idle',
    },
  };
}

export const useFlowStore = create<FlowState>((set, get) => ({
  currentFlowId: null,
  currentFlowName: 'Mi flujo',
  nodes: [],
  edges: [],
  selectedNodeId: null,
  addNode: (kind) =>
    set((state) => {
      const nextNode = makeNode(kind, state.nodes.length);

      return {
        nodes: [...state.nodes, nextNode],
        selectedNodeId: nextNode.id,
      };
    }),
  buildFlowPayload: (): FlowPayload => {
    const state = get();

    return {
      name: state.currentFlowName.trim() || 'Mi flujo',
      nodes: state.nodes,
      edges: state.edges,
      version: 1,
    };
  },
  loadFlow: (flow) =>
    set(() => ({
      currentFlowId: flow.id,
      currentFlowName: flow.name,
      nodes: flow.nodes,
      edges: flow.edges,
      selectedNodeId: null,
    })),
  selectNode: (nodeId) => set(() => ({ selectedNodeId: nodeId })),
  setCurrentFlowMeta: (flowId, name) => set(() => ({ currentFlowId: flowId, currentFlowName: name })),
  setNodeRuntimeState: (nodeId, status, output, lastError) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                status,
                output,
                lastError,
              },
            }
          : node,
      ),
    })),
  onConnect: (connection) =>
    set((state) => ({
      edges: addEdge(
        {
          ...connection,
          animated: true,
          style: { stroke: '#58c4dd', strokeWidth: 2 },
        },
        state.edges,
      ),
    })),
  onEdgesChange: (changes) =>
    set((state) => ({
      edges: applyEdgeChanges(changes, state.edges),
    })),
  onNodesChange: (changes) =>
    set((state) => {
      const nextNodes = applyNodeChanges(changes, state.nodes);
      const hasSelectedNode = state.selectedNodeId
        ? nextNodes.some((node) => node.id === state.selectedNodeId)
        : false;

      return {
        nodes: nextNodes,
        selectedNodeId: hasSelectedNode ? state.selectedNodeId : null,
      };
    }),
  updateNodeData: (nodeId, updater) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: updater(node.data),
            }
          : node,
      ),
    })),
}));