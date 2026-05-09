import json
import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "models.json"

# Hardcoded fallback catalog. If config/models.json is missing or malformed,
# we use this so the app keeps working.
FALLBACK_CATALOG: dict[str, dict] = {
    "anthropic": {
        "label": "Anthropic",
        "secret_key": "anthropic_api_key",
        "auth": "api_key",
        "supports_base_url": False,
        "structured_output": "tool_use",
        "default_model": "claude-sonnet-4-6",
        "models": ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5"],
    },
    "openai": {
        "label": "OpenAI",
        "secret_key": "openai_api_key",
        "auth": "api_key",
        "supports_base_url": True,
        "structured_output": "json_schema",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "o1-mini"],
    },
    "gemini": {
        "label": "Google Gemini",
        "secret_key": "gemini_api_key",
        "auth": "api_key",
        "supports_base_url": False,
        "structured_output": "response_schema",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro"],
    },
    "github_models": {
        "label": "GitHub Models (PAT)",
        "secret_key": "github_token",
        "auth": "api_key",
        "supports_base_url": False,
        "structured_output": "json_schema",
        "default_model": "openai/gpt-4o-mini",
        "models": ["openai/gpt-4o", "openai/gpt-4o-mini"],
    },
    "copilot_models": {
        "label": "GitHub Models (gh auth)",
        "secret_key": None,
        "auth": "gh_cli",
        "supports_base_url": False,
        "structured_output": "json_schema",
        "default_model": "openai/gpt-4o-mini",
        "models": [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-5",
            "openai/gpt-5-chat",
            "openai/gpt-5-mini",
            "openai/gpt-5-nano",
        ],
    },
    "copilot_cli": {
        "label": "Copilot CLI (local)",
        "secret_key": None,
        "auth": "external",
        "supports_base_url": False,
        "structured_output": "prompt",
        "default_model": "gpt-5.4",
        "models": [
            "gpt-4.1",
            "gpt-5-mini",
            "gpt-5.2",
            "gpt-5.4",
            "gpt-5.4-mini",
            "claude-sonnet-4.6",
            "claude-haiku-4.5",
        ],
        "extra_fields": ["timeout_seconds"],
    },
}


def load_catalog() -> dict[str, dict]:
    """Load the model catalog from disk. Falls back to FALLBACK_CATALOG."""
    if not CONFIG_PATH.exists():
        return FALLBACK_CATALOG
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        providers = raw.get("providers")
        if not isinstance(providers, dict) or not providers:
            raise ValueError("'providers' must be a non-empty object")
        return providers
    except (json.JSONDecodeError, ValueError, OSError) as e:
        logger.warning("Could not load %s, using fallback catalog: %s", CONFIG_PATH, e)
        return FALLBACK_CATALOG


# Public catalog. Reload happens on every settings/providers GET so editing
# the file doesn't require a restart.
PROVIDERS = load_catalog()


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
    output_schema: dict | None = None,
) -> LLMResponse:
    """Dispatch to the right provider implementation.

    `output_schema` (when set) is a JSON Schema; providers use their native
    structured-output mode. `json_mode=True` without schema means "any JSON".
    """
    catalog = load_catalog()
    spec = catalog.get(provider)
    if spec is None:
        raise ValueError(f"Unknown provider: {provider}")

    from .anthropic_client import call_anthropic
    from .gemini_client import call_gemini
    from .github_models_client import call_github_models
    from .openai_client import call_openai

    if provider == "anthropic":
        return call_anthropic(db, model, system, user, json_mode, output_schema)
    if provider == "openai":
        return call_openai(db, model, system, user, json_mode, output_schema)
    if provider == "gemini":
        return call_gemini(db, model, system, user, json_mode, output_schema)
    if provider == "github_models":
        return call_github_models(db, model, system, user, json_mode, output_schema)
    if provider == "azure_openai":
        from .azure_openai_client import call_azure_openai

        return call_azure_openai(db, model, system, user, json_mode, output_schema)
    if provider == "copilot_models":
        from .copilot_models_client import call_copilot_models

        return call_copilot_models(db, model, system, user, json_mode, output_schema)
    if provider == "copilot_cli":
        from .copilot_cli_client import call_copilot_cli

        return call_copilot_cli(db, model, system, user, json_mode, output_schema)
    if provider == "cli_subprocess":
        from .cli_subprocess_client import call_cli_subprocess

        return call_cli_subprocess(db, model, system, user, json_mode, output_schema)
    if provider == "openai_compat":
        from .openai_compat_client import call_openai_compat

        return call_openai_compat(db, model, system, user, json_mode, output_schema)

    raise ValueError(f"Provider has no implementation: {provider}")


def _get_secret(db: Session, key: str) -> str:
    from ..crypto import decrypt
    from ..models import Setting

    row = db.get(Setting, key)
    if not row or not row.value_encrypted:
        raise RuntimeError(
            f"Missing credential '{key}'. Configure it in the Settings panel."
        )
    return decrypt(row.value_encrypted)


def _get_optional_setting(db: Session, key: str) -> str | None:
    """Return a setting if present (decrypted), else None. No exception."""
    from ..crypto import decrypt
    from ..models import Setting

    row = db.get(Setting, key)
    if not row or not row.value_encrypted:
        return None
    try:
        return decrypt(row.value_encrypted)
    except Exception:  # noqa: BLE001
        return None
