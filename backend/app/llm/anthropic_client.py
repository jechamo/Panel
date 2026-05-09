import json

from sqlalchemy.orm import Session

from .base import LLMResponse, _get_secret

_TOOL_NAME = "submit_structured_output"


def call_anthropic(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """Anthropic agent call.

    With output_schema → tool_use mode (forced tool, JSON guaranteed).
    Without → plain text. With json_mode but no schema → adds prompt hint.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=_get_secret(db, "anthropic_api_key"))

    if output_schema:
        msg = client.messages.create(
            model=model,
            max_tokens=4096,
            system=(system or None),
            messages=[{"role": "user", "content": user}],
            tools=[
                {
                    "name": _TOOL_NAME,
                    "description": "Return the final structured output for the workflow node.",
                    "input_schema": output_schema,
                }
            ],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
        )
        for block in msg.content:
            if block.type == "tool_use" and block.name == _TOOL_NAME:
                return LLMResponse(
                    text=json.dumps(block.input, ensure_ascii=False),
                    provider="anthropic",
                    model=model,
                )
        # Model ignored the forced tool — fall through to text extraction
        text = "".join(b.text for b in msg.content if b.type == "text")
        return LLMResponse(text=text, provider="anthropic", model=model)

    sys_prompt = system or ""
    if json_mode:
        sys_prompt = (
            sys_prompt
            + "\n\nRespond with a single JSON object only. No prose, no markdown fences."
        ).strip()

    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        system=sys_prompt or None,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return LLMResponse(text=text, provider="anthropic", model=model)
