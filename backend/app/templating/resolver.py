import json
import os
import re
from typing import Any

from app.core.file_storage import get_uploads_storage_path

TEMPLATE_PATTERN = re.compile(r'{{\s*([^{}]+?)\s*}}')
FULL_TEMPLATE_PATTERN = re.compile(r'^{{\s*([^{}]+?)\s*}}$')


class TemplateResolutionError(Exception):
    pass


def resolve_template_value(
    value: Any,
    *,
    flow_id: str | None = None,
    input_data: Any = None,
) -> Any:
    if isinstance(value, dict):
        return {
            key: resolve_template_value(item, flow_id=flow_id, input_data=input_data)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            resolve_template_value(item, flow_id=flow_id, input_data=input_data)
            for item in value
        ]

    if not isinstance(value, str):
        return value

    full_match = FULL_TEMPLATE_PATTERN.fullmatch(value)
    if full_match:
        return _resolve_expression(full_match.group(1), flow_id=flow_id, input_data=input_data)

    return TEMPLATE_PATTERN.sub(
        lambda match: _stringify_value(
            _resolve_expression(match.group(1), flow_id=flow_id, input_data=input_data),
        ),
        value,
    )


def _resolve_expression(expression: str, *, flow_id: str | None, input_data: Any) -> Any:
    normalized = expression.strip()

    if normalized.startswith('env.'):
        env_key = normalized.removeprefix('env.').strip()
        if not env_key:
            raise TemplateResolutionError('Environment variable placeholder cannot be empty.')

        env_value = os.getenv(env_key)
        if env_value is None:
            raise TemplateResolutionError(f'Environment variable "{env_key}" is not defined.')

        return env_value

    if normalized.startswith('input.'):
        input_path = normalized.removeprefix('input.').strip()
        if not input_path:
            raise TemplateResolutionError('Input placeholder cannot be empty.')

        return _resolve_input_path(input_data, input_path, normalized)

    if normalized.startswith('archivos.'):
        variable_name = normalized.removeprefix('archivos.').strip()
        if not variable_name:
            raise TemplateResolutionError('File placeholder cannot be empty.')

        return _read_uploaded_file_text(flow_id, variable_name)

    raise TemplateResolutionError(f'Unsupported template placeholder "{normalized}".')


def _resolve_input_path(input_data: Any, input_path: str, placeholder: str) -> Any:
    if input_data is None:
        raise TemplateResolutionError(
            f'No input data is available for placeholder "{placeholder}".',
        )

    current = input_data
    for segment in input_path.split('.'):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
            continue

        raise TemplateResolutionError(
            f'Input placeholder "{placeholder}" could not be resolved.',
        )

    return current


def _read_uploaded_file_text(flow_id: str | None, variable_name: str) -> str:
    if not flow_id:
        raise TemplateResolutionError(
            f'Flow id is required to resolve file placeholder "archivos.{variable_name}".',
        )

    flow_uploads_path = get_uploads_storage_path() / flow_id
    if not flow_uploads_path.exists():
        raise TemplateResolutionError(f'No uploaded files exist for flow "{flow_id}".')

    for metadata_path in flow_uploads_path.glob('*/metadata.json'):
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        if metadata.get('variableName') == variable_name:
            parsed_text_path = metadata_path.parent / 'parsed.txt'
            if not parsed_text_path.exists():
                raise TemplateResolutionError(
                    f'Parsed text is missing for file placeholder "archivos.{variable_name}".',
                )

            return parsed_text_path.read_text(encoding='utf-8')

    raise TemplateResolutionError(
        f'File placeholder "archivos.{variable_name}" could not be resolved.',
    )


def _stringify_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)