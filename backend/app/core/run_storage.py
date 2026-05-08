import json
from pathlib import Path
from uuid import uuid4

from app.core.settings import get_settings
from app.models.run import NodeRunLog


def get_runs_storage_path() -> Path:
    storage_path = Path(get_settings().runs_storage_dir)
    if not storage_path.is_absolute():
        storage_path = Path(__file__).resolve().parents[2] / storage_path

    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def create_node_run_log(payload: NodeRunLog) -> NodeRunLog:
    document = payload.model_copy(update={'id': payload.id or str(uuid4())})
    _run_file_path(document.id).write_text(
        json.dumps(document.model_dump(mode='json'), indent=2),
        encoding='utf-8',
    )
    return document


def list_node_run_logs(flow_id: str | None, node_id: str, limit: int = 10) -> list[NodeRunLog]:
    matching_logs: list[NodeRunLog] = []

    for file_path in sorted(get_runs_storage_path().glob('*.json'), reverse=True):
        document = NodeRunLog.model_validate_json(file_path.read_text(encoding='utf-8'))
        if document.nodeId != node_id:
            continue
        if flow_id is not None and document.flowId != flow_id:
            continue

        matching_logs.append(document)
        if len(matching_logs) >= limit:
            break

    return sorted(matching_logs, key=lambda item: item.startedAt, reverse=True)


def _run_file_path(run_id: str) -> Path:
    return get_runs_storage_path() / f'{run_id}.json'