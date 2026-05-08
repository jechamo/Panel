from typing import Literal

from pydantic import BaseModel

ProviderId = Literal['anthropic', 'openai', 'gemini']


class ModelOption(BaseModel):
    id: str
    label: str
    provider: ProviderId


class SettingsSnapshot(BaseModel):
    anthropicConfigured: bool
    openaiConfigured: bool
    geminiConfigured: bool
    models: list[ModelOption]


class SettingsUpdateRequest(BaseModel):
    anthropicApiKey: str | None = None
    openaiApiKey: str | None = None
    geminiApiKey: str | None = None