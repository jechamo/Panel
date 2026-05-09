from sqlalchemy.orm import Session

from .base import LLMResponse, _get_secret


def call_openai(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    from openai import OpenAI

    client = OpenAI(api_key=_get_secret(db, "openai_api_key"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    kwargs = {"model": model, "messages": messages}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    return LLMResponse(text=text, provider="openai", model=model)
