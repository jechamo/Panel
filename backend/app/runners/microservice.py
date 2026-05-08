from typing import Any

import httpx

from .templating import render


def run_microservice(config: dict[str, Any], context: dict[str, Any]) -> Any:
    method = (config.get("method") or "GET").upper()
    url = render(config.get("url", ""), context)
    if not url:
        raise ValueError("Microservice node has no URL configured")

    headers_raw = config.get("headers") or []  # list of {key, value}
    headers = {
        render(h.get("key", ""), context): render(h.get("value", ""), context)
        for h in headers_raw
        if h.get("key")
    }

    body_raw = config.get("body", "")
    body_text = render(body_raw, context) if body_raw else ""

    timeout = float(config.get("timeout_seconds", 30))

    with httpx.Client(timeout=timeout) as client:
        if method in ("GET", "DELETE", "HEAD"):
            r = client.request(method, url, headers=headers)
        else:
            content_type = headers.get("Content-Type", "application/json").lower()
            if "json" in content_type and body_text:
                import json

                try:
                    payload = json.loads(body_text)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Body is not valid JSON: {e}") from e
                r = client.request(method, url, headers=headers, json=payload)
            else:
                r = client.request(method, url, headers=headers, content=body_text)

    try:
        return r.json()
    except ValueError:
        return {"status_code": r.status_code, "text": r.text}
