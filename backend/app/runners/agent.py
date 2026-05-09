import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..db import UPLOADS_DIR
from ..llm import call_llm
from ..llm.schema import build_output_schema
from ..parsers import extract_text
from .templating import render


def _read_attachments(attachments: list[dict[str, Any]]) -> str:
    """`attachments` items are { name, path } where path is relative to UPLOADS_DIR."""
    if not attachments:
        return ""
    chunks = []
    for att in attachments:
        rel = att.get("path", "")
        if not rel:
            continue
        full = (UPLOADS_DIR / rel).resolve()
        try:
            full.relative_to(UPLOADS_DIR.resolve())
        except ValueError:
            continue  # path traversal guard
        if not full.exists():
            continue
        try:
            text = extract_text(full)
        except Exception as e:  # noqa: BLE001
            text = f"[failed to parse {att.get('name', rel)}: {e}]"
        chunks.append(f"=== Attachment: {att.get('name', rel)} ===\n{text}")
    return "\n\n".join(chunks)


def _parse_json_loose(text: str) -> Any:
    """Best-effort JSON extraction: try direct, then strip code fences."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl != -1:
            stripped = text[first_nl + 1 :]
            if stripped.endswith("```"):
                stripped = stripped[:-3]
            try:
                return json.loads(stripped.strip())
            except json.JSONDecodeError:
                pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def _schema_hint_for_prompt(schema: dict[str, Any]) -> str:
    """Render a human-readable description of the JSON schema for prompt-only providers."""
    props = schema.get("properties", {}) or {}
    if not props:
        return ""
    lines = ["Return a JSON object with exactly these fields:"]
    for name, spec in props.items():
        desc = spec.get("description", "")
        lines.append(f'  - "{name}" (string): {desc or "(no description)"}')
    return "\n".join(lines)


def run_agent(db: Session, config: dict[str, Any], context: dict[str, Any]) -> Any:
    provider = config.get("provider", "anthropic")
    model = config.get("model") or ""
    system = render(config.get("system_prompt", ""), context)
    user = render(config.get("user_prompt", ""), context)
    fields: list[dict[str, str]] = config.get("output_fields", []) or []
    attachments = config.get("attachments", []) or []

    attachment_text = _read_attachments(attachments)
    if attachment_text:
        user = f"{user}\n\n=== Attachments ===\n{attachment_text}"

    if not fields:
        # Free-text mode: no schema, no validation.
        response = call_llm(
            db=db,
            provider=provider,
            model=model,
            system=system,
            user=user,
            json_mode=False,
            output_schema=None,
        )
        return {"text": response.text}

    # Structured mode: build schema, ask provider for native structured output,
    # validate the result.
    try:
        validation_model, json_schema = build_output_schema(fields)
    except ValueError as e:
        return {"_error": f"Invalid output_fields configuration: {e}"}

    # Always include the prompt-style hint in the system prompt as a safety net
    # for providers that fall back to plain JSON mode.
    hint = _schema_hint_for_prompt(json_schema)
    system_with_hint = (system + ("\n\n" + hint if hint else "")).strip()

    response = call_llm(
        db=db,
        provider=provider,
        model=model,
        system=system_with_hint,
        user=user,
        json_mode=True,
        output_schema=json_schema,
    )

    parsed = _parse_json_loose(response.text)
    if parsed is None:
        return {
            "_raw": response.text,
            "_error": "Model did not return valid JSON",
        }
    try:
        validated = validation_model.model_validate(parsed)
    except ValidationError as e:
        return {
            "_raw": parsed,
            "_error": f"Output did not match the declared schema: {e.errors()[:3]}",
        }
    return validated.model_dump(by_alias=True)
