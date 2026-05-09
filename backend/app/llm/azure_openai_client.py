from sqlalchemy.orm import Session

from .base import LLMResponse, _get_optional_setting, _get_secret


def call_azure_openai(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """Azure OpenAI uses the OpenAI SDK's AzureOpenAI client.

    Required settings (Settings panel):
      - azure_openai_api_key
      - azure_openai__endpoint    (https://<resource>.openai.azure.com/)
      - azure_openai__api_version (e.g. 2024-08-01-preview)
      - azure_openai__deployment  (the deployment name; takes priority over `model`)
    """
    from openai import AzureOpenAI

    api_key = _get_secret(db, "azure_openai_api_key")
    endpoint = _get_optional_setting(db, "azure_openai__endpoint")
    api_version = _get_optional_setting(db, "azure_openai__api_version")
    deployment = _get_optional_setting(db, "azure_openai__deployment") or model

    if not endpoint:
        raise RuntimeError(
            "Azure OpenAI requires 'azure_openai__endpoint' in Settings."
        )
    if not api_version:
        raise RuntimeError(
            "Azure OpenAI requires 'azure_openai__api_version' in Settings."
        )
    if not deployment:
        raise RuntimeError(
            "Azure OpenAI requires either a deployment in Settings or a model name on the node."
        )

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
    )

    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    kwargs: dict = {"model": deployment, "messages": messages}

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
        # Older api-versions may not support strict json_schema
        if output_schema and "response_format" in str(e).lower():
            kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
        else:
            raise

    text = resp.choices[0].message.content or ""
    return LLMResponse(text=text, provider="azure_openai", model=deployment)
