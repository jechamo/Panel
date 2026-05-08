import json
from typing import Any

from openai import OpenAI

from app.core.settings import get_settings


def get_openai_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError('OPENAI_API_KEY is required to run agent nodes with OpenAI models.')

    return OpenAI(api_key=settings.openai_api_key)


def run_openai_structured_output(
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_schema: dict[str, Any],
) -> dict[str, Any]:
    client = get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        response_format={
            'type': 'json_schema',
            'json_schema': {
                'name': 'submit_structured_output',
                'schema': input_schema,
                'strict': True,
            },
        },
    )

    message_content = response.choices[0].message.content if response.choices else None
    if not message_content:
        raise ValueError('OpenAI response did not include structured JSON output.')

    return json.loads(message_content)