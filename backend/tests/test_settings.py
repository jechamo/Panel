from pathlib import Path

from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import app


def test_settings_api_updates_env_and_exposes_models(
    tmp_path: Path,
    monkeypatch,
) -> None:
    env_file = tmp_path / '.env'
    models_file = tmp_path / 'models.yaml'
    models_file.write_text(
        'providers:\n'
        '  anthropic:\n'
        '    - id: claude-test\n'
        '      label: Claude Test\n'
        '  openai:\n'
        '    - gpt-test\n'
        '  gemini:\n'
        '    - id: gemini-test\n'
        '      label: Gemini Test\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('PANEL_ENV_FILE', str(env_file))
    monkeypatch.setenv('MODELS_CONFIG_PATH', str(models_file))
    get_settings.cache_clear()

    client = TestClient(app)
    initial_response = client.get('/settings')

    assert initial_response.status_code == 200
    initial_payload = initial_response.json()['data']
    assert initial_payload['anthropicConfigured'] is False
    assert [model['provider'] for model in initial_payload['models']] == [
        'anthropic',
        'openai',
        'gemini',
    ]

    update_response = client.put(
        '/settings',
        json={
            'anthropicApiKey': 'anthropic-key',
            'openaiApiKey': 'openai-key',
            'geminiApiKey': 'gemini-key',
        },
    )

    assert update_response.status_code == 200
    updated_payload = update_response.json()['data']
    assert updated_payload['anthropicConfigured'] is True
    assert updated_payload['openaiConfigured'] is True
    assert updated_payload['geminiConfigured'] is True
    assert 'ANTHROPIC_API_KEY=anthropic-key' in env_file.read_text(encoding='utf-8')
    assert 'OPENAI_API_KEY=openai-key' in env_file.read_text(encoding='utf-8')
    assert 'GEMINI_API_KEY=gemini-key' in env_file.read_text(encoding='utf-8')

    get_settings.cache_clear()