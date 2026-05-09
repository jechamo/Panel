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
    config = types.GenerateContentConfig(
        system_instruction=system or None,
        response_mime_type="application/json" if json_mode else None,
    )
    resp = client.models.generate_content(
        model=model, contents=user, config=config
    )
    return LLMResponse(text=resp.text or "", provider="gemini", model=model)
