import json
from pathlib import Path
from uuid import uuid4

from app.core.settings import get_settings
from app.models.flow import FlowCreateRequest, FlowDocument, FlowSummary, FlowUpdateRequest


def get_flows_storage_path() -> Path:
    storage_path = Path(get_settings().flows_storage_dir)
    if not storage_path.is_absolute():
        storage_path = Path(__file__).resolve().parents[2] / storage_path

    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def _flow_file_path(flow_id: str) -> Path:
    return get_flows_storage_path() / f"{flow_id}.json"


def list_flows() -> list[FlowSummary]:
    flows: list[FlowSummary] = []

    for file_path in sorted(get_flows_storage_path().glob('*.json')):
        document = FlowDocument.model_validate_json(file_path.read_text(encoding='utf-8'))
        flows.append(FlowSummary(id=document.id, name=document.name, version=document.version))

    return flows


def create_flow(payload: FlowCreateRequest) -> FlowDocument:
    document = FlowDocument(id=str(uuid4()), **payload.model_dump())
    _write_flow(document)
    return document


def get_flow(flow_id: str) -> FlowDocument | None:
    file_path = _flow_file_path(flow_id)
    if not file_path.exists():
        return None

    return FlowDocument.model_validate_json(file_path.read_text(encoding='utf-8'))


def update_flow(flow_id: str, payload: FlowUpdateRequest) -> FlowDocument | None:
    file_path = _flow_file_path(flow_id)
    if not file_path.exists():
        return None

    document = FlowDocument(id=flow_id, **payload.model_dump(exclude={'id'}))
    _write_flow(document)
    return document


def get_predecessor_node_id(flow_id: str, node_id: str) -> str | None:
    document = get_flow(flow_id)
    if document is None:
        return None

    incoming_edges = [edge for edge in document.edges if edge.get('target') == node_id]
    if not incoming_edges:
        return None

    if len(incoming_edges) > 1:
        raise ValueError('Only one predecessor edge is supported in this phase.')

    predecessor_id = incoming_edges[0].get('source')
    return predecessor_id if isinstance(predecessor_id, str) else None


def get_node_output(flow_id: str, node_id: str):
    document = get_flow(flow_id)
    if document is None:
        return None

    node = _find_node(document, node_id)
    if node is None:
        return None

    return node.get('data', {}).get('output')


def set_node_runtime_state(
    flow_id: str,
    node_id: str,
    *,
    status: str,
    output,
    last_error,
) -> FlowDocument | None:
    document = get_flow(flow_id)
    if document is None:
        return None

    node = _find_node(document, node_id)
    if node is None:
        return None

    node_data = node.setdefault('data', {})
    node_data['status'] = status
    node_data['output'] = output
    node_data['lastError'] = last_error

    _write_flow(document)
    return document


def delete_flow(flow_id: str) -> bool:
    file_path = _flow_file_path(flow_id)
    if not file_path.exists():
        return False

    file_path.unlink()
    return True


def _write_flow(document: FlowDocument) -> None:
    _flow_file_path(document.id).write_text(
        json.dumps(document.model_dump(mode='json'), indent=2),
        encoding='utf-8',
    )


def _find_node(document: FlowDocument, node_id: str) -> dict | None:
    for node in document.nodes:
        if node.get('id') == node_id:
            return node

    return None