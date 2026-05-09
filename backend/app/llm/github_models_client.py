from sqlalchemy.orm import Session

from .base import LLMResponse
from .openai_client import _call_openai_compatible

_GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"


def call_github_models(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """GitHub Models exposes an OpenAI-compatible API at the inference endpoint."""
    resp = _call_openai_compatible(
        db=db,
        provider="github_models",
        secret_key="github_token",
        base_url=_GITHUB_MODELS_BASE_URL,
        model=model,
        system=system,
        user=user,
        json_mode=json_mode,
        output_schema=output_schema,
    )
    return LLMResponse(text=resp.text, provider="github_models", model=model)
