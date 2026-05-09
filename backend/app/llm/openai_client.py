from sqlalchemy.orm import Session

from .base import LLMResponse, _get_optional_setting, _get_secret


def call_openai(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    return _call_openai_compatible(
        db=db,
        provider="openai",
        secret_key="openai_api_key",
        base_url=_get_optional_setting(db, "openai__base_url"),  # may be None
        model=model,
        system=system,
        user=user,
        json_mode=json_mode,
        output_schema=output_schema,
    )


def _call_openai_compatible(
    *,
    db: Session,
    provider: str,
    secret_key: str,
    base_url: str | None,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None,
) -> LLMResponse:
    """Shared chat-completions path for OpenAI-compatible APIs.

    Used by openai, github_models, copilot_models, openai_compat, and the
    Azure client falls into a sibling function with the AzureOpenAI client.
    """
    from openai import OpenAI

    kwargs_client: dict = {"api_key": _get_secret(db, secret_key)}
    if base_url:
        kwargs_client["base_url"] = base_url
    client = OpenAI(**kwargs_client)

    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    kwargs: dict = {"model": model, "messages": messages}

    if output_schema:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "submit_structured_output",
                "schema": output_schema,
                "strict": True,
            },
        }
    elif json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = client.chat.completions.create(**kwargs)
    except Exception as e:  # noqa: BLE001
        # Fallback: model rejected json_schema → retry with json_object
        if output_schema and "response_format" in str(e).lower():
            kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
        else:
            raise

    text = resp.choices[0].message.content or ""
    return LLMResponse(text=text, provider=provider, model=model)
