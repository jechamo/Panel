from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/introspect", tags=["introspect"])


class VariablesRequest(BaseModel):
    """Frontend posts the in-memory graph and the target node id."""

    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    last_outputs: dict[str, Any] = {}
    node_id: str


class Variable(BaseModel):
    path: str  # e.g. "agent-1.address.city"
    placeholder: str  # e.g. "{{agent-1.address.city}}"
    source: str  # "cached" | "schema" | "node"
    sample: str | None = None  # short preview when source == "cached"


class VariablesResponse(BaseModel):
    variables: list[Variable]


_MAX_DEPTH = 4
_MAX_PATHS_PER_NODE = 60


def _flatten(value: Any, prefix: str, depth: int = 0) -> list[tuple[str, Any]]:
    """Yield (path, leaf_value) pairs from a JSON-ish value."""
    if depth > _MAX_DEPTH:
        return [(prefix, value)]
    if isinstance(value, dict):
        out: list[tuple[str, Any]] = [(prefix, value)] if prefix else []
        for k, v in value.items():
            child_prefix = f"{prefix}.{k}" if prefix else k
            out.extend(_flatten(v, child_prefix, depth + 1))
        return out
    if isinstance(value, list):
        out = [(prefix, value)] if prefix else []
        for i, v in enumerate(value[:5]):
            child_prefix = f"{prefix}.{i}"
            out.extend(_flatten(v, child_prefix, depth + 1))
        return out
    return [(prefix, value)]


def _short(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return None  # don't preview structures, only leaves
    text = str(value)
    return text if len(text) <= 60 else text[:57] + "..."


def _ancestors(target: str, edges: list[dict]) -> list[str]:
    """Return all transitive predecessors of target (BFS)."""
    parents: dict[str, list[str]] = {}
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if isinstance(s, str) and isinstance(t, str):
            parents.setdefault(t, []).append(s)

    seen: set[str] = set()
    queue = list(parents.get(target, []))
    while queue:
        nid = queue.pop(0)
        if nid in seen:
            continue
        seen.add(nid)
        queue.extend(parents.get(nid, []))
    return list(seen)


@router.post("/variables", response_model=VariablesResponse)
def variables(payload: VariablesRequest) -> VariablesResponse:
    by_id: dict[str, dict] = {n["id"]: n for n in payload.nodes if "id" in n}
    if payload.node_id not in by_id:
        return VariablesResponse(variables=[])

    ancestor_ids = _ancestors(payload.node_id, payload.edges)
    out: list[Variable] = []

    for aid in ancestor_ids:
        node = by_id.get(aid)
        if node is None:
            continue
        cached = payload.last_outputs.get(aid)
        added_paths: set[str] = set()

        if cached is not None:
            for path, leaf in _flatten(cached, aid)[:_MAX_PATHS_PER_NODE]:
                if path in added_paths:
                    continue
                added_paths.add(path)
                out.append(
                    Variable(
                        path=path,
                        placeholder="{{" + path + "}}",
                        source="cached",
                        sample=_short(leaf),
                    )
                )

        if node.get("type") == "agent":
            cfg = (node.get("data") or {}).get("config") or {}
            for f in cfg.get("output_fields") or []:
                name = (f.get("name") or "").strip()
                if not name:
                    continue
                path = f"{aid}.{name}"
                if path in added_paths:
                    continue
                added_paths.add(path)
                out.append(
                    Variable(
                        path=path,
                        placeholder="{{" + path + "}}",
                        source="schema",
                        sample=(f.get("description") or "").strip() or None,
                    )
                )

        if aid not in added_paths:
            out.append(
                Variable(path=aid, placeholder="{{" + aid + "}}", source="node")
            )

    return VariablesResponse(variables=out)
