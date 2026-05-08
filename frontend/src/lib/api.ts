export type HealthResponse = {
  ok: boolean;
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