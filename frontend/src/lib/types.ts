import type { Node } from '@xyflow/react';

export type NodeKind = 'agent' | 'microservice';
export type NodeStatus = 'idle' | 'running' | 'success' | 'error';
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type AttachmentReference = {
  id: string;
  mimeType: string;
  name: string;
};

export type OutputField = {
  id: string;
  name: string;
  description: string;
};

export type HeaderField = {
  id: string;
  key: string;
  value: string;
};

export type AgentNodeConfig = {
  systemPrompt: string;
  userPrompt: string;
  attachments: AttachmentReference[];
  outputFields: OutputField[];
  model: string;
};

export type MicroserviceNodeConfig = {
  endpoint: string;
  method: HttpMethod;
  headers: HeaderField[];
  payload: string;
};

type BaseWorkflowNodeData = {
  title: string;
  description: string;
  status: NodeStatus;
};

export type AgentNodeData = BaseWorkflowNodeData & {
  kind: 'agent';
  config: AgentNodeConfig;
};

export type MicroserviceNodeData = BaseWorkflowNodeData & {
  kind: 'microservice';
  config: MicroserviceNodeConfig;
};

export type WorkflowNodeData = AgentNodeData | MicroserviceNodeData;

export type WorkflowNode = Node<WorkflowNodeData, 'workflow'>;