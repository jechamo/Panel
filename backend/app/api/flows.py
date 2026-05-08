from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.flow_storage import create_flow, delete_flow, get_flow, list_flows, update_flow
from app.core.responses import error_response, success_response
from app.executors.graph_runner import GraphRunError, run_flow_graph
from app.models.flow import FlowCreateRequest, FlowUpdateRequest

router = APIRouter(prefix='/flows', tags=['flows'])


@router.get('')
def read_flows() -> dict:
    return success_response([flow.model_dump(mode='json') for flow in list_flows()])


@router.post('', status_code=status.HTTP_201_CREATED)
def create_flow_endpoint(payload: FlowCreateRequest) -> dict:
    document = create_flow(payload)
    return success_response(document.model_dump(mode='json'))


@router.get('/{flow_id}')
def read_flow(flow_id: str):
    document = get_flow(flow_id)
    if document is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response('flow_not_found', f'Flow {flow_id} was not found.'),
        )

    return success_response(document.model_dump(mode='json'))


@router.post('/{flow_id}/run')
def run_flow_endpoint(flow_id: str):
    try:
        document = run_flow_graph(flow_id)
    except GraphRunError as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('flow_run_error', str(error)),
        )

    return success_response(document.model_dump(mode='json'))


@router.put('/{flow_id}')
def update_flow_endpoint(flow_id: str, payload: FlowUpdateRequest):
    if payload.id != flow_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('flow_id_mismatch', 'Flow id in path and payload must match.'),
        )

    document = update_flow(flow_id, payload)
    if document is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response('flow_not_found', f'Flow {flow_id} was not found.'),
        )

    return success_response(document.model_dump(mode='json'))


@router.delete('/{flow_id}')
def delete_flow_endpoint(flow_id: str):
    deleted = delete_flow(flow_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response('flow_not_found', f'Flow {flow_id} was not found.'),
        )

    return success_response({'deleted': True, 'id': flow_id})