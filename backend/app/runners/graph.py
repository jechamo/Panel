import time
from collections import defaultdict, deque
from typing import Any

from sqlalchemy.orm import Session

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


def run_graph(
    db: Session,
    graph: dict[str, Any],
    only_node: str | None = None,
) -> list[NodeOutput]:
    nodes: list[dict] = graph.get("nodes", []) or []
    edges: list[dict] = graph.get("edges", []) or []
    cached: dict[str, Any] = dict(graph.get("last_outputs", {}) or {})
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

        t0 = time.perf_counter()
        try:
            output = _execute_node(db, node, ctx)
            cached[nid] = output
            results.append(
                NodeOutput(
                    node_id=nid,
                    status="ok",
                    output=output,
                    duration_ms=int((time.perf_counter() - t0) * 1000),
                )
            )
        except Exception as e:  # noqa: BLE001
            results.append(
                NodeOutput(
                    node_id=nid,
                    status="error",
                    error=str(e),
                    duration_ms=int((time.perf_counter() - t0) * 1000),
                )
            )
            if not only_node:
                # downstream nodes will see this parent missing → marked "skipped"
                continue
    return results
