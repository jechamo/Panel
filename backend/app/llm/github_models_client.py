from sqlalchemy.orm import Session

from .base import LLMResponse, _get_secret


def call_github_models(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """GitHub Models exposes an OpenAI-compatible API at the inference endpoint."""
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=_get_secret(db, "github_token"),
    )
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    kwargs = {"model": model, "messages": messages}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    return LLMResponse(text=text, provider="github_models", model=model)
