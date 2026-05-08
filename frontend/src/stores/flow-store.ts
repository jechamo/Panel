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

import type { WorkflowNode, WorkflowNodeData, NodeKind } from '../lib/types';

type FlowState = {
  edges: Edge[];
  nodes: WorkflowNode[];
  addNode: (kind: NodeKind) => void;
  onConnect: (connection: Connection) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onNodesChange: (changes: NodeChange<WorkflowNode>[]) => void;
};

const templates: Record<NodeKind, Omit<WorkflowNodeData, 'status'>> = {
  agent: {
    kind: 'agent',
    title: 'Agente',
    description: 'Prompt estructurado y salida reusable.',
  },
  microservice: {
    kind: 'microservice',
    title: 'Microservicio',
    description: 'Endpoint HTTP con entrada y salida JSON.',
  },
};

const positions: Record<NodeKind, { x: number; y: number }> = {
  agent: { x: 120, y: 140 },
  microservice: { x: 420, y: 300 },
};

function makeNode(kind: NodeKind, index: number): WorkflowNode {
  const base = templates[kind];
  const offset = index * 36;

  return {
    id: crypto.randomUUID(),
    type: 'workflow',
    position: {
      x: positions[kind].x + offset,
      y: positions[kind].y + offset,
    },
    data: {
      ...base,
      status: 'idle',
    },
  };
}

export const useFlowStore = create<FlowState>((set) => ({
  nodes: [],
  edges: [],
  addNode: (kind) =>
    set((state) => ({
      nodes: [...state.nodes, makeNode(kind, state.nodes.length)],
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
    set((state) => ({
      nodes: applyNodeChanges(changes, state.nodes),
    })),
}));