from sqlalchemy.orm import Session

from .base import LLMResponse, _get_secret


def call_gemini(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_get_secret(db, "gemini_api_key"))

    config_kwargs: dict = {
        "system_instruction": system or None,
    }
    if output_schema:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = output_schema
    elif json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    config = types.GenerateContentConfig(**config_kwargs)

    try:
        resp = client.models.generate_content(
            model=model, contents=user, config=config
        )
    except Exception as e:  # noqa: BLE001
        # Older models may not accept response_schema → retry without it
        if output_schema and "schema" in str(e).lower():
            config = types.GenerateContentConfig(
                system_instruction=system or None,
                response_mime_type="application/json",
            )
            resp = client.models.generate_content(
                model=model, contents=user, config=config
            )
        else:
            raise

    return LLMResponse(text=resp.text or "", provider="gemini", model=model)
