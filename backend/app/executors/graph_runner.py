from typing import Any

import httpx
from pydantic import ValidationError

from app.core.flow_storage import (
    get_flow,
    get_node_output,
    set_node_runtime_state,
)
from app.executors.agent_executor import AgentExecutionError, run_agent_with_context
from app.executors.microservice_executor import (
    MicroserviceExecutionError,
    run_microservice_with_context,
)
from app.models.flow import FlowDocument
from app.models.node import AgentNodeConfig, MicroserviceNodeConfig, NodeExecutionContext


class GraphRunError(Exception):
    pass


def run_flow_graph(flow_id: str) -> FlowDocument:
    document = get_flow(flow_id)
    if document is None:
        raise GraphRunError(f'Flow {flow_id} was not found.')

    ordered_node_ids = topological_sort(document)

    for node_id in ordered_node_ids:
        node = _find_node(document, node_id)
        if node is None:
            raise GraphRunError(f'Node {node_id} was not found in flow {flow_id}.')

        node_data = node.get('data', {})
        node_kind = node_data.get('kind')
        raw_config = node_data.get('config') or {}
        predecessor_output = _get_predecessor_output(document, node_id)

        set_node_runtime_state(
            flow_id,
            node_id,
            status='running',
            output=node_data.get('output'),
            last_error=None,
        )

        try:
            result = _run_single_node(
                node_kind,
                raw_config,
                NodeExecutionContext(flowId=flow_id, input=predecessor_output),
            )
        except (GraphRunError, AgentExecutionError, MicroserviceExecutionError) as error:
            set_node_runtime_state(
                flow_id,
                node_id,
                status='error',
                output=None,
                last_error=str(error),
            )
            raise GraphRunError(str(error)) from error
        except httpx.HTTPStatusError as error:
            set_node_runtime_state(
                flow_id,
                node_id,
                status='error',
                output=None,
                last_error=f'Microservice returned status {error.response.status_code}.',
            )
            raise GraphRunError(
                f'Microservice returned status {error.response.status_code}.',
            ) from error
        except httpx.HTTPError as error:
            set_node_runtime_state(
                flow_id,
                node_id,
                status='error',
                output=None,
                last_error=str(error),
            )
            raise GraphRunError(str(error)) from error

        set_node_runtime_state(
            flow_id,
            node_id,
            status='success',
            output=result.output,
            last_error=None,
        )

    refreshed_document = get_flow(flow_id)
    if refreshed_document is None:
        raise GraphRunError(f'Flow {flow_id} was not found after execution.')

    return refreshed_document


def topological_sort(document: FlowDocument) -> list[str]:
    node_ids = [node.get('id') for node in document.nodes if isinstance(node.get('id'), str)]
    in_degree = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}

    for edge in document.edges:
        source = edge.get('source')
        target = edge.get('target')

        if not isinstance(source, str) or not isinstance(target, str):
            raise GraphRunError('Flow edges must include string source and target node ids.')

        if source not in adjacency or target not in in_degree:
            raise GraphRunError('Flow contains edges that reference missing nodes.')

        adjacency[source].append(target)
        in_degree[target] += 1

    queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
    ordered: list[str] = []

    while queue:
        node_id = queue.pop(0)
        ordered.append(node_id)

        for child_id in adjacency[node_id]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0:
                queue.append(child_id)

    if len(ordered) != len(node_ids):
        raise GraphRunError('Flow graph contains a cycle and cannot be executed.')

    return ordered


def _find_node(document: FlowDocument, node_id: str) -> dict[str, Any] | None:
    for node in document.nodes:
        if node.get('id') == node_id:
            return node

    return None


def _get_predecessor_output(document: FlowDocument, node_id: str) -> Any:
    incoming_edges = [edge for edge in document.edges if edge.get('target') == node_id]
    if not incoming_edges:
        return None

    if len(incoming_edges) > 1:
        raise GraphRunError('Only one predecessor edge is supported in this phase.')

    predecessor_id = incoming_edges[0].get('source')
    if not isinstance(predecessor_id, str):
        raise GraphRunError(f'Node {node_id} has an invalid predecessor reference.')

    predecessor_output = get_node_output(document.id, predecessor_id)
    if predecessor_output is None:
        raise GraphRunError(
            f'Node {node_id} requires cached output from predecessor {predecessor_id}.',
        )

    return predecessor_output


def _run_single_node(
    node_kind: Any,
    raw_config: dict[str, Any],
    context: NodeExecutionContext,
):
    try:
        if node_kind == 'agent':
            return run_agent_with_context(AgentNodeConfig.model_validate(raw_config), context)

        if node_kind == 'microservice':
            return run_microservice_with_context(
                MicroserviceNodeConfig.model_validate(raw_config),
                context,
            )
    except ValidationError as error:
        raise GraphRunError('Node configuration is invalid for execution.') from error

    raise GraphRunError(f'Unsupported node kind "{node_kind}" in flow execution.')