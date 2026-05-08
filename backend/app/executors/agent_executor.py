from app.llm.anthropic import get_anthropic_client
from app.models.node import AgentNodeConfig, NodeRunResult


class AgentExecutionError(Exception):
    pass


def run_agent(config: AgentNodeConfig) -> NodeRunResult:
    if not config.model.strip():
        raise AgentExecutionError('Agent model is required before executing the node.')

    if not config.userPrompt.strip():
        raise AgentExecutionError('User prompt is required before executing the node.')

    try:
        client = get_anthropic_client()
    except ValueError as error:
        raise AgentExecutionError(str(error)) from error

    response = client.messages.create(
        model=config.model,
        max_tokens=1024,
        system=config.systemPrompt or None,
        messages=[
            {
                'role': 'user',
                'content': config.userPrompt,
            }
        ],
    )

    text_output = ''.join(
        block.text for block in response.content if getattr(block, 'type', None) == 'text'
    ).strip()

    if not text_output:
        raise AgentExecutionError('Anthropic response did not include text output.')

    return NodeRunResult(output=text_output, status_code=200)