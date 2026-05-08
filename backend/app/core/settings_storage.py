import os
from pathlib import Path

from app.core.settings import get_settings

PROVIDER_ENV_KEYS = {
    'anthropic': 'ANTHROPIC_API_KEY',
    'openai': 'OPENAI_API_KEY',
    'gemini': 'GEMINI_API_KEY',
}


def get_env_file_path() -> Path:
    configured_path = os.getenv('PANEL_ENV_FILE')
    if configured_path:
        return Path(configured_path)

    return Path(__file__).resolve().parents[2] / '.env'


def persist_api_keys(updates: dict[str, str | None]) -> None:
    env_file_path = get_env_file_path()
    env_file_path.parent.mkdir(parents=True, exist_ok=True)

    existing_lines = (
        env_file_path.read_text(encoding='utf-8').splitlines()
        if env_file_path.exists()
        else []
    )
    next_lines: list[str] = []
    seen_keys: set[str] = set()

    for line in existing_lines:
        if '=' not in line or line.lstrip().startswith('#'):
            next_lines.append(line)
            continue

        key, _, current_value = line.partition('=')
        normalized_key = key.strip()
        if normalized_key not in updates:
            next_lines.append(line)
            continue

        next_value = updates[normalized_key] or ''
        next_lines.append(f'{normalized_key}={next_value}')
        seen_keys.add(normalized_key)

    for key, value in updates.items():
        if key in seen_keys:
            continue

        next_lines.append(f'{key}={value or ""}')

    env_file_path.write_text('\n'.join(next_lines).rstrip() + '\n', encoding='utf-8')

    for key, value in updates.items():
        os.environ[key] = value or ''

    get_settings.cache_clear()