import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Flow
from ..schemas import FlowCreate, FlowDetail, FlowSummary, FlowUpdate

router = APIRouter(prefix="/api/flows", tags=["flows"])


@router.get("", response_model=list[FlowSummary])
def list_flows(db: Session = Depends(get_db)):
    return db.query(Flow).order_by(Flow.updated_at.desc()).all()


@router.post("", response_model=FlowDetail)
def create_flow(payload: FlowCreate, db: Session = Depends(get_db)):
    if db.query(Flow).filter(Flow.name == payload.name).first():
        raise HTTPException(409, f"Flow named '{payload.name}' already exists")
    flow = Flow(name=payload.name, graph=json.dumps(payload.graph))
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return _to_detail(flow)


@router.get("/{flow_id}", response_model=FlowDetail)
def get_flow(flow_id: int, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(404, "Flow not found")
    return _to_detail(flow)


@router.put("/{flow_id}", response_model=FlowDetail)
def update_flow(flow_id: int, payload: FlowUpdate, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(404, "Flow not found")
    if payload.name is not None:
        flow.name = payload.name
    if payload.graph is not None:
        flow.graph = json.dumps(payload.graph)
    db.commit()
    db.refresh(flow)
    return _to_detail(flow)


@router.delete("/{flow_id}", status_code=204)
def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    flow = db.get(Flow, flow_id)
    if not flow:
        raise HTTPException(404, "Flow not found")
    db.delete(flow)
    db.commit()


def _to_detail(flow: Flow) -> FlowDetail:
    return FlowDetail(
        id=flow.id,
        name=flow.name,
        updated_at=flow.updated_at,
        graph=json.loads(flow.graph or "{}"),
    )
