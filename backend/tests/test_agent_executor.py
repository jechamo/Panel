from types import SimpleNamespace

from app.executors.agent_executor import run_agent_with_context
from app.models.node import AgentNodeConfig, NodeExecutionContext


def test_run_agent_builds_validated_structured_output(monkeypatch) -> None:
    captured_kwargs = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
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
    monkeypatch.setenv('AGENT_SUBJECT', 'release notes')
    monkeypatch.setattr(
        'app.templating.resolver._read_uploaded_file_text',
        lambda flow_id, variable_name: 'uploaded report text',
    )

    result = run_agent_with_context(
        AgentNodeConfig(
            model='manual-model-id',
            outputFields=[
                {'id': 'field-1', 'name': 'summary', 'description': 'Short summary'},
                {'id': 'field-2', 'name': 'next_step', 'description': 'Recommended next action'},
            ],
            systemPrompt='Be concise for {{input.audience}}.',
            userPrompt='Summarize {{env.AGENT_SUBJECT}} from {{archivos.report}}.',
        ),
        NodeExecutionContext(
            flowId='flow-1',
            input={'audience': 'ops'},
        ),
    )

    assert result.output == {
        'summary': 'Done',
        'next_step': 'Notify the team',
    }
    assert result.status_code == 200
    assert captured_kwargs['system'] == 'Be concise for ops.'
    assert captured_kwargs['messages'][0]['content'] == (
        'Summarize release notes from uploaded report text.'
    )