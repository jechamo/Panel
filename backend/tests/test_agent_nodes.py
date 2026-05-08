from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_run_agent_node_returns_text(monkeypatch) -> None:
    class FakeResult:
        output = {
            'summary': 'Agent response',
            'next_step': 'Send the report',
        }
        status_code = 200

        def model_dump(self, mode='json'):
            return {
                'output': self.output,
                'status_code': self.status_code,
            }

    monkeypatch.setattr(
        'app.api.nodes.run_agent_with_context',
        lambda config, context: FakeResult(),
    )

    response = client.post(
        '/nodes/node-agent/run',
        json={
            'kind': 'agent',
            'config': {
                'model': 'manual-model-id',
                'outputFields': [
                    {'id': 'field-1', 'name': 'summary', 'description': 'Short summary'},
                    {'id': 'field-2', 'name': 'next_step', 'description': 'Recommended next step'},
                ],
                'systemPrompt': 'You are a helper.',
                'userPrompt': 'Say hello.',
            },
            'context': {
                'flowId': 'flow-123',
                'input': {'topic': 'hello'},
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['data'] == {
        'output': {
            'summary': 'Agent response',
            'next_step': 'Send the report',
        },
        'status_code': 200,
    }