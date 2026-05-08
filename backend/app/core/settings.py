from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Panel Backend"
    app_version: str = "0.1.0"
    app_env: str = "development"
    anthropic_api_key: str = ""
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    flows_storage_dir: str = "storage/flows"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()