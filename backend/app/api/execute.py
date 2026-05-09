from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..runners.graph import run_graph
from ..schemas import RunRequest, RunResponse

router = APIRouter(prefix="/api/run", tags=["execute"])


@router.post("", response_model=RunResponse)
def run(payload: RunRequest, db: Session = Depends(get_db)):
    results = run_graph(db, payload.graph, only_node=payload.node_id)
    return RunResponse(results=results)
