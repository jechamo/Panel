import type {
  AgentNodeConfig,
  AttachmentReference,
  FlowDocument,
  FlowPayload,
  FlowSummary,
  JsonValue,
  MicroserviceNodeConfig,
} from './types';

export type HealthResponse = {
  ok: boolean;
};

export type ApiError = {
  code: string;
  message: string;
};

export type MicroserviceRunResult = {
  output: JsonValue;
  status_code: number;
};

export type AgentRunResult = {
  output: JsonValue;
  status_code: number;
};

type NodeExecutionContext = {
  flowId?: string | null;
  input?: JsonValue;
};

type ApiEnvelope<T> = {
  ok: boolean;
  data: T;
  error: ApiError | null;
};

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

function getApiBaseUrl(): string {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL;

  return configuredBaseUrl && configuredBaseUrl.length > 0
    ? configuredBaseUrl
    : DEFAULT_API_BASE_URL;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>('/health');
}

async function requestEnvelope<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  const payload = (await response.json()) as ApiEnvelope<T>;

  if (!response.ok || !payload.ok) {
    throw new Error(payload.error?.message ?? `Request failed with status ${response.status}`);
  }

  return payload.data;
}

export async function createFlow(flow: FlowPayload): Promise<FlowDocument> {
  return requestEnvelope<FlowDocument>('/flows', {
    method: 'POST',
    body: JSON.stringify(flow),
  });
}

export async function deleteFlow(flowId: string): Promise<void> {
  await requestEnvelope<{ deleted: true; id: string }>(`/flows/${flowId}`, {
    method: 'DELETE',
  });
}

export async function getFlow(flowId: string): Promise<FlowDocument> {
  return requestEnvelope<FlowDocument>(`/flows/${flowId}`);
}

export async function listFlows(): Promise<FlowSummary[]> {
  return requestEnvelope<FlowSummary[]>('/flows');
}

export async function updateFlow(flow: FlowDocument): Promise<FlowDocument> {
  return requestEnvelope<FlowDocument>(`/flows/${flow.id}`, {
    method: 'PUT',
    body: JSON.stringify(flow),
  });
}

export async function runMicroserviceNode(
  nodeId: string,
  config: MicroserviceNodeConfig,
  context?: NodeExecutionContext,
): Promise<MicroserviceRunResult> {
  return requestEnvelope<MicroserviceRunResult>(`/nodes/${nodeId}/run`, {
    method: 'POST',
    body: JSON.stringify({
      kind: 'microservice',
      config,
      context,
    }),
  });
}

export async function runAgentNode(
  nodeId: string,
  config: AgentNodeConfig,
  context?: NodeExecutionContext,
): Promise<AgentRunResult> {
  return requestEnvelope<AgentRunResult>(`/nodes/${nodeId}/run`, {
    method: 'POST',
    body: JSON.stringify({
      kind: 'agent',
      config: {
        model: config.model,
        outputFields: config.outputFields,
        systemPrompt: config.systemPrompt,
        userPrompt: config.userPrompt,
      },
      context,
    }),
  });
}

export async function uploadAttachment(flowId: string, file: File): Promise<AttachmentReference> {
  const formData = new FormData();
  formData.append('flow_id', flowId);
  formData.append('file', file);

  const response = await fetch(`${getApiBaseUrl()}/files/upload`, {
    method: 'POST',
    body: formData,
  });

  const payload = (await response.json()) as ApiEnvelope<AttachmentReference>;

  if (!response.ok || !payload.ok) {
    throw new Error(payload.error?.message ?? `Request failed with status ${response.status}`);
  }

  return payload.data;
}