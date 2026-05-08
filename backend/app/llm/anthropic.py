from typing import Any

from anthropic import Anthropic

from app.core.settings import get_settings


def get_anthropic_client() -> Anthropic:
    settings = get_settings()

    if not settings.anthropic_api_key:
        raise ValueError('ANTHROPIC_API_KEY is required to run agent nodes.')

    return Anthropic(api_key=settings.anthropic_api_key)


def build_structured_output_tool(input_schema: dict) -> dict:
    return {
        'name': 'submit_structured_output',
        'description': 'Return the final structured output for the workflow node.',
        'input_schema': input_schema,
    }


def run_anthropic_structured_output(
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_schema: dict[str, Any],
) -> dict[str, Any]:
    client = get_anthropic_client()
    output_tool = build_structured_output_tool(input_schema)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt or None,
        messages=[
            {
                'role': 'user',
                'content': user_prompt,
            }
        ],
        tool_choice={'type': 'tool', 'name': output_tool['name']},
        tools=[output_tool],
    )

    return extract_tool_input(response.content, output_tool['name'])


def extract_tool_input(content_blocks: list[Any], tool_name: str) -> dict[str, Any]:
    for block in content_blocks:
        if getattr(block, 'type', None) == 'tool_use' and getattr(block, 'name', None) == tool_name:
            return getattr(block, 'input', {})

    raise ValueError('Anthropic response did not include the structured output tool payload.')