from sqlalchemy.orm import Session

from .base import LLMResponse, _get_optional_setting
from .openai_client import _call_openai_compatible


def call_openai_compat(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """Generic OpenAI-compatible endpoint.

    Settings:
      - openai_compat_api_key (secret; can be a dummy if your endpoint doesn't auth)
      - openai_compat__base_url (e.g. http://localhost:11434/v1 for Ollama)

    Use this for Ollama, vLLM, LiteLLM, any internal gateway exposing the
    /v1/chat/completions OpenAI-compatible API.
    """
    base_url = _get_optional_setting(db, "openai_compat__base_url")
    if not base_url:
        raise RuntimeError(
            "openai_compat provider requires 'openai_compat__base_url' in Settings."
        )
    resp = _call_openai_compatible(
        db=db,
        provider="openai_compat",
        secret_key="openai_compat_api_key",
        base_url=base_url,
        model=model,
        system=system,
        user=user,
        json_mode=json_mode,
        output_schema=output_schema,
    )
    return LLMResponse(text=resp.text, provider="openai_compat", model=model)
