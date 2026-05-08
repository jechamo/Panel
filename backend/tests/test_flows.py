from pathlib import Path

from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app


def test_flow_crud_cycle(tmp_path: Path, monkeypatch) -> None:
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
                    'position': {'x': 120, 'y': 140},
                    'data': {
                        'kind': 'agent',
                        'title': 'Agente',
                        'description': 'Demo',
                        'status': 'idle',
                    },
                }
            ],
            'edges': [],
            'version': 1,
        },
    )

    assert create_response.status_code == 201
    created_flow = create_response.json()['data']
    flow_id = created_flow['id']
    assert (tmp_path / f'{flow_id}.json').exists()

    list_response = client.get('/flows')
    assert list_response.status_code == 200
    assert list_response.json()['data'] == [
        {
            'id': flow_id,
            'name': 'Demo flow',
            'version': 1,
        }
    ]

    get_response = client.get(f'/flows/{flow_id}')
    assert get_response.status_code == 200
    assert get_response.json()['data']['name'] == 'Demo flow'

    update_response = client.put(
        f'/flows/{flow_id}',
        json={
            'id': flow_id,
            'name': 'Updated flow',
            'nodes': created_flow['nodes'],
            'edges': [
                {
                    'id': 'edge-1',
                    'source': 'node-1',
                    'target': 'node-2',
                    'animated': True,
                }
            ],
            'version': 1,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()['data']['name'] == 'Updated flow'
    assert update_response.json()['data']['edges'][0]['id'] == 'edge-1'

    delete_response = client.delete(f'/flows/{flow_id}')
    assert delete_response.status_code == 200
    assert delete_response.json()['data'] == {'deleted': True, 'id': flow_id}

    missing_response = client.get(f'/flows/{flow_id}')
    assert missing_response.status_code == 404
    assert missing_response.json()['error']['code'] == 'flow_not_found'

    get_settings.cache_clear()