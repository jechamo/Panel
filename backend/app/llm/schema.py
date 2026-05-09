from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model


def build_output_schema(
    output_fields: list[dict[str, str]],
) -> tuple[type[BaseModel], dict[str, Any]]:
    """Translate the user-defined output_fields into:
    - a Pydantic model for post-response validation
    - a JSON Schema (OpenAI/Azure/Gemini-compatible, strict-friendly)

    Each field becomes a required string. Names with dashes/spaces are
    escaped via Pydantic alias so the wire JSON keeps the user's name.
    """
    if not output_fields:
        raise ValueError("output_fields cannot be empty")

    field_definitions: dict[str, tuple[Any, Any]] = {}
    properties: dict[str, dict[str, str]] = {}
    required: list[str] = []

    seen: set[str] = set()
    for index, item in enumerate(output_fields):
        name = (item.get("name") or "").strip()
        description = (item.get("description") or "").strip()
        if not name:
            raise ValueError(f"output_fields[{index}].name is empty")
        if name in seen:
            raise ValueError(f"output_fields contains duplicate name: {name!r}")
        seen.add(name)

        internal = f"f_{index}"
        field_definitions[internal] = (
            str,
            Field(..., alias=name, description=description or name),
        )
        properties[name] = {
            "type": "string",
            "description": description or name,
        }
        required.append(name)

    model = create_model(
        "AgentStructuredOutput",
        __config__=ConfigDict(extra="forbid", populate_by_name=False),
        **field_definitions,
    )

    json_schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }

    return model, json_schema
