from sqlalchemy.orm import Session

from .base import LLMResponse, _get_secret


def call_anthropic(
    db: Session, model: str, system: str, user: str, json_mode: bool
) -> LLMResponse:
    from anthropic import Anthropic

    client = Anthropic(api_key=_get_secret(db, "anthropic_api_key"))
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
    text = "".join(block.text for block in msg.content if block.type == "text")
    return LLMResponse(text=text, provider="anthropic", model=model)
