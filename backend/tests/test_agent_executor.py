from types import SimpleNamespace

from app.executors.agent_executor import run_agent
from app.models.node import AgentNodeConfig


def test_run_agent_builds_validated_structured_output(monkeypatch) -> None:
    class FakeMessages:
        def create(self, **kwargs):
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type='tool_use',
                        name='submit_structured_output',
                        input={
                            'summary': 'Done',
                            'next_step': 'Notify the team',
                        },
                    )
                ]
            )

    class FakeClient:
        messages = FakeMessages()

    monkeypatch.setattr('app.executors.agent_executor.get_anthropic_client', lambda: FakeClient())

    result = run_agent(
        AgentNodeConfig(
            model='manual-model-id',
            outputFields=[
                {'id': 'field-1', 'name': 'summary', 'description': 'Short summary'},
                {'id': 'field-2', 'name': 'next_step', 'description': 'Recommended next action'},
            ],
            systemPrompt='Be concise.',
            userPrompt='Summarize the task.',
        )
    )

    assert result.output == {
        'summary': 'Done',
        'next_step': 'Notify the team',
    }
    assert result.status_code == 200