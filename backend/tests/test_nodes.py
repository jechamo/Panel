import httpx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_run_microservice_node_returns_json(monkeypatch) -> None:
    monkeypatch.setenv('MICROSERVICE_TOKEN', 'demo-secret')

    def fake_request(*args, **kwargs):
        assert args[1] == 'https://example.com/alpha'
        assert kwargs['headers'] == {'Authorization': 'Bearer demo-secret'}
        assert kwargs['json'] == {'foo': 'alpha', 'count': 3}
        request = httpx.Request('POST', 'https://example.com/api')
        return httpx.Response(200, json={'ok': True, 'echo': {'foo': 'bar'}}, request=request)

    monkeypatch.setattr('app.executors.microservice_executor.httpx.request', fake_request)

    response = client.post(
        '/nodes/node-1/run',
        json={
            'kind': 'microservice',
            'config': {
                'endpoint': 'https://example.com/{{input.slug}}',
                'method': 'POST',
                'headers': [
                    {
                        'id': 'header-1',
                        'key': 'Authorization',
                        'value': 'Bearer {{env.MICROSERVICE_TOKEN}}',
                    }
                ],
                'payload': '{"foo": "{{input.slug}}", "count": {{input.count}}}',
            },
            'context': {
                'input': {'slug': 'alpha', 'count': 3},
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['data'] == {
        'output': {'ok': True, 'echo': {'foo': 'bar'}},
        'status_code': 200,
    }