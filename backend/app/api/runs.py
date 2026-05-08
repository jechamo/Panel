from fastapi import APIRouter, Query

from app.core.responses import success_response
from app.core.run_storage import list_node_run_logs

router = APIRouter(prefix='/runs', tags=['runs'])


@router.get('')
def read_runs(
    node_id: str = Query(..., alias='nodeId'),
    flow_id: str | None = Query(default=None, alias='flowId'),
    limit: int = Query(default=10, ge=1, le=50),
):
    runs = list_node_run_logs(flow_id=flow_id, node_id=node_id, limit=limit)
    return success_response([run.model_dump(mode='json') for run in runs])