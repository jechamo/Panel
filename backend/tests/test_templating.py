import json
from pathlib import Path

from app.core.settings import get_settings
from app.templating.resolver import resolve_template_value


def test_resolve_template_value_supports_input_and_env(monkeypatch) -> None:
    monkeypatch.setenv('API_TOKEN', 'secret-token')

    resolved = resolve_template_value(
        {
            'header': 'Bearer {{env.API_TOKEN}}',
            'count': '{{input.meta.count}}',
            'title': 'Hello {{input.user.name}}',
        },
        input_data={'user': {'name': 'Ada'}, 'meta': {'count': 2}},
    )

    assert resolved == {
        'header': 'Bearer secret-token',
        'count': 2,
        'title': 'Hello Ada',
    }


def test_resolve_template_value_supports_uploaded_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv('UPLOADS_STORAGE_DIR', str(tmp_path))
    get_settings.cache_clear()

    file_dir = tmp_path / 'flow-1' / 'file-1'
    file_dir.mkdir(parents=True)
    (file_dir / 'metadata.json').write_text(
        json.dumps({'variableName': 'report'}),
        encoding='utf-8',
    )
    (file_dir / 'parsed.txt').write_text('uploaded report text', encoding='utf-8')

    resolved = resolve_template_value(
        'Resumen: {{archivos.report}}',
        flow_id='flow-1',
    )

    assert resolved == 'Resumen: uploaded report text'

    get_settings.cache_clear()