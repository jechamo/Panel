import type { Node } from '@xyflow/react';

export type NodeKind = 'agent' | 'microservice';
export type NodeStatus = 'idle' | 'running' | 'success' | 'error';

export type WorkflowNodeData = {
  kind: NodeKind;
  title: string;
  description: string;
  status: NodeStatus;
};

export type WorkflowNode = Node<WorkflowNodeData, 'workflow'>;