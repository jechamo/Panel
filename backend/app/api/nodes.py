import httpx
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.responses import error_response, success_response
from app.executors.microservice_executor import (
    MicroserviceExecutionError,
    run_microservice,
)
from app.models.node import NodeRunRequest

router = APIRouter(prefix='/nodes', tags=['nodes'])


@router.post('/{node_id}/run')
def run_node(node_id: str, payload: NodeRunRequest):
    if payload.kind != 'microservice':
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(
                'invalid_node_kind',
                'Only microservice nodes can be run in this phase.',
            ),
        )

    try:
        result = run_microservice(payload.config)
    except MicroserviceExecutionError as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response('microservice_execution_error', str(error)),
        )
    except httpx.HTTPStatusError as error:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=error_response(
                'microservice_http_error',
                f'Microservice returned status {error.response.status_code}.',
            ),
        )
    except httpx.HTTPError as error:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=error_response('microservice_network_error', str(error)),
        )

    return success_response(result.model_dump(mode='json'))