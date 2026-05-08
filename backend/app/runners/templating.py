import re
from typing import Any

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\-]+)(?:\.([a-zA-Z0-9_\-]+))?\s*\}\}")


def _stringify(value: Any) -> str:
    import json

    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, default=str)


def render(template: str, context: dict[str, Any]) -> str:
    """Replace {{node_id}} or {{node_id.field}} with values from context.

    `context` is a dict keyed by upstream node id, value being that node's output.
    Missing keys render as an empty string.
    """
    if not template:
        return ""

    def repl(match: re.Match[str]) -> str:
        node_id, field = match.group(1), match.group(2)
        value = context.get(node_id)
        if field:
            if isinstance(value, dict):
                value = value.get(field)
            else:
                value = None
        return _stringify(value)

    return PLACEHOLDER_RE.sub(repl, template)
