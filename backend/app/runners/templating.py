import re
from typing import Any

# Matches {{ node_id }} or {{ node_id.path.with.any.depth }}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*)\s*\}\}")


def _stringify(value: Any) -> str:
    import json

    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))


def _walk(value: Any, segments: list[str]) -> Any:
    for seg in segments:
        if isinstance(value, dict):
            if seg in value:
                value = value[seg]
                continue
            return None
        if isinstance(value, list):
            try:
                idx = int(seg)
            except ValueError:
                return None
            if 0 <= idx < len(value):
                value = value[idx]
                continue
            return None
        return None
    return value


def render(template: str, context: dict[str, Any]) -> str:
    """Replace {{node_id[.path...]}} with values from context.

    `context` is a dict keyed by upstream node id, value being that node's
    output. Missing keys render as empty string. Nested paths are walked
    against dicts and integer-indexed against lists.
    """
    if not template:
        return ""

    def repl(match: re.Match[str]) -> str:
        path = match.group(1)
        segments = path.split(".")
        head, rest = segments[0], segments[1:]
        if head not in context:
            return ""
        value = context[head]
        if rest:
            value = _walk(value, rest)
        return _stringify(value)

    return PLACEHOLDER_RE.sub(repl, template)
