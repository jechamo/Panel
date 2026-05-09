import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import NodeRun

router = APIRouter(prefix="/api/runs", tags=["runs"])


class NodeRunView(BaseModel):
    id: int
    flow_id: int | None
    node_id: str
    node_kind: str
    status: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    input: object | None = None
    output: object | None = None
    error: str | None

    @classmethod
    def from_orm_safe(cls, row: NodeRun) -> "NodeRunView":
        def _try(text: str) -> object | None:
            if not text:
                return None
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text

        return cls(
            id=row.id,
            flow_id=row.flow_id,
            node_id=row.node_id,
            node_kind=row.node_kind,
            status=row.status,
            started_at=row.started_at,
            finished_at=row.finished_at,
            duration_ms=row.duration_ms,
            input=_try(row.input_json),
            output=_try(row.output_json),
            error=row.error,
        )


@router.get("", response_model=list[NodeRunView])
def list_runs(
    node_id: str | None = Query(default=None),
    flow_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(NodeRun)
    if node_id is not None:
        query = query.filter(NodeRun.node_id == node_id)
    if flow_id is not None:
        query = query.filter(NodeRun.flow_id == flow_id)
    rows = query.order_by(desc(NodeRun.started_at)).limit(limit).all()
    return [NodeRunView.from_orm_safe(r) for r in rows]


@router.delete("")
def prune_runs(
    older_than_days: int | None = Query(default=None, ge=0),
    node_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Maintenance endpoint. Either delete by node_id, or by age (or both)."""
    query = db.query(NodeRun)
    if node_id is not None:
        query = query.filter(NodeRun.node_id == node_id)
    if older_than_days is not None:
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        query = query.filter(NodeRun.started_at < cutoff)
    deleted = query.delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}
