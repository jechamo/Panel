from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_run_agent_node_returns_text(monkeypatch) -> None:
    class FakeResult:
        output = 'Agent response'
        status_code = 200

        def model_dump(self, mode='json'):
            return {
                'output': self.output,
                'status_code': self.status_code,
            }

    monkeypatch.setattr('app.api.nodes.run_agent', lambda config: FakeResult())

    response = client.post(
        '/nodes/node-agent/run',
        json={
            'kind': 'agent',
            'config': {
                'model': 'manual-model-id',
                'systemPrompt': 'You are a helper.',
                'userPrompt': 'Say hello.',
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['data'] == {
        'output': 'Agent response',
        'status_code': 200,
    }