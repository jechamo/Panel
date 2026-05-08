import json
from typing import Any

from google import genai
from google.genai import types

from app.core.settings import get_settings


def get_gemini_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError('GEMINI_API_KEY is required to run agent nodes with Gemini models.')

    return genai.Client(api_key=settings.gemini_api_key)


def run_gemini_structured_output(
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_schema: dict[str, Any],
) -> dict[str, Any]:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            response_mime_type='application/json',
            response_schema=input_schema,
        ),
    )

    if not getattr(response, 'text', None):
        raise ValueError('Gemini response did not include structured JSON output.')

    return json.loads(response.text)