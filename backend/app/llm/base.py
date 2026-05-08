from dataclasses import dataclass

from sqlalchemy.orm import Session


PROVIDERS = {
    "anthropic": {
        "label": "Anthropic",
        "default_model": "claude-sonnet-4-6",
        "models": [
            "claude-sonnet-4-6",
            "claude-opus-4-7",
            "claude-haiku-4-5",
        ],
        "secret_key": "anthropic_api_key",
    },
    "openai": {
        "label": "OpenAI",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "o1-mini"],
        "secret_key": "openai_api_key",
    },
    "gemini": {
        "label": "Google Gemini",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro"],
        "secret_key": "gemini_api_key",
    },
    "github_models": {
        "label": "GitHub Models",
        "default_model": "openai/gpt-4o-mini",
        "models": [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "meta/Meta-Llama-3.1-70B-Instruct",
            "mistral-ai/Mistral-Nemo",
        ],
        "secret_key": "github_token",
    },
}


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str


def call_llm(
    db: Session,
    provider: str,
    model: str,
    system: str,
    user: str,
    json_mode: bool = False,
) -> LLMResponse:
    """Dispatch to the right provider implementation."""
    from .anthropic_client import call_anthropic
    from .gemini_client import call_gemini
    from .github_models_client import call_github_models
    from .openai_client import call_openai

    if provider == "anthropic":
        return call_anthropic(db, model, system, user, json_mode)
    if provider == "openai":
        return call_openai(db, model, system, user, json_mode)
    if provider == "gemini":
        return call_gemini(db, model, system, user, json_mode)
    if provider == "github_models":
        return call_github_models(db, model, system, user, json_mode)
    raise ValueError(f"Unknown provider: {provider}")


def _get_secret(db: Session, key: str) -> str:
    from ..crypto import decrypt
    from ..models import Setting

    row = db.get(Setting, key)
    if not row or not row.value_encrypted:
        raise RuntimeError(
            f"Missing credential '{key}'. Configure it in the Settings panel."
        )
    return decrypt(row.value_encrypted)
