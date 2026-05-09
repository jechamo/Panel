import json
import shlex
import subprocess

from sqlalchemy.orm import Session

from .base import LLMResponse, _get_optional_setting

_DEFAULT_TIMEOUT_SECONDS = 120


def call_cli_subprocess(
    db: Session,
    model: str,  # noqa: ARG001 - command_template can use it
    system: str,
    user: str,
    json_mode: bool,  # noqa: ARG001
    output_schema: dict | None = None,  # noqa: ARG001 - validation happens upstream
) -> LLMResponse:
    """Run an arbitrary local CLI to get the LLM response.

    Settings (Settings panel):
      - cli_subprocess__command_template: e.g. "claude -p --output-format json"
        The full prompt (system + user joined) is passed on stdin.
      - cli_subprocess__timeout_seconds: defaults to 120.
      - cli_subprocess__output_path: optional jq-like path to extract from a
        JSON stdout (e.g. "result"). If empty, stdout is returned verbatim.

    Useful for environments that approve a specific LLM CLI (Claude Code,
    a corporate-bundled inference CLI, etc.) but no API keys.
    """
    command_template = _get_optional_setting(db, "cli_subprocess__command_template")
    if not command_template:
        raise RuntimeError(
            "cli_subprocess provider requires 'cli_subprocess__command_template' in Settings."
        )
    timeout_str = _get_optional_setting(db, "cli_subprocess__timeout_seconds")
    try:
        timeout = int(timeout_str) if timeout_str else _DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        timeout = _DEFAULT_TIMEOUT_SECONDS

    output_path = _get_optional_setting(db, "cli_subprocess__output_path")

    args = shlex.split(command_template)
    if not args:
        raise RuntimeError("cli_subprocess command_template is empty after parsing.")

    full_prompt = (system + "\n\n" + user).strip() if system else user

    try:
        result = subprocess.run(
            args,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"CLI subprocess timed out after {timeout}s. Adjust 'cli_subprocess__timeout_seconds'."
        ) from e
    except OSError as e:
        raise RuntimeError(f"Could not run CLI subprocess: {e}") from e

    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "no stderr"
        raise RuntimeError(
            f"CLI subprocess exited {result.returncode}: {stderr[:500]}"
        )

    text = (result.stdout or "").strip()
    if output_path:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Configured output_path={output_path!r} but stdout is not JSON: {e}"
            ) from e
        for segment in output_path.split("."):
            if not isinstance(data, dict) or segment not in data:
                raise RuntimeError(
                    f"output_path {output_path!r} did not match the CLI response shape."
                )
            data = data[segment]
        text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)

    return LLMResponse(text=text, provider="cli_subprocess", model="cli")
