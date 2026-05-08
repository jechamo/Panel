from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app


def test_run_flow_executes_nodes_in_topological_order(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv('FLOWS_STORAGE_DIR', str(tmp_path))
    get_settings.cache_clear()

    client = TestClient(app)
    create_response = client.post(
        '/flows',
        json={
            'name': 'Demo flow',
            'nodes': [
                {
                    'id': 'node-1',
                    'type': 'workflow',
                    'position': {'x': 0, 'y': 0},
                    'data': {
                        'kind': 'microservice',
                        'title': 'Source',
                        'description': '',
                        'status': 'idle',
                        'lastError': None,
                        'output': None,
                        'config': {
                            'endpoint': 'https://example.com/source',
                            'method': 'POST',
                            'headers': [],
                            'payload': '{}',
                        },
                    },
                },
                {
                    'id': 'node-2',
                    'type': 'workflow',
                    'position': {'x': 120, 'y': 0},
                    'data': {
                        'kind': 'microservice',
                        'title': 'Follower',
                        'description': '',
                        'status': 'idle',
                        'lastError': None,
                        'output': None,
                        'config': {
                            'endpoint': 'https://example.com/follower',
                            'method': 'POST',
                            'headers': [],
                            'payload': '{"slug": "{{input.slug}}"}',
                        },
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
    request_order: list[str] = []

    def fake_request(method, url, **kwargs):
        request_order.append(url)
        request = httpx.Request(method, url)

        if url.endswith('/source'):
            return httpx.Response(200, json={'slug': 'alpha'}, request=request)

        assert kwargs['json'] == {'slug': 'alpha'}
        return httpx.Response(200, json={'done': True}, request=request)

    monkeypatch.setattr('app.executors.microservice_executor.httpx.request', fake_request)

    run_response = client.post(f'/flows/{flow_id}/run')

    assert run_response.status_code == 200
    assert request_order == [
        'https://example.com/source',
        'https://example.com/follower',
    ]
    returned_nodes = run_response.json()['data']['nodes']
    node_1 = next(node for node in returned_nodes if node['id'] == 'node-1')
    node_2 = next(node for node in returned_nodes if node['id'] == 'node-2')
    assert node_1['data']['status'] == 'success'
    assert node_1['data']['output'] == {'slug': 'alpha'}
    assert node_2['data']['status'] == 'success'
    assert node_2['data']['output'] == {'done': True}

    get_settings.cache_clear()