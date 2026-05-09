import json
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from ..models import NodeRun
from ..schemas import NodeOutput
from .agent import run_agent
from .microservice import run_microservice


def _topo_order(nodes: list[dict], edges: list[dict]) -> list[str]:
    ids = {n["id"] for n in nodes}
    indeg: dict[str, int] = defaultdict(int)
    out: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s in ids and t in ids:
            out[s].append(t)
            indeg[t] += 1

    queue = deque([n["id"] for n in nodes if indeg[n["id"]] == 0])
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in out[nid]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(nodes):
        # cycle: fall back to declared order so the user gets *some* feedback
        return [n["id"] for n in nodes]
    return order


def _parents_of(node_id: str, edges: list[dict]) -> list[str]:
    return [e["source"] for e in edges if e.get("target") == node_id]


def _execute_node(db: Session, node: dict, context: dict[str, Any]) -> Any:
    ntype = node.get("type")
    config = node.get("data", {}).get("config", {}) or {}
    if ntype == "agent":
        return run_agent(db, config, context)
    if ntype == "microservice":
        return run_microservice(config, context)
    raise ValueError(f"Unknown node type: {ntype}")


def _persist_run(
    db: Session,
    *,
    flow_id: int | None,
    node_id: str,
    node_kind: str,
    status: str,
    started_at: datetime,
    duration_ms: int,
    input_data: Any,
    output: Any,
    error: str | None,
) -> None:
    """Best-effort log write. Never raises so a logging failure cannot
    cancel the actual execution result."""
    try:
        run = NodeRun(
            flow_id=flow_id,
            node_id=node_id,
            node_kind=node_kind,
            status=status,
            started_at=started_at,
            finished_at=datetime.utcnow(),
            duration_ms=duration_ms,
            input_json=json.dumps(input_data, ensure_ascii=False, default=str)[:50_000],
            output_json=json.dumps(output, ensure_ascii=False, default=str)[:50_000]
            if output is not None
            else "",
            error=error[:5000] if error else None,
        )
        db.add(run)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()


def run_graph(
    db: Session,
    graph: dict[str, Any],
    only_node: str | None = None,
) -> list[NodeOutput]:
    nodes: list[dict] = graph.get("nodes", []) or []
    edges: list[dict] = graph.get("edges", []) or []
    cached: dict[str, Any] = dict(graph.get("last_outputs", {}) or {})
    flow_id_raw = graph.get("flow_id")
    flow_id = int(flow_id_raw) if isinstance(flow_id_raw, (int, str)) and str(flow_id_raw).isdigit() else None
    by_id = {n["id"]: n for n in nodes}

    if only_node:
        if only_node not in by_id:
            return [
                NodeOutput(
                    node_id=only_node, status="error", error="Node not found"
                )
            ]
        targets = [only_node]
    else:
        targets = _topo_order(nodes, edges)

    results: list[NodeOutput] = []
    for nid in targets:
        node = by_id[nid]
        parent_ids = _parents_of(nid, edges)
        ctx = {pid: cached.get(pid) for pid in parent_ids}

        if not only_node and any(p not in cached for p in parent_ids):
            results.append(
                NodeOutput(
                    node_id=nid,
                    status="skipped",
                    error="A parent did not produce an output",
                )
            )
            continue

        started_at = datetime.utcnow()
        t0 = time.perf_counter()
        try:
            output = _execute_node(db, node, ctx)
            cached[nid] = output
            duration_ms = int((time.perf_counter() - t0) * 1000)
            results.append(
                NodeOutput(
                    node_id=nid,
                    status="ok",
                    output=output,
                    duration_ms=duration_ms,
                )
            )
            _persist_run(
                db,
                flow_id=flow_id,
                node_id=nid,
                node_kind=node.get("type", "unknown"),
                status="ok",
                started_at=started_at,
                duration_ms=duration_ms,
                input_data=ctx,
                output=output,
                error=None,
            )
        except Exception as e:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - t0) * 1000)
            results.append(
                NodeOutput(
                    node_id=nid,
                    status="error",
                    error=str(e),
                    duration_ms=duration_ms,
                )
            )
            _persist_run(
                db,
                flow_id=flow_id,
                node_id=nid,
                node_kind=node.get("type", "unknown"),
                status="error",
                started_at=started_at,
                duration_ms=duration_ms,
                input_data=ctx,
                output=None,
                error=str(e),
            )
            if not only_node:
                # downstream nodes will see this parent missing → marked "skipped"
                continue
    return results
