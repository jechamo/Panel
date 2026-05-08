from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app


def test_node_run_resolves_input_from_cached_predecessor_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv('FLOWS_STORAGE_DIR', str(tmp_path / 'flows'))
    get_settings.cache_clear()

    client = TestClient(app)
    create_response = client.post(
        '/flows',
        json={
            'name': 'Chain flow',
            'nodes': [
                {
                    'id': 'node-1',
                    'type': 'workflow',
                    'position': {'x': 0, 'y': 0},
                    'data': {
                        'kind': 'microservice',
                        'title': 'A',
                        'description': '',
                        'status': 'idle',
                    },
                },
                {
                    'id': 'node-2',
                    'type': 'workflow',
                    'position': {'x': 100, 'y': 0},
                    'data': {
                        'kind': 'microservice',
                        'title': 'B',
                        'description': '',
                        'status': 'idle',
                    },
                },
            ],
            'edges': [
                {
                    'id': 'edge-1',
                    'source': 'node-1',
                    'target': 'node-2',
                }
            ],
            'version': 1,
        },
    )
    flow_id = create_response.json()['data']['id']

    def fake_request(method, url, **kwargs):
        if url.endswith('/step-1'):
            request = httpx.Request(method, url)
            return httpx.Response(200, json={'slug': 'alpha'}, request=request)

        assert url.endswith('/step-2')
        assert kwargs['json'] == {'slug': 'alpha'}
        request = httpx.Request(method, url)
        return httpx.Response(200, json={'done': True}, request=request)

    monkeypatch.setattr('app.executors.microservice_executor.httpx.request', fake_request)

    first_run_response = client.post(
        '/nodes/node-1/run',
        json={
            'kind': 'microservice',
            'config': {
                'endpoint': 'https://example.com/step-1',
                'method': 'POST',
                'headers': [],
                'payload': '{}',
            },
            'context': {'flowId': flow_id},
        },
    )

    assert first_run_response.status_code == 200

    second_run_response = client.post(
        '/nodes/node-2/run',
        json={
            'kind': 'microservice',
            'config': {
                'endpoint': 'https://example.com/step-2',
                'method': 'POST',
                'headers': [],
                'payload': '{"slug": "{{input.slug}}"}',
            },
            'context': {'flowId': flow_id},
        },
    )

    assert second_run_response.status_code == 200

    flow_response = client.get(f'/flows/{flow_id}')
    nodes = flow_response.json()['data']['nodes']
    node_1 = next(node for node in nodes if node['id'] == 'node-1')
    node_2 = next(node for node in nodes if node['id'] == 'node-2')

    assert node_1['data']['output'] == {'slug': 'alpha'}
    assert node_2['data']['output'] == {'done': True}

    get_settings.cache_clear()