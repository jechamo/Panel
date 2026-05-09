import shutil
import subprocess
import json

from sqlalchemy.orm import Session

from .base import LLMResponse, _get_optional_setting

_DEFAULT_TIMEOUT_SECONDS = 120


def _shape_hint(output_schema: dict | None) -> str | None:
    if not output_schema:
        return None
    props = output_schema.get("properties") or {}
    if not isinstance(props, dict) or not props:
        return None
    shape: dict[str, str] = {}
    for name, spec in props.items():
        field_type = (spec or {}).get("type") or "string"
        shape[name] = field_type
    return json.dumps(shape, ensure_ascii=False, separators=(",", ":"))


def call_copilot_cli(
    db: Session,
    model: str,
    system: str,
    user: str,
    json_mode: bool,
    output_schema: dict | None = None,
) -> LLMResponse:
    """Run the real GitHub Copilot CLI locally with an explicit model.

    This uses `gh copilot -- ...`, which routes through the installed Copilot CLI,
    not the GitHub Models inference endpoint. That allows access to Copilot-only
    model names such as `gpt-5.4` and `claude-sonnet-4.6` when available.
    """
    gh_path = shutil.which("gh")
    if gh_path is None:
        raise RuntimeError("GitHub CLI (`gh`) is not installed or not on PATH.")

    timeout_str = _get_optional_setting(db, "copilot_cli__timeout_seconds")
    try:
        timeout = int(timeout_str) if timeout_str else _DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        timeout = _DEFAULT_TIMEOUT_SECONDS

    prompt_sections: list[str] = [user.strip()]
    if system.strip():
        prompt_sections.append(f"Additional requirements: {system.strip()}")
    shape_hint = _shape_hint(output_schema)
    if shape_hint:
        prompt_sections.append(
            f"Return only a valid JSON object with exactly this shape: {shape_hint}."
        )
    elif json_mode:
        prompt_sections.append("Return only valid JSON.")
    full_prompt = "/ask " + " ".join(section for section in prompt_sections if section).strip()

    command = [gh_path, "copilot", "--", "--model", model, "-p", full_prompt, "-s"]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Copilot CLI timed out after {timeout}s. Adjust 'copilot_cli__timeout_seconds'."
        ) from e
    except OSError as e:
        raise RuntimeError(f"Could not run Copilot CLI: {e}") from e

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or "no output"
        raise RuntimeError(f"Copilot CLI exited {result.returncode}: {detail[:500]}")

    text = (result.stdout or "").strip()
    if not text:
        raise RuntimeError("Copilot CLI returned an empty response.")

    return LLMResponse(text=text, provider="copilot_cli", model=model)