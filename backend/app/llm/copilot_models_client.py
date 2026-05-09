import shutil
import subprocess

from sqlalchemy.orm import Session

from .base import LLMResponse

_GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"
_GH_AUTH_TIMEOUT_SECONDS = 5


def _resolve_github_token() -> str:
    """Get a GitHub token from the locally-installed gh CLI.

    Returns the token printed by `gh auth token`. Raises a clear error if
    `gh` isn't installed or the user isn't logged in.
    """
    if shutil.which("gh") is None:
        raise RuntimeError(
            "GitHub CLI (`gh`) is not installed or not on PATH. Install it or "
            "use the 'GitHub Models (PAT)' provider instead and paste a token."
        )
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=_GH_AUTH_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"`gh auth token` timed out after {_GH_AUTH_TIMEOUT_SECONDS}s") from e
    except OSError as e:
        raise RuntimeError(f"Could not run `gh auth token`: {e}") from e

    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "no stderr"
        raise RuntimeError(
            f"`gh auth token` failed (exit {result.returncode}): {stderr}. "
            "Run `gh auth login` and try again."
        )
    token = (result.stdout or "").strip()
    if not token:
        raise RuntimeError("`gh auth token` returned an empty token.")
    return token


def call_copilot_models(
    db: Session,  # noqa: ARG001 - kept for signature parity
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """Use the gh CLI's existing login to call GitHub Models.

    No API key to paste in Settings — the bank's already-authorized gh CLI
    provides the token. Same OpenAI-compatible API as `github_models`.
    """
    from openai import OpenAI

    token = _resolve_github_token()
    client = OpenAI(base_url=_GITHUB_MODELS_BASE_URL, api_key=token)

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
        if output_schema and "response_format" in str(e).lower():
            kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
        else:
            raise

    text = resp.choices[0].message.content or ""
    return LLMResponse(text=text, provider="copilot_models", model=model)
