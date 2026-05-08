from fastapi import APIRouter

from app.core.responses import success_response
from app.core.settings import get_settings
from app.core.settings_storage import PROVIDER_ENV_KEYS, persist_api_keys
from app.llm.catalog import list_model_options
from app.models.settings import SettingsSnapshot, SettingsUpdateRequest

router = APIRouter(prefix='/settings', tags=['settings'])


@router.get('')
def read_settings():
    return success_response(build_settings_snapshot().model_dump(mode='json'))


@router.put('')
def update_settings(payload: SettingsUpdateRequest):
    persist_api_keys(
        {
            PROVIDER_ENV_KEYS['anthropic']: payload.anthropicApiKey,
            PROVIDER_ENV_KEYS['openai']: payload.openaiApiKey,
            PROVIDER_ENV_KEYS['gemini']: payload.geminiApiKey,
        }
    )

    return success_response(build_settings_snapshot().model_dump(mode='json'))


def build_settings_snapshot() -> SettingsSnapshot:
    settings = get_settings()

    return SettingsSnapshot(
        anthropicConfigured=bool(settings.anthropic_api_key),
        openaiConfigured=bool(settings.openai_api_key),
        geminiConfigured=bool(settings.gemini_api_key),
        models=list_model_options(),
    )