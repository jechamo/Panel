from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app


def test_node_run_persists_log_and_lists_it(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv('FLOWS_STORAGE_DIR', str(tmp_path / 'flows'))
    monkeypatch.setenv('RUNS_STORAGE_DIR', str(tmp_path / 'runs'))
    get_settings.cache_clear()

    client = TestClient(app)
    create_response = client.post(
        '/flows',
        json={
            'name': 'Run log flow',
            'nodes': [
                {
                    'id': 'node-1',
                    'type': 'workflow',
                    'position': {'x': 0, 'y': 0},
                    'data': {
                        'kind': 'microservice',
                        'title': 'Node',
                        'description': '',
                        'status': 'idle',
                        'lastError': None,
                        'output': None,
                        'config': {
                            'endpoint': 'https://example.com/demo',
                            'method': 'POST',
                            'headers': [],
                            'payload': '{"foo": "bar"}',
                        },
                    },
                }
            ],
            'edges': [],
            'version': 1,
        },
    )
    flow_id = create_response.json()['data']['id']

    def fake_request(*args, **kwargs):
        request = httpx.Request('POST', 'https://example.com/demo')
        return httpx.Response(200, json={'ok': True}, request=request)

    monkeypatch.setattr('app.executors.microservice_executor.httpx.request', fake_request)

    run_response = client.post(
        '/nodes/node-1/run',
        json={
            'kind': 'microservice',
            'config': {
                'endpoint': 'https://example.com/demo',
                'method': 'POST',
                'headers': [],
                'payload': '{"foo": "bar"}',
            },
            'context': {'flowId': flow_id, 'input': {'foo': 'bar'}},
        },
    )

    assert run_response.status_code == 200

    runs_response = client.get(f'/runs?flowId={flow_id}&nodeId=node-1')

    assert runs_response.status_code == 200
    runs = runs_response.json()['data']
    assert len(runs) == 1
    assert runs[0]['nodeId'] == 'node-1'
    assert runs[0]['status'] == 'success'
    assert runs[0]['input'] == {'foo': 'bar'}
    assert runs[0]['output'] == {'ok': True}
    assert runs[0]['error'] is None

    get_settings.cache_clear()