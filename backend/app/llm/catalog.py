from pathlib import Path

import yaml

from app.core.settings import get_settings
from app.models.settings import ModelOption, ProviderId

KNOWN_PROVIDERS: tuple[ProviderId, ...] = ('anthropic', 'openai', 'gemini')


def list_model_options() -> list[ModelOption]:
    config_path = get_models_config_path()
    if not config_path.exists():
        return []

    raw_document = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
    providers_section = raw_document.get('providers', {})
    if not isinstance(providers_section, dict):
        return []

    options: list[ModelOption] = []
    for provider in KNOWN_PROVIDERS:
        raw_entries = providers_section.get(provider, [])
        if not isinstance(raw_entries, list):
            continue

        for entry in raw_entries:
            if isinstance(entry, str):
                model_id = entry.strip()
                if model_id:
                    options.append(ModelOption(id=model_id, label=model_id, provider=provider))
                continue

            if isinstance(entry, dict):
                model_id = str(entry.get('id', '')).strip()
                label = str(entry.get('label', '')).strip() or model_id
                if model_id:
                    options.append(ModelOption(id=model_id, label=label, provider=provider))

    return options


def get_model_provider(model_id: str) -> ProviderId:
    normalized_model_id = model_id.strip()
    for option in list_model_options():
        if option.id == normalized_model_id:
            return option.provider

    raise ValueError(
        'Selected model was not found in backend/config/models.yaml. '
        'Update the catalog before running the agent.',
    )


def get_models_config_path() -> Path:
    settings = get_settings()
    config_path = Path(settings.models_config_path)
    if not config_path.is_absolute():
        config_path = Path(__file__).resolve().parents[2] / config_path

    return config_path