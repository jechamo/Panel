from anthropic import Anthropic

from app.core.settings import get_settings


def get_anthropic_client() -> Anthropic:
    settings = get_settings()

    if not settings.anthropic_api_key:
        raise ValueError('ANTHROPIC_API_KEY is required to run agent nodes.')

    return Anthropic(api_key=settings.anthropic_api_key)