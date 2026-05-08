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