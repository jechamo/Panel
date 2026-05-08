from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.flow_storage import get_node_output, get_predecessor_node_id, set_node_runtime_state
from app.core.responses import error_response, success_response
from app.core.run_storage import create_node_run_log
from app.executors.agent_executor import AgentExecutionError, run_agent_with_context
from app.executors.microservice_executor import (
    MicroserviceExecutionError,
    run_microservice_with_context,
)
from app.models.node import NodeRunRequest
from app.models.run import NodeRunLog

router = APIRouter(prefix='/nodes', tags=['nodes'])


class NodeExecutionContextError(Exception):
    pass


@router.post('/{node_id}/run')
def run_node(node_id: str, payload: NodeRunRequest):
    started_at = datetime.now(timezone.utc)

    try:
        resolved_context = _resolve_execution_context(node_id, payload.context)
    except NodeExecutionContextError as error:
        _write_run_log(
            flow_id=payload.context.flowId,
            node_id=node_id,
            node_kind=payload.kind,
            status='error',
            started_at=started_at,
            input_data=payload.context.input,
            output=None,
            error_message=str(error),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('node_context_error', str(error)),
        )

    if payload.kind == 'agent':
        try:
            result = run_agent_with_context(payload.config, resolved_context)
        except AgentExecutionError as error:
            _persist_runtime_error(node_id, resolved_context.flowId, str(error))
            _write_run_log(
                flow_id=resolved_context.flowId,
                node_id=node_id,
                node_kind='agent',
                status='error',
                started_at=started_at,
                input_data=resolved_context.input,
                output=None,
                error_message=str(error),
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response('agent_execution_error', str(error)),
            )
        except httpx.HTTPError as error:
            _persist_runtime_error(node_id, resolved_context.flowId, str(error))
            _write_run_log(
                flow_id=resolved_context.flowId,
                node_id=node_id,
                node_kind='agent',
                status='error',
                started_at=started_at,
                input_data=resolved_context.input,
                output=None,
                error_message=str(error),
            )
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content=error_response('agent_network_error', str(error)),
            )

        _persist_runtime_success(node_id, resolved_context.flowId, result.output)
        _write_run_log(
            flow_id=resolved_context.flowId,
            node_id=node_id,
            node_kind='agent',
            status='success',
            started_at=started_at,
            input_data=resolved_context.input,
            output=result.output,
            error_message=None,
        )

        return success_response(result.model_dump(mode='json'))

    if payload.kind != 'microservice':
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(
                'invalid_node_kind',
                'Only microservice and agent nodes can be run in this phase.',
            ),
        )

    try:
        result = run_microservice_with_context(payload.config, resolved_context)
    except MicroserviceExecutionError as error:
        _persist_runtime_error(node_id, resolved_context.flowId, str(error))
        _write_run_log(
            flow_id=resolved_context.flowId,
            node_id=node_id,
            node_kind='microservice',
            status='error',
            started_at=started_at,
            input_data=resolved_context.input,
            output=None,
            error_message=str(error),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('microservice_execution_error', str(error)),
        )
    except httpx.HTTPStatusError as error:
        _persist_runtime_error(node_id, resolved_context.flowId, str(error))
        error_message = f'Microservice returned status {error.response.status_code}.'
        _write_run_log(
            flow_id=resolved_context.flowId,
            node_id=node_id,
            node_kind='microservice',
            status='error',
            started_at=started_at,
            input_data=resolved_context.input,
            output=None,
            error_message=error_message,
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=error_response(
                'microservice_http_error',
                error_message,
            ),
        )
    except httpx.HTTPError as error:
        _persist_runtime_error(node_id, resolved_context.flowId, str(error))
        _write_run_log(
            flow_id=resolved_context.flowId,
            node_id=node_id,
            node_kind='microservice',
            status='error',
            started_at=started_at,
            input_data=resolved_context.input,
            output=None,
            error_message=str(error),
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=error_response('microservice_network_error', str(error)),
        )

    _persist_runtime_success(node_id, resolved_context.flowId, result.output)
    _write_run_log(
        flow_id=resolved_context.flowId,
        node_id=node_id,
        node_kind='microservice',
        status='success',
        started_at=started_at,
        input_data=resolved_context.input,
        output=result.output,
        error_message=None,
    )

    return success_response(result.model_dump(mode='json'))


def _resolve_execution_context(node_id: str, context):
    if not context.flowId:
        return context

    if context.input is not None:
        return context

    try:
        predecessor_id = get_predecessor_node_id(context.flowId, node_id)
    except ValueError as error:
        raise NodeExecutionContextError(str(error)) from error

    if predecessor_id is None:
        return context

    predecessor_output = get_node_output(context.flowId, predecessor_id)
    if predecessor_output is None:
        raise NodeExecutionContextError(
            f'Node {node_id} requires cached output from predecessor {predecessor_id}.',
        )

    return context.model_copy(update={'input': predecessor_output})


def _persist_runtime_success(node_id: str, flow_id: str | None, output) -> None:
    if not flow_id:
        return

    set_node_runtime_state(
        flow_id,
        node_id,
        status='success',
        output=output,
        last_error=None,
    )


def _persist_runtime_error(node_id: str, flow_id: str | None, error_message: str) -> None:
    if not flow_id:
        return

    set_node_runtime_state(
        flow_id,
        node_id,
        status='error',
        output=None,
        last_error=error_message,
    )


def _write_run_log(
    *,
    flow_id: str | None,
    node_id: str,
    node_kind: str,
    status: str,
    started_at: datetime,
    input_data,
    output,
    error_message: str | None,
) -> None:
    create_node_run_log(
        NodeRunLog(
            id='',
            flowId=flow_id,
            nodeId=node_id,
            nodeKind=node_kind,
            status=status,
            startedAt=started_at,
            finishedAt=datetime.now(timezone.utc),
            input=input_data,
            output=output,
            error=error_message,
        )
    )